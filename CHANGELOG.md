# Changelog

## Unreleased

### Changed

The ⌥ and ⇧⌥ planes are rearranged, with ⌥ following the US layout wherever
Cyrillic displaced a punctuation key. This is a pure rearrangement: taken
together, the two planes carry exactly the same characters as upstream, with the
same number of keys for each. `scripts/upstream-option-layers.txt` records that
multiset and `scripts/test_keylayout.py` asserts it every build.

- **`[` `]` moved to ⌥Х and ⌥Ї, and `{` `}` to ⇧⌥Х and ⇧⌥Ї** — keycodes 33 and 30,
  which are the physical keys a US keyboard puts the brackets on. Holding ⌥ now
  reaches the same bracket key you already use in English, in the same order.

  Upstream scatters them: `[` `]` on keycode 50 and `{` `}` on keycode 4, both
  pairs with the *closing* bracket on ⌥ and the opening one on ⇧⌥.

- **`“` `”` moved to ⌥9 and ⌥0, under `«` `»` on ⇧⌥9 and ⇧⌥0.** Both quote pairs
  on one pair of keys, opening on 9 and closing on 0 in both layers. `“` was
  previously on two keys at once; the `“` `„` pair on the `.` key is untouched.

- **`ъ` `Ъ` moved to ⌥Р and ⇧⌥Р**, the slots the braces vacated.

- **`(` `)` are on ⌥` and ⇧⌥`**, where they went when the brackets left the
  number row. On ⌥9 and ⌥0 they had been duplicating what shift already gives.

  **ASCII `'` (U+0027) is now on ⇧⌥=, not ⇧⌥9.** `` ` `` moved with it, to ⌥=.

- **`<` and `>` swapped with `≤` and `≥`** on the `б` and `ю` keys (keycodes 43 and
  47). ASCII angle brackets are now on plain ⌥; the maths symbols they displaced
  are on ⇧⌥. Writing markup or code while in a Ukrainian layout is ordinary;
  typing `≤` is not.

Applied to the ⇪⌥ plane as well, so caps lock does not change which character
these keys produce. The ⌘ and ⌃ planes are untouched, as always.

## 0.2.0 — 2026-08-16

### Changed

- **Apostrophe is now U+02BC ʼ (modifier letter apostrophe)** on the unmodified
  `` ` `` key (keycode 50), replacing U+0027 `'`. U+02BC is the typographically
  correct Ukrainian apostrophe; U+0027 is a programmer's quote that happens to be
  reachable on a typewriter.

  Note that U+02BC is a *letter* to Unicode, not punctuation. That is usually what
  you want — it keeps `пʼять` as a single word for selection and line breaking —
  but text typed with it will not match text typed with U+0027 or U+2019 under a
  naive search.

  ASCII `'` (U+0027) is still available on **⇧⌥9**, and ’ (U+2019) on **⇧⌥З**
  (with ‘ U+2018 on **⌥З**).
  The ⌘ plane is untouched — it is the US ANSI layout key for key — so ⌘`
  still cycles windows and ⌘' still reaches the ANSI quote key.

- **`/` and `\` swapped** on the `\|` key (keycode 42): `/` is now unmodified and
  `\` is on shift. Slash is far more common in ordinary Ukrainian typing than
  backslash. Nothing is lost — both characters remain on the same key.
  ⌘\ still sends a backslash, since the ⌘ plane is US ANSI regardless.

Both changes are applied to the caps-lock plane as well, so caps lock does not
change which character these keys produce.

## 0.1.0 — 2026-08-16

Baseline fork of the Ukelele-produced "Ukrainian - PC" layout as
"Ukrainian - Mac PC": new display name, own bundle ID and keyboard id so both
can be installed side by side. Key mappings are byte-identical to upstream.
