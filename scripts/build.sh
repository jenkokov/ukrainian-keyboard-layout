#!/bin/bash
# Assemble the keyboard layout bundle from src/ into dist/, then zip it.
#
#   ./scripts/build.sh            version from `git describe`, or 0.0.0-dev
#   ./scripts/build.sh 1.2.0      explicit version
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck source=layout.conf
source layout.conf

VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
	tag="$(git describe --tags --abbrev=0 2>/dev/null || true)"
	VERSION="${tag#v}"
	VERSION="${VERSION:-0.0.0-dev}"
fi
BUILD="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"

KEYLAYOUT="src/${LAYOUT_NAME}.keylayout"
BUNDLE="dist/${LAYOUT_NAME}.bundle"
ARCHIVE="dist/${ARCHIVE_NAME}-${VERSION}.zip"

echo "==> ${LAYOUT_NAME} ${VERSION} (${BUILD})"

# --- validate source -------------------------------------------------------
[[ -f "$KEYLAYOUT" ]] || { echo "missing $KEYLAYOUT" >&2; exit 1; }

# The name inside the XML is what macOS shows in the input menu; if it drifts
# from LAYOUT_NAME the bundle and the layout disagree and the layout silently
# fails to appear. Catch that here rather than after a logout.
xml_name="$(sed -n 's/.*<keyboard[^>]*name="\([^"]*\)".*/\1/p' "$KEYLAYOUT" | head -1)"
if [[ "$xml_name" != "$LAYOUT_NAME" ]]; then
	echo "name mismatch: layout.conf says '${LAYOUT_NAME}', $KEYLAYOUT says '${xml_name}'" >&2
	exit 1
fi

python3 scripts/validate.py "$KEYLAYOUT"

# --- assemble --------------------------------------------------------------
rm -rf "$BUNDLE" "$ARCHIVE"
mkdir -p "$BUNDLE/Contents/Resources/en.lproj"

render() {
	sed -e "s|@@LAYOUT_NAME@@|${LAYOUT_NAME}|g" \
		-e "s|@@BUNDLE_ID@@|${BUNDLE_ID}|g" \
		-e "s|@@INTENDED_LANGUAGE@@|${INTENDED_LANGUAGE}|g" \
		-e "s|@@VERSION@@|${VERSION}|g" \
		-e "s|@@BUILD@@|${BUILD}|g" \
		"$1" >"$2"
}

render src/Info.plist.in "$BUNDLE/Contents/Info.plist"
render src/version.plist.in "$BUNDLE/Contents/version.plist"
cp "$KEYLAYOUT" "$BUNDLE/Contents/Resources/${LAYOUT_NAME}.keylayout"
cp src/icon.icns "$BUNDLE/Contents/Resources/${LAYOUT_NAME}.icns"

# InfoPlist.strings must be UTF-16 for the input-source name to render.
printf '"%s" = "%s";\n' "$LAYOUT_NAME" "$LAYOUT_NAME" |
	iconv -f UTF-8 -t UTF-16LE |
	{ printf '\xff\xfe'; cat; } >"$BUNDLE/Contents/Resources/en.lproj/InfoPlist.strings"

plutil -lint "$BUNDLE/Contents/Info.plist" >/dev/null
plutil -lint "$BUNDLE/Contents/version.plist" >/dev/null

# --- package ---------------------------------------------------------------
if command -v ditto >/dev/null; then
	ditto -c -k --sequesterRsrc --keepParent "$BUNDLE" "$ARCHIVE"
else
	(cd dist && zip -qr "$(basename "$ARCHIVE")" "$(basename "$BUNDLE")")
fi

echo "==> $BUNDLE"
echo "==> $ARCHIVE"
