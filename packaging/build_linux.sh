#!/usr/bin/env bash
# Builds dist/tunemeta -- a single portable binary.
# Run from a Linux machine with `pip install -e ".[gui,build]"` done first.
#
# pywebview needs GTK3 + WebKit2GTK at runtime (unlike macOS/Windows, Linux
# has no OS-bundled webview). Most desktop distros already have this
# (GNOME/Ubuntu/Fedora Workstation); on a minimal system, install it first:
#   Debian/Ubuntu: sudo apt install python3-gi gir1.2-webkit2-4.1
#   Fedora:        sudo dnf install python3-gobject webkit2gtk4.1
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

pyinstaller \
  --onefile \
  --windowed \
  --name tunemeta \
  --noconfirm \
  --distpath dist \
  --workpath build \
  --specpath build \
  src/tunemeta/gui.py

chmod +x dist/tunemeta
echo "Built dist/tunemeta"
