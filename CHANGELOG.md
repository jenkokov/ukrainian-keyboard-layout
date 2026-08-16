# Changelog

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
