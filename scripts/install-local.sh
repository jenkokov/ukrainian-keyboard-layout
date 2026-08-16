#!/bin/bash
# Build and install into ~/Library/Keyboard Layouts for testing.
# Log out and back in afterwards, then add the layout under
# System Settings > Keyboard > Input Sources.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
source layout.conf

./scripts/build.sh "$@"

DEST="$HOME/Library/Keyboard Layouts"
mkdir -p "$DEST"
rm -rf "${DEST:?}/${LAYOUT_NAME}.bundle"
cp -R "dist/${LAYOUT_NAME}.bundle" "$DEST/"

echo "==> installed to ${DEST}/${LAYOUT_NAME}.bundle"
echo "    log out and back in for macOS to pick it up"
