# Changelog

## 0.3.0 — 2026-08-17

### Changed

The ⌥ and ⇧⌥ planes are reorganised around one rule: **where a Cyrillic letter
covers a US punctuation key, ⌥ gives that key's English character back.** Typing
Ukrainian and code in the same day should not mean learning a second set of
positions for the same symbols.

Nothing became untypeable. `scripts/option-layer-inventory.txt` lists every
character these layers can produce and `scripts/test_keylayout.py` asserts it, so
a rearrangement cannot quietly drop something.

- **`[` `]` on ⌥Х and ⌥Ї, `{` `}` on ⇧⌥Х and ⇧⌥Ї** — keycodes 33 and 30, the
  physical keys a US keyboard puts the brackets on. Previously `[` `]` were on
  keycode 50 and `{` `}` on keycode 4, both pairs with the *closing* bracket on
  ⌥ and the opening one on ⇧⌥.

- **`≈` and `≠` on ⌥= and ⇧⌥=**, beside the `=` they are variations on. Each had
  been occupying both option slots of its own key (`ч` and `с`) with a duplicate.

- **ASCII `'` and `"` on ⌥Ч and ⌥С**, in the space that freed up. They went to
  the US apostrophe key (⌥Є) first, which was wrong: `э` lives there, and the
  non-Ukrainian Cyrillic letters each sit on the key of their Ukrainian
  counterpart — `ё` on Е, `ъ` on Ь, `ґ` on Г. That pattern is worth more than one
  more US position, so the letters keep their keys.

- **`` ` `` on ⌥ and `~` on ⇧⌥ of the ʼ key** — keycode 50, the US backtick key.
  `~` had been occupying both option slots of the `ь` key; it now has one home.

- **`|` on ⌥ of the `/` key** — keycode 42, the US backslash key, completing
  `/ \ |` on one key. It displaced a second copy of `ё` `Ё`, which remain on `е`.

- **`<` `>` on ⌥Б and ⌥Ю**, with the maths `≤` `≥` they displaced on ⇧⌥. Writing
  markup while in a Ukrainian layout is ordinary; typing `≤` is not.

- **`“` `”` on ⌥9 and ⌥0, `«` `»` on ⇧⌥9 and ⇧⌥0.** Both quote pairs on one pair
  of keys, opening on 9 and closing on 0 in both layers. The `“` `„` pair on the
  `.` key is untouched.

- **`ъ` `Ъ` on ⌥Ь and ⇧⌥Ь**, the soft sign key giving the hard sign. **`(` `)` on
  ⌥Р and ⇧⌥Р.**

Applied to the ⇪⌥ plane as well, so caps lock does not change which character
these keys produce. The ⌘ and ⌃ planes are untouched, as always.

### Documentation

- The README leads with what the layout is rather than with a diff against
  "Ukrainian - PC", which most readers have never used. The comparison is still
  there, in one section for the people it serves.
- Install has a Finder path alongside the Terminal one. Copying the bundle into
  `~/Library/Keyboard Layouts` *is* the installation — there is no double-click
  installer for keyboard layouts, and nothing said so.
- The Terminal command is `ditto -x -k` rather than `unzip`, which prompts before
  replacing an existing copy and leaves a `__MACOSX` folder behind.

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
