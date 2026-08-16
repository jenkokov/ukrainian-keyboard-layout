# Changelog

## Unreleased

### Changed

The ⌥ and ⇧⌥ planes are rearranged. This is a pure rearrangement: taken together,
the two planes carry exactly the same set of characters as before, just in
different places. `scripts/test_keylayout.py` asserts that nothing fell off.

- **`[` and `]` moved to ⌥9 and ⌥0**, and **`«` `»` to ⇧⌥9 and ⇧⌥0.** The brackets
  were on one key in the far corner (⌥` and ⇧⌥`), and the guillemets on another
  (⌥= and ⇧⌥=). Both are common enough in Ukrainian typing to deserve the number
  row, where they sit under the same fingers as `(` and `)` one row up.

  What they displaced moved to where they came from: ⌥9 and ⌥0 were duplicates of
  shift's `(` and `)`, and are now on ⌥` and ⇧⌥` — still reachable, no longer
  occupying the best real estate on the layout for characters shift already
  provides.

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
