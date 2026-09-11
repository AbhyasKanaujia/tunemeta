#!/usr/bin/env bash
# Builds dist/tunemeta.app and wraps it in dist/tunemeta.dmg.
# Run from a macOS machine with `pip install -e ".[gui,build]"` and
# `brew install create-dmg` done first.
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

create-dmg \
  --volname "tunemeta" \
  --volicon "$ROOT_DIR/src/tunemeta/assets/icon.icns" \
  --background "$ROOT_DIR/packaging/dmg_background.png" \
  --window-pos 200 120 \
  --window-size 660 400 \
  --icon-size 100 \
  --icon "tunemeta.app" 180 170 \
  --hide-extension "tunemeta.app" \
  --app-drop-link 480 170 \
  --no-internet-enable \
  "$DMG" \
  "$STAGING"

rm -rf "$STAGING"

echo "Built $APP and $DMG"
