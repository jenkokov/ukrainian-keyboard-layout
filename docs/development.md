# Development

Everything here is stdlib Python 3 and bash. There is nothing to install.

```sh
./scripts/build.sh                                     # -> dist/*.bundle + dist/*.zip
./scripts/install-local.sh                             # build, then install locally
python3 scripts/test_keylayout.py                      # unit tests
python3 scripts/render.py src/*.keylayout docs/images   # regenerate diagrams
python3 scripts/keylayout.py src/*.keylayout base shift # dump a plane to stdout
```

`build.sh` runs the structural checks and the unit tests before it packages
anything, so a broken layout never reaches `dist/`.

## Repository layout

```
layout.conf                          name, bundle ID, language — drives everything
src/Ukrainian - Mac PC.keylayout     the layout itself; edit here (Ukelele opens it)
src/Info.plist.in                    bundle metadata template
src/version.plist.in                 version metadata template
src/icon.icns                        input-menu icon
scripts/keylayout.py                 parser: modifier resolution + key geometry
scripts/validate.py                  structural checks on the keylayout
scripts/render.py                    generates docs/images/*.svg from the keylayout
scripts/test_keylayout.py            unit tests for the resolver and geometry
scripts/build.sh                     assembles dist/*.bundle and the release zip
docs/layers.md                       one diagram per modifier layer
docs/development.md                  this file
.github/workflows/release.yml        builds on push, publishes a release on v* tags
```

`InfoPlist.strings` is generated at build time, so the layout name lives in exactly
one place: `LAYOUT_NAME` in `layout.conf`.

## Editing the layout

Open `src/Ukrainian - Mac PC.keylayout` in
[Ukelele](https://software.sil.org/ukelele/) or any text editor, then regenerate
the diagrams and commit them alongside the change.

Keep the `name=` attribute in sync with `LAYOUT_NAME` in `layout.conf` — the build
fails loudly if they drift, because a bundle whose name disagrees with its layout
silently fails to appear in the input menu.

The `id="-19217"` on `<keyboard>` is deliberately negative and distinct from
upstream's, so both layouts can be installed side by side.

## Diagrams

`scripts/render.py` generates every SVG in `docs/images/` from the `.keylayout`
itself, so a diagram cannot drift from the mappings it claims to document. CI
regenerates them and fails on any diff — a mapping change with a stale picture does
not merge.

Output is deterministic (no timestamps, no generated ids), so a diff in
`docs/images/` always means a mapping actually changed.

Three styles come off one geometry table:

- **quad** — all four planes on one keycap as a 2×2 grid, plus a legend. The
  README hero.
- **combined** — base, shift and option on one keycap. Simpler, narrower.
- **plane** — one character per keycap, one file per plane, with the modifiers you
  hold highlighted. Used by [layers.md](layers.md).

Light and dark are separate files rather than one SVG carrying a
`prefers-color-scheme` query, because GitHub renders SVGs through an `<img>` where
that query does not reliably follow the reader's theme.

A shifted legend is omitted where it repeats or merely capitalises the one below
it. On a Cyrillic layout that is most of the keyboard, so what remains is exactly
the keys where shift does something you would not have guessed.

The ⌘ and ⌃ planes are deliberately not drawn: they are Latin passthrough and
control characters, part of how macOS shortcuts work rather than part of the
Ukrainian layout. Caps lock is not drawn either — it changes letter case only, and
`test_keylayout.py` asserts that it leaves every non-letter key alone.

## How the layout file is read

`scripts/keylayout.py` is the shared parser; `validate.py` and `render.py` both go
through it.

**It is XML 1.1, not 1.0.** `.keylayout` files carry raw C0 control characters in
`output` attributes, which XML 1.0 forbids and every stdlib parser therefore
rejects. `xmllint` is not usable here for the same reason — libxml2 only implements
1.0 and will reject a perfectly valid layout. The parser rewrites the declaration,
parks C0 controls in a private-use block for the duration of the parse, and maps
them back afterwards, so a control character stays itself rather than becoming
U+FFFD.

**A `modifierMap` is an ordered match table, not a list of named planes.** It is
evaluated over the 256 physical modifier states — command, caps, and separate left
and right bits for shift, option and control. Within one `<modifier keys="...">`
pattern:

- a bare token means that modifier must be **down**
- a `?` suffix means it **may** be either
- a modifier no token mentions must be **up**
- `anyShift` / `anyOption` / `anyControl` mention both bits of a pair and require
  **at least one** of them
- the first matching `keyMapSelect` in document order wins, and `defaultIndex`
  catches anything unmatched

Do not shortcut this by assuming "map 5 is base". `resolve()` in `keylayout.py`
implements it properly, and the tests walk all 256 states to pin the result: map 7
absorbs 181 of them, no state matches two `keyMapSelect` entries, and exactly one
state — every modifier held at once — falls through to `defaultIndex`.

## Validation

`scripts/validate.py` checks the invariants that make a layout silently fail to
load rather than error visibly: that `<layout>` points at a keyMapSet and
modifierMap that exist, that key codes are unique within each keyMap, that every
selected `mapIndex` is present, and that referenced actions are defined.

`scripts/test_keylayout.py` covers what fails silently *and* plausibly:

- the modifier resolver, across all 256 states
- the geometry table, pinned by asserting the upper letter row reads `йцукенгшщзхї`,
  so an off-by-one fails loudly instead of rendering a subtly wrong picture
- the two mappings this fork exists for, asserted by codepoint so a lookalike
  character cannot pass
- that the ⌘ layer is US ANSI key for key, which is why shortcuts are unaffected
- that caps lock changes letter case only
- that C0 control characters survive the parse

It does not check semantics beyond that: nothing here can tell you a key produces
the *wrong* letter, only that the file is well-formed and internally consistent.

## Release

```sh
git tag v1.0.0 && git push --tags
```

CI builds on a macOS runner and attaches the zip to the GitHub release. Version
numbers come from the tag; `build.sh` falls back to `git describe` locally.
