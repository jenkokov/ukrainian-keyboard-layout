# Ukrainian - Mac PC

A Ukrainian keyboard layout for macOS, forked from the community "Ukrainian - PC"
layout. Full documentation and layout diagrams are coming; for now this repo holds
the source and the build pipeline.

## Install

Download the latest `Ukrainian-Mac-PC-<version>.zip` from
[Releases](https://github.com/jenkokov/ukrainian-keyboard-layout/releases), then:

```sh
unzip Ukrainian-Mac-PC-*.zip -d ~/Library/"Keyboard Layouts"
```

Log out and back in, then add it under **System Settings › Keyboard › Input Sources › Edit › + › Ukrainian**.

macOS only loads keyboard layouts at login, so the logout is not optional.

## Build

```sh
./scripts/build.sh            # -> dist/Ukrainian - Mac PC.bundle + dist/*.zip
./scripts/install-local.sh    # build, then install into ~/Library/Keyboard Layouts
```

## Layout

```
layout.conf                          name, bundle ID, language — drives everything
src/Ukrainian - Mac PC.keylayout     the layout itself; edit here (Ukelele opens it)
src/Info.plist.in                    bundle metadata template
src/version.plist.in                 version metadata template
src/icon.icns                        input-menu icon
scripts/validate.py                  structural checks on the keylayout
scripts/build.sh                     assembles dist/*.bundle and the release zip
.github/workflows/release.yml        builds on push, publishes a release on v* tags
```

`InfoPlist.strings` is generated at build time, so the layout name lives in exactly
one place.

## Release

```sh
git tag v1.0.0 && git push --tags
```

CI builds on a macOS runner and attaches the zip to the release.

## Validation

`scripts/validate.py` runs on every build and checks that `<layout>` points at a
keyMapSet and modifierMap that exist, that key codes are unique within each keyMap,
that every selected `mapIndex` is present, and that referenced actions are defined —
the mistakes that make a layout silently fail to load rather than error visibly.

`xmllint` is deliberately not used: `.keylayout` files are XML **1.1**, because they
carry C0 control characters in `output` attributes that XML 1.0 forbids, and libxml2
only implements 1.0. It rejects a perfectly valid layout.

## Editing the layout

Open `src/Ukrainian - Mac PC.keylayout` in [Ukelele](https://software.sil.org/ukelele/)
or any text editor. Keep the `name=` attribute in sync with `LAYOUT_NAME` in
`layout.conf` — the build fails loudly if they drift.

The `id="-19217"` on the `<keyboard>` element is deliberately negative and distinct
from the upstream layout's, so both can be installed side by side.

## Provenance

Derived from the "Ukrainian - PC" layout produced with
[Ukelele](https://software.sil.org/ukelele/). Modifications in this repo are MIT
licensed; see [LICENSE](LICENSE).
