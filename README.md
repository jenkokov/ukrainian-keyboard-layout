# Ukrainian - Mac PC

A Ukrainian keyboard layout for macOS. It is the familiar community
"Ukrainian - PC" layout with the everyday friction taken out: a real Ukrainian
apostrophe, slash where you can actually reach it, and brackets and quotes moved
somewhere your fingers already are.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/layout-quad-dark.svg">
  <img alt="Ukrainian - Mac PC keyboard layout" src="docs/images/layout-quad-light.svg">
</picture>

Installs alongside "Ukrainian - PC" rather than replacing it, so you can try it
and switch back. Everything else about the layout is untouched, and ⌘-shortcuts
are unaffected.

**[Download the latest release →](https://github.com/jenkokov/ukrainian-keyboard-layout/releases)**

## What's different

### `ʼ` — a real apostrophe

The `` ` `` key now types **U+02BC ʼ**, the typographically correct Ukrainian
apostrophe, instead of the programmer's quote `'` U+0027.

To Unicode, U+02BC is a *letter* rather than punctuation. That is almost always
what you want in Ukrainian: it keeps `пʼять` a single word, so double-clicking
selects the whole thing and a line break never lands inside it.

The one catch worth knowing: text typed with `ʼ` will not match text typed with
`'` or `’` in a naive search. If you need the others, ASCII `'` is on **⇧⌥=** and
`’` on **⇧⌥З**.

### `/` without shift

On the `\|` key, `/` and `\` swap places: **`/` is now unmodified**, `\` is on
shift. Slash is far more common than backslash in ordinary Ukrainian typing.
Nothing is lost — both characters stay on the same key.

### Brackets and quotes on the number row

**`[` `]` are on ⌥9 and ⌥0**, and **`«` `»` on ⇧⌥9 and ⇧⌥0** — directly under
`(` and `)`, so all three pairs live on the same two fingers.

Upstream parks them in the far corners of the keyboard, on the `` ` `` and `=`
keys, while ⌥9 and ⌥0 sit there holding a second copy of `(` and `)` that shift
already gives you. This trades that duplication for the two pairs you actually
reach for. The displaced `(` `)` are still there, on ⌥` and ⇧⌥`.

### `<` `>` without the extra reach

On the `б` and `ю` keys, ASCII **`<` and `>` are on plain ⌥**; the maths `≤` `≥`
they displaced moved to ⇧⌥. Writing markup or code without leaving the Ukrainian
layout is ordinary. Typing `≤` is not.

### Everything else is unchanged

Nothing was removed. The ⌥ and ⇧⌥ layers between them carry exactly the same set
of characters as upstream — every change above is a rearrangement, and the tests
assert that no character fell off the layout.

The ⌘ and ⌃ layers are untouched. The ⌘ layer is the US ANSI layout key for key,
so every shortcut still lands on the same physical key — `⌘C` reaches `C`, not `С`.

That does mean this is **not** a strict superset: muscle memory from
"Ukrainian - PC" transfers everywhere except the seven keys above.

## Install

Download `Ukrainian-Mac-PC-<version>.zip` from
[Releases](https://github.com/jenkokov/ukrainian-keyboard-layout/releases).

### In Finder

1. Double-click the zip. You get **Ukrainian - Mac PC.bundle**.
2. In Finder, press **⇧⌘G** and go to `~/Library/Keyboard Layouts`.
   If that folder doesn't exist, create it — the name has to be exact.
3. Drag the bundle in.

There is no double-click installer for keyboard layouts; copying the bundle into
that folder *is* the installation.

### In Terminal

```sh
ditto -x -k Ukrainian-Mac-PC-*.zip ~/Library/"Keyboard Layouts"
```

(`ditto` rather than `unzip`: it overwrites an existing copy without prompting,
and it doesn't leave a `__MACOSX` folder behind.)

### Either way

**Log out and back in.** macOS only reads keyboard layouts at login, so this step
is not optional.

Then add it under **System Settings › Keyboard › Input Sources › Edit › + ›
Ukrainian**, and pick **Ukrainian - Mac PC**.

## Uninstall

Drag **Ukrainian - Mac PC.bundle** out of `~/Library/Keyboard Layouts` (⇧⌘G in
Finder to get there), or:

```sh
rm -rf ~/Library/"Keyboard Layouts"/"Ukrainian - Mac PC.bundle"
```

Remove the input source in System Settings too, then log out. Deleting only the
bundle leaves a ghost entry in the input menu.

## Troubleshooting

**It doesn't appear in the input source list.** Almost always a missed logout.
macOS reads `~/Library/Keyboard Layouts` at login only.

**It appears but types the wrong characters.** You are probably typing on upstream
"Ukrainian - PC" — both show up as "Ukrainian" in the input menu, and this layout
still uses the upstream icon, so they look alike. Remove upstream while you
compare, or check which one is ticked in System Settings.

**An app ignores it.** A few apps request the ASCII-capable layout for shortcuts.
That is macOS behaviour and applies to upstream equally.

## Layer diagrams

Each keycap above is a 2×2 grid: left column unmodified, right column ⌥ (tinted);
bottom row unshifted, top row ⇧. A shifted legend is shown only where it does more
than capitalise the one below it.

If you would rather see one layer at a time, **[every layer has its own
diagram](docs/layers.md)** — base, shift, option and shift+option, each with the
keys you hold highlighted.

## Contributing and internals

Build instructions, how the diagrams are generated, and notes on the `.keylayout`
format are in **[docs/development.md](docs/development.md)**. Planned work is in
[ROADMAP.md](ROADMAP.md); what has changed is in [CHANGELOG.md](CHANGELOG.md).

## Credits

Derived from the "Ukrainian - PC" layout produced with
[Ukelele](https://software.sil.org/ukelele/). Modifications in this repo are MIT
licensed; see [LICENSE](LICENSE).
