# Layers

One diagram per modifier layer, with the keys you hold to reach it highlighted.
All four layers on a single keyboard are in the [README](../README.md); these are
for looking up one character at a time.

Every diagram here is generated from the layout file itself, so it cannot drift
from what the keyboard actually does. Don't edit them by hand — see
[development.md](development.md).

## Base

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="images/layout-base-dark.svg">
  <img alt="Base layer" src="images/layout-base-light.svg">
</picture>

The standard Ukrainian typewriter arrangement, with two keys chosen differently:
the apostrophe is **U+02BC ʼ** rather than `'`, and `/` sits unmodified on the
`\|` key.

## Shift

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="images/layout-shift-dark.svg">
  <img alt="Shift layer" src="images/layout-shift-light.svg">
</picture>

Letters capitalise. The number row carries `₴ ! " № ; % : ? * ( ) _ +`, and `\` is
here on the `\|` key.

## Option

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="images/layout-option-dark.svg">
  <img alt="Option layer" src="images/layout-option-light.svg">
</picture>

Where a Cyrillic letter covers a US punctuation key, ⌥ hands that key's English
character back. `[` `]` on **⌥Х** and **⌥Ї**, `'` and `"` on **⌥Є**, `` ` `` on
the apostrophe key, `|` on the `/` key, `<` `>` on **⌥Б** and **⌥Ю**. The English
quotes `“` `”` are on **⌥9** and **⌥0**, and `(` `)` on **⌥Р**.

The rest is what a Ukrainian layout is expected to carry: non-Ukrainian Cyrillic
(`ј џ ќ ё њ ѕ ў ъ ы ћ љ э ђ и`), typographic marks and maths.

Worth knowing that `‘` U+2018 is on **⌥З**, `’` U+2019 on **⇧⌥З**, and ASCII `'`
on **⌥Є**, if you need any of them alongside the U+02BC apostrophe.

## Shift + Option

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="images/layout-shift-option-dark.svg">
  <img alt="Shift plus Option layer" src="images/layout-shift-option-light.svg">
</picture>

Capitalised forms of the option layer, plus currency and the remaining
punctuation — again following US where it can. `{` `}` are on **⇧⌥Х** and
**⇧⌥Ї**, directly above the brackets; `~` on the apostrophe key, above `` ` ``.
The Ukrainian quotes `«` `»` are on **⇧⌥9** and **⇧⌥0**, above the English pair,
and `≤` `≥` on **⇧⌥Б** and **⇧⌥Ю**.

## Layers not shown

The ⌘ and ⌃ layers are deliberately absent. They are Latin passthrough and control
characters respectively — `⌘C` has to reach the `C` key, not `С` — so they are part
of how macOS shortcuts work rather than part of the Ukrainian layout. This fork does
not touch them.

Caps lock is also not shown: it changes letter case only, and leaves every
non-letter key, including the two this fork changes, exactly as the base layer.
`scripts/test_keylayout.py` asserts that.
