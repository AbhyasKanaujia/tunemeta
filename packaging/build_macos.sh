#!/usr/bin/env bash
# Builds dist/tunemeta.app and wraps it in dist/tunemeta.dmg.
# Run from a macOS machine with `pip install -e ".[gui,build]"` done first.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

pyinstaller \
  --windowed \
  --name tunemeta \
  --icon "$ROOT_DIR/src/tunemeta/assets/icon.icns" \
  --add-data "$ROOT_DIR/src/tunemeta/assets:assets" \
  --noconfirm \
  --distpath dist \
  --workpath build \
  --specpath build \
  src/tunemeta/gui.py

APP="dist/tunemeta.app"
DMG="dist/tunemeta.dmg"
STAGING="dist/dmg_staging"

rm -rf "$STAGING" "$DMG"
mkdir -p "$STAGING"
cp -R "$APP" "$STAGING/"
ln -s /Applications "$STAGING/Applications"
hdiutil create -volname "tunemeta" -srcfolder "$STAGING" -ov -format UDZO "$DMG"
rm -rf "$STAGING"

echo "Built $APP and $DMG"
