# Ukrainian - Mac PC

A Ukrainian keyboard layout for macOS. It is the familiar community
"Ukrainian - PC" layout with two keys fixed: a real Ukrainian apostrophe, and
slash where you can actually reach it.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/layout-quad-dark.svg">
  <img alt="Ukrainian - Mac PC keyboard layout" src="docs/images/layout-quad-light.svg">
</picture>

Installs alongside "Ukrainian - PC" rather than replacing it, so you can try it
and switch back. Everything else about the layout is untouched, and ⌘-shortcuts
are unaffected.

**[Download the latest release →](https://github.com/jenkokov/ukrainian-keyboard-layout/releases)**

## The two changes

### `ʼ` — a real apostrophe

The `` ` `` key now types **U+02BC ʼ**, the typographically correct Ukrainian
apostrophe, instead of the programmer's quote `'` U+0027.

To Unicode, U+02BC is a *letter* rather than punctuation. That is almost always
what you want in Ukrainian: it keeps `пʼять` a single word, so double-clicking
selects the whole thing and a line break never lands inside it.

The one catch worth knowing: text typed with `ʼ` will not match text typed with
`'` or `’` in a naive search. If you need the others, ASCII `'` is on **⇧⌥9** and
`’` on **⇧⌥З**.

### `/` without shift

On the `\|` key, `/` and `\` swap places: **`/` is now unmodified**, `\` is on
shift. Slash is far more common than backslash in ordinary Ukrainian typing.
Nothing is lost — both characters stay on the same key.

### Everything else is unchanged

Exactly five cells differ from upstream across the whole layout, all on those two
keys. The option, shift+option, ⌘ and ⌃ layers are identical. The ⌘ layer is the US
ANSI layout key for key, so every shortcut still lands on the same physical key —
`⌘C` reaches `C`, not `С`.

That does mean this is **not** a strict superset: muscle memory from
"Ukrainian - PC" transfers everywhere except those two keys.

## Install

Download `Ukrainian-Mac-PC-<version>.zip` from
[Releases](https://github.com/jenkokov/ukrainian-keyboard-layout/releases), then:

```sh
unzip Ukrainian-Mac-PC-*.zip -d ~/Library/"Keyboard Layouts"
```

**Log out and back in.** macOS only reads keyboard layouts at login, so this step
is not optional.

Then add it under **System Settings › Keyboard › Input Sources › Edit › + ›
Ukrainian**, and pick **Ukrainian - Mac PC**.

## Uninstall

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
