#!/usr/bin/env python3
"""Tests for the modifierMap resolver and the geometry table.

    python3 scripts/test_keylayout.py

Plain unittest, no dependencies, so CI needs nothing but a Python.
"""

import collections
import itertools
import pathlib
import sys
import unittest

import keylayout
from keylayout import ROWS, KeyLayout, Pattern, check_geometry

ROOT = pathlib.Path(__file__).resolve().parent.parent
LAYOUT = next(iter(sorted((ROOT / "src").glob("*.keylayout"))))

# What each virtual keycode produces on a US ANSI keyboard, which is what the ⌘
# layer has to reproduce for shortcuts to land on the right physical key.
US_ANSI = {
    50: "`", 18: "1", 19: "2", 20: "3", 21: "4", 23: "5", 22: "6",
    26: "7", 28: "8", 25: "9", 29: "0", 27: "-", 24: "=",
    12: "q", 13: "w", 14: "e", 15: "r", 17: "t", 16: "y", 32: "u",
    34: "i", 31: "o", 35: "p", 33: "[", 30: "]", 42: "\\",
    0: "a", 1: "s", 2: "d", 3: "f", 5: "g", 4: "h", 38: "j",
    40: "k", 37: "l", 41: ";", 39: "'",
    6: "z", 7: "x", 8: "c", 9: "v", 11: "b", 45: "n", 46: "m",
    43: ",", 47: ".", 44: "/",
}


INVENTORY = pathlib.Path(__file__).with_name("option-layer-inventory.txt")


def option_layer_characters(layout):
    """Every printable character the ⌥ and ⇧⌥ layers can type, and how many keys
    carry each. Controls and the non-breaking space are function keys rather than
    anything a person types deliberately, so they are left out."""
    return collections.Counter(
        char
        for char in list(layout.plane("option").values())
        + list(layout.plane("shift+option").values())
        if char and char.isprintable() and char != "\xa0"
    )


def read_inventory():
    counts = {}
    for line in INVENTORY.read_text(encoding="utf-8").splitlines():
        # A data row is exactly three tab-separated fields. Comments are matched
        # by shape rather than by a leading '#', because '#' is one of the
        # characters the file records.
        fields = line.split("\t")
        if len(fields) == 3:
            counts[fields[0]] = int(fields[1])
    return counts


def write_inventory(layout):
    counts = option_layer_characters(layout)
    rows = "\n".join(
        f"{char}\t{n}\tU+{ord(char):04X}"
        for char, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    )
    INVENTORY.write_text(INVENTORY_HEADER + rows + "\n", encoding="utf-8")
    return counts


INVENTORY_HEADER = """\
# Every printable character the ⌥ and ⇧⌥ layers can type, and how many keys
# carry each. Rearranging those layers is free; this file is here so that
# *losing* something is not — a character overwritten by a move, or one of a
# pair of duplicates dropped while relocating the other, fails the tests instead
# of surfacing as "I can't type that any more" months later.
#
# Regenerate deliberately, and let the diff speak in review:
#
#     python3 scripts/test_keylayout.py --update-inventory
#
"""


class PatternTests(unittest.TestCase):
    def match(self, keys, *held):
        state = {bit: bit in held for bit in keylayout.MODIFIER_BITS}
        return Pattern(keys).matches(state)

    def test_empty_pattern_is_the_bare_keyboard(self):
        self.assertTrue(self.match(""))
        self.assertFalse(self.match("", "shift"))
        self.assertFalse(self.match("", "caps"))

    def test_bare_token_requires_the_modifier_down(self):
        self.assertTrue(self.match("caps", "caps"))
        self.assertFalse(self.match("caps"))

    def test_unmentioned_modifiers_must_be_up(self):
        self.assertTrue(self.match("caps", "caps"))
        self.assertFalse(self.match("caps", "caps", "command"))

    def test_question_mark_makes_a_modifier_optional(self):
        self.assertTrue(self.match("anyShift caps?", "shift"))
        self.assertTrue(self.match("anyShift caps?", "shift", "caps"))
        self.assertFalse(self.match("anyShift caps?", "caps"))

    def test_any_matches_either_side(self):
        self.assertTrue(self.match("anyOption", "option"))
        self.assertTrue(self.match("anyOption", "rightOption"))
        self.assertTrue(self.match("anyOption", "option", "rightOption"))
        self.assertFalse(self.match("anyOption"))

    def test_sided_token_requires_that_side_and_excludes_the_other(self):
        self.assertTrue(self.match("option", "option"))
        self.assertFalse(self.match("option", "rightOption"))
        self.assertFalse(self.match("option", "option", "rightOption"))

    def test_optional_any_leaves_both_sides_free(self):
        self.assertTrue(self.match("anyShift? command", "command"))
        self.assertTrue(self.match("anyShift? command", "command", "shift"))
        self.assertTrue(self.match("anyShift? command", "command", "rightShift"))

    def test_unknown_token_is_rejected(self):
        with self.assertRaises(ValueError):
            Pattern("fn")
        with self.assertRaises(ValueError):
            Pattern("anyCommand")


class ResolveTests(unittest.TestCase):
    """The three anchors from the roadmap, then the whole 256-state table."""

    @classmethod
    def setUpClass(cls):
        cls.layout = KeyLayout(str(LAYOUT))
        cls.modifiers = cls.layout.modifiers

    def test_named_planes_land_on_the_expected_maps(self):
        self.assertEqual(self.modifiers.resolve(), "5")
        self.assertEqual(self.modifiers.resolve("shift"), "1")
        self.assertEqual(self.modifiers.resolve("command"), "0")

    def test_right_hand_modifiers_agree_with_left(self):
        self.assertEqual(
            self.modifiers.resolve("shift"), self.modifiers.resolve("rightShift")
        )
        self.assertEqual(
            self.modifiers.resolve("option"), self.modifiers.resolve("rightOption")
        )

    def test_no_state_matches_two_selects(self):
        """If two keyMapSelects can claim one state, document order is deciding
        something, and this file would be relying on an ordering nobody chose."""
        for combo in self._states():
            state = dict(zip(keylayout.MODIFIER_BITS, combo))
            hits = [
                index
                for index, patterns in self.modifiers.selects
                if any(pattern.matches(state) for pattern in patterns)
            ]
            self.assertLessEqual(
                len(hits), 1, f"{sorted(k for k, v in state.items() if v)} -> {hits}"
            )

    def test_table_covers_every_state_but_one(self):
        """Exactly one of the 256 states is unmatched: every modifier at once,
        which falls through to defaultIndex. See ROADMAP 'Decided against'."""
        unmatched = []
        for combo in self._states():
            held = [bit for bit, on in zip(keylayout.MODIFIER_BITS, combo) if on]
            state = dict(zip(keylayout.MODIFIER_BITS, combo))
            if not any(
                pattern.matches(state)
                for _, patterns in self.modifiers.selects
                for pattern in patterns
            ):
                unmatched.append(held)
        self.assertEqual(unmatched, [list(keylayout.MODIFIER_BITS)])
        self.assertEqual(self.modifiers.resolve(*keylayout.MODIFIER_BITS), "5")

    def test_control_plane_is_the_widest(self):
        """Map 7 absorbs the control states; a shrunken count means the pattern
        semantics changed under us."""
        counts = {}
        for combo in self._states():
            held = [bit for bit, on in zip(keylayout.MODIFIER_BITS, combo) if on]
            index = self.modifiers.resolve(*held)
            counts[index] = counts.get(index, 0) + 1
        self.assertEqual(counts["7"], 181)
        self.assertEqual(sum(counts.values()), 256)

    @staticmethod
    def _states():
        return itertools.product([False, True], repeat=len(keylayout.MODIFIER_BITS))


class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout = KeyLayout(str(LAYOUT))

    def test_geometry_matches_the_layout(self):
        check_geometry(self.layout)

    def test_every_positioned_keycode_exists_in_every_plane(self):
        positioned = {what for row in ROWS for what, _ in row if isinstance(what, int)}
        for name in keylayout.PLANES:
            plane = self.layout.plane(name)
            missing = sorted(positioned - set(plane))
            self.assertEqual(missing, [], f"plane {name} is missing codes {missing}")

    def test_documented_changes_are_present(self):
        """The two mappings this fork exists for, asserted by codepoint so a
        lookalike character cannot pass."""
        base = self.layout.plane("base")
        shift = self.layout.plane("shift")
        caps = self.layout.plane("caps")
        self.assertEqual(base[50], "ʼ")
        self.assertEqual(caps[50], "ʼ")
        self.assertEqual(base[42], "/")
        self.assertEqual(shift[42], "\\")
        self.assertEqual(caps[42], "/")

    def test_alternative_apostrophes_are_where_the_docs_say(self):
        """README and docs/layers.md send people to these three keys when they
        need an apostrophe that is not U+02BC. Pin them; prose drifts."""
        self.assertEqual(self.layout.plane("option")[39], "'")  # ⌥Є
        self.assertEqual(self.layout.plane("shift+option")[35], "’")  # ⇧⌥З
        self.assertEqual(self.layout.plane("option")[35], "‘")  # ⌥З

    def test_brackets_sit_on_the_us_bracket_keys(self):
        """⌥ reproduces the US layout on the two keys Cyrillic took the brackets
        from, so there is one bracket position to remember rather than two. The
        US_ANSI assertions are the point of the test: they prove 33 and 30 really
        are those keys, rather than trusting a comment."""
        self.assertEqual((US_ANSI[33], US_ANSI[30]), ("[", "]"))
        option = self.layout.plane("option")
        shift_option = self.layout.plane("shift+option")
        self.assertEqual((option[33], option[30]), ("[", "]"))
        self.assertEqual((shift_option[33], shift_option[30]), ("{", "}"))

    def test_quote_pairs_share_the_number_row(self):
        """9 and 0 are the quote keys: ⌥ gives the English pair, ⇧⌥ the Ukrainian
        one, opening on 9 and closing on 0 in both. Pinned by codepoint, because
        “ ” « „ are four characters that look alike in a diff."""
        option = self.layout.plane("option")
        shift_option = self.layout.plane("shift+option")
        self.assertEqual((option[25], option[29]), ("“", "”"))
        self.assertEqual((shift_option[25], shift_option[29]), ("«", "»"))

    def test_angle_brackets_are_easier_than_their_maths_lookalikes(self):
        """ASCII < > on ⌥, the maths ≤ ≥ they displaced on ⇧⌥. Typing HTML or
        code in Ukrainian is common; typing ≤ is not."""
        option = self.layout.plane("option")
        shift_option = self.layout.plane("shift+option")
        self.assertEqual((option[43], option[47]), ("<", ">"))
        self.assertEqual((shift_option[43], shift_option[47]), ("≤", "≥"))

    def test_the_option_layers_can_still_type_everything(self):
        """Moving characters around these layers is routine; quietly dropping one
        is not. If this fails and the change was intended, regenerate with
        --update-inventory and let the diff be reviewed."""
        self.assertEqual(dict(option_layer_characters(self.layout)), read_inventory())

    def test_caps_option_tracks_option_on_non_letters(self):
        """⌥ and ⇪⌥ are separate keyMaps, so a punctuation edit applied to one and
        not the other makes caps lock silently change punctuation."""
        option = self.layout.key_maps[self.layout.modifiers.resolve("option")]
        caps_option = self.layout.key_maps[
            self.layout.modifiers.resolve("caps", "option")
        ]
        for code, output in option.items():
            if output and not output.isalpha():
                self.assertEqual(
                    caps_option.get(code), output, f"caps+option differs at {code}"
                )

    def test_command_layer_is_us_ansi(self):
        """Why ⌘-shortcuts are unaffected by anything this fork does: the ⌘ layer
        is the US ANSI layout, key for key, so ⌘C reaches C and not С."""
        command = self.layout.key_maps[self.layout.modifiers.resolve("command")]
        deviations = {
            code: (command.get(code), expected)
            for code, expected in US_ANSI.items()
            if command.get(code) != expected
        }
        self.assertEqual(deviations, {})

    def test_caps_only_changes_letter_case(self):
        base = self.layout.plane("base")
        caps = self.layout.plane("caps")
        for code, output in base.items():
            if output and not output.isalpha():
                self.assertEqual(
                    caps.get(code), output, f"caps changed non-letter key {code}"
                )

    def test_control_characters_survive_the_parse(self):
        """load() parks C0 controls in a private-use block; decode_controls has
        to bring them back, or a plane silently contains U+E00D for return."""
        control_plane = self.layout.key_maps["7"]
        self.assertEqual(control_plane[36], "\r")
        for output in control_plane.values():
            if output:
                self.assertFalse(
                    any("\uE000" <= ch <= "\uE01F" for ch in output),
                    f"undecoded placeholder in {output!r}",
                )


if __name__ == "__main__":
    if "--update-inventory" in sys.argv:
        counts = write_inventory(KeyLayout(str(LAYOUT)))
        print(f"{INVENTORY.name}: {len(counts)} characters, {sum(counts.values())} keys")
        sys.exit(0)
    unittest.main(verbosity=2)
