#!/usr/bin/env python3
"""Parse a .keylayout file into resolved key planes.

Shared by validate.py (structure) and render.py (diagrams), so both read the
layout through the same rules. The interesting part is resolve(): a modifierMap
is an ordered match table over the 256 physical modifier states, not a list of
named planes, and getting it wrong produces diagrams that look plausible and are
wrong.

Run directly to dump a plane:

    python3 scripts/keylayout.py src/*.keylayout base shift option
"""

import re
import sys
import xml.etree.ElementTree as ET

# .keylayout is XML 1.1: `output` attributes carry raw C0 control characters,
# which XML 1.0 forbids and which every stdlib parser therefore rejects. Park
# them in a private-use block for the duration of the parse and map them back on
# the way out, so a control character stays itself rather than becoming U+FFFD.
CONTROL_REF = re.compile(r"&#x00([01][0-9a-fA-F]);")
_PUA_BASE = 0xE000
_PUA_RANGE = re.compile("[\uE000-\uE01F]")


def load(path):
    """Parse `path` and return its <keyboard> element."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    text = text.replace('<?xml version="1.1"', '<?xml version="1.0"', 1)
    text = CONTROL_REF.sub(lambda m: chr(_PUA_BASE + int(m.group(1), 16)), text)
    text = re.sub(r"<!DOCTYPE[^>]*>", "", text, count=1)
    return ET.fromstring(text)


def decode_controls(text):
    """Undo load()'s private-use parking, restoring real C0 characters."""
    if text is None:
        return None
    return _PUA_RANGE.sub(lambda m: chr(ord(m.group()) - _PUA_BASE), text)


# --- modifier resolution ---------------------------------------------------

# The eight bits macOS keys a modifierMap on. Left and right are separate bits
# for shift/option/control; caps and command have only one each.
MODIFIER_BITS = (
    "command",
    "shift",
    "rightShift",
    "caps",
    "option",
    "rightOption",
    "control",
    "rightControl",
)

# `anyShift` and friends are a disjunction over the pair, not a bit of their own.
_PAIRS = {
    "shift": ("shift", "rightShift"),
    "option": ("option", "rightOption"),
    "control": ("control", "rightControl"),
}


class Pattern:
    """One <modifier keys="..."> element, compiled for matching.

    A token means that modifier must be down; a `?` suffix means it may be
    either; a modifier no token mentions must be up. `anyX` mentions both bits
    of the pair and requires at least one of them.
    """

    __slots__ = ("keys", "required", "disjunctions")

    def __init__(self, keys):
        self.keys = keys
        required = {}
        disjunctions = []
        mentioned = set()

        for token in keys.split():
            optional = token.endswith("?")
            name = token[:-1] if optional else token
            if name.startswith("any"):
                pair = name[3].lower() + name[4:]
                if pair not in _PAIRS:
                    raise ValueError(f"unknown modifier token {token!r}")
                left, right = _PAIRS[pair]
                mentioned.update((left, right))
                if not optional:
                    disjunctions.append((left, right))
            else:
                if name not in MODIFIER_BITS:
                    raise ValueError(f"unknown modifier token {token!r}")
                mentioned.add(name)
                if not optional:
                    required[name] = True

        for bit in MODIFIER_BITS:
            if bit not in mentioned:
                required.setdefault(bit, False)

        self.required = required
        self.disjunctions = disjunctions

    def matches(self, state):
        for bit, wanted in self.required.items():
            if state.get(bit, False) != wanted:
                return False
        return all(state.get(a) or state.get(b) for a, b in self.disjunctions)

    def __repr__(self):
        return f"Pattern({self.keys!r})"


class ModifierMap:
    """An ordered <keyMapSelect> table plus its defaultIndex."""

    def __init__(self, element):
        self.id = element.get("id")
        self.default_index = element.get("defaultIndex")
        self.selects = [
            (select.get("mapIndex"), [Pattern(m.get("keys", "")) for m in select.iter("modifier")])
            for select in element.iter("keyMapSelect")
        ]

    def resolve(self, *modifiers):
        """Map a set of held modifiers to a keyMap index.

        Accepts bit names from MODIFIER_BITS; `resolve()` is the bare keyboard.
        Falls back to defaultIndex when nothing matches, exactly as macOS does.
        """
        unknown = set(modifiers) - set(MODIFIER_BITS)
        if unknown:
            raise ValueError(f"unknown modifier(s): {sorted(unknown)}")
        state = {bit: bit in modifiers for bit in MODIFIER_BITS}
        for index, patterns in self.selects:
            if any(pattern.matches(state) for pattern in patterns):
                return index
        return self.default_index


# --- layout ----------------------------------------------------------------

# The planes worth documenting. The ⌘ and ⌃ planes are deliberately absent: they
# are Latin passthrough and control characters, not part of the Ukrainian layout.
PLANES = {
    "base": (),
    "shift": ("shift",),
    "option": ("option",),
    "shift+option": ("shift", "option"),
    "caps": ("caps",),
}


class KeyLayout:
    def __init__(self, path):
        self.path = path
        self.root = load(path)
        self.name = self.root.get("name")
        self.id = self.root.get("id")

        key_map_sets = {ks.get("id"): ks for ks in self.root.iter("keyMapSet")}
        modifier_maps = {mm.get("id"): mm for mm in self.root.iter("modifierMap")}

        layout = next(self.root.iter("layout"), None)
        if layout is None:
            raise ValueError(f"{path}: no <layout>")
        key_map_set = key_map_sets[layout.get("mapSet")]
        self.modifiers = ModifierMap(modifier_maps[layout.get("modifiers")])

        # index -> {keycode: output}. A key with an action and no output has no
        # single output to draw; it is stored as None and rendered blank.
        self.key_maps = {}
        for key_map in key_map_set.iter("keyMap"):
            self.key_maps[key_map.get("index")] = {
                int(key.get("code")): decode_controls(key.get("output"))
                for key in key_map.iter("key")
            }

    def plane(self, name):
        """Return {keycode: output} for a named plane in PLANES."""
        if name not in PLANES:
            raise KeyError(f"unknown plane {name!r}; known: {sorted(PLANES)}")
        return self.key_maps[self.modifiers.resolve(*PLANES[name])]


# --- geometry --------------------------------------------------------------

# Virtual keycode -> position, which is the one thing not derivable from the
# file. Rows are lists of (what, width_in_units): an int is a keycode whose
# output gets drawn, a str is a fixed legend for a key the layout never emits.
# Widths are ANSI, and every row sums to 15.0 so the picture squares up.
ROWS = (
    ((50, 1), (18, 1), (19, 1), (20, 1), (21, 1), (23, 1), (22, 1),
     (26, 1), (28, 1), (25, 1), (29, 1), (27, 1), (24, 1), ("⌫", 2)),
    (("⇥", 1.5), (12, 1), (13, 1), (14, 1), (15, 1), (17, 1), (16, 1),
     (32, 1), (34, 1), (31, 1), (35, 1), (33, 1), (30, 1), (42, 1.5)),
    (("⇪", 1.75), (0, 1), (1, 1), (2, 1), (3, 1), (5, 1), (4, 1),
     (38, 1), (40, 1), (37, 1), (41, 1), (39, 1), ("⏎", 2.25)),
    (("⇧", 2.25), (6, 1), (7, 1), (8, 1), (9, 1), (11, 1), (45, 1),
     (46, 1), (43, 1), (47, 1), (44, 1), ("⇧", 2.75)),
    (("⌃", 1.25), ("⌥", 1.25), ("⌘", 1.5), (49, 7),
     ("⌘", 1.5), ("⌥", 1.25), ("⌃", 1.25)),
)

ROW_UNITS = 15.0

# If the geometry table drifts by one, every diagram is subtly wrong and still
# looks fine. Pin it to something a human can check at a glance.
HOME_ROW_CHECK = "йцукенгшщзхї"


def check_geometry(layout):
    """Raise if ROWS and the layout's base plane disagree about the letter row."""
    base = layout.plane("base")
    letters = "".join(
        base.get(what) or "" for what, _ in ROWS[1] if isinstance(what, int) and what != 42
    )
    if letters != HOME_ROW_CHECK:
        raise AssertionError(
            f"geometry/layout mismatch: upper letter row reads {letters!r}, "
            f"expected {HOME_ROW_CHECK!r}"
        )
    for row in ROWS:
        total = sum(width for _, width in row)
        if abs(total - ROW_UNITS) > 1e-9:
            raise AssertionError(f"row sums to {total} units, expected {ROW_UNITS}")


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    layout = KeyLayout(argv[1])
    check_geometry(layout)
    for name in argv[2:] or ["base"]:
        plane = layout.plane(name)
        rendered = "".join(
            plane.get(what) or "·" for row in ROWS for what, _ in row if isinstance(what, int)
        )
        print(f"{name:>13}  {rendered}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
