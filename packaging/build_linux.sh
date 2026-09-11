#!/usr/bin/env bash
# Builds dist/tunemeta -- a single portable binary.
# Run from a Linux machine with `pip install -e ".[gui,build]"` done first.
#
# pywebview needs GTK3 + WebKit2GTK at runtime (unlike macOS/Windows, Linux
# has no OS-bundled webview). Most desktop distros already have this
# (GNOME/Ubuntu/Fedora Workstation); on a minimal system, install it first:
#   Debian/Ubuntu: sudo apt install python3-gi gir1.2-webkit2-4.1
#   Fedora:        sudo dnf install python3-gobject webkit2gtk4.1
#
# No file-manager icon here -- ELF binaries don't embed one the way .app/.exe
# do (that needs a .desktop file, out of scope for a portable binary). The
# window/taskbar icon while it's running still comes through via GTK.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

pyinstaller \
  --onefile \
  --windowed \
  --name tunemeta \
  --add-data "$ROOT_DIR/src/tunemeta/assets:assets" \
  --noconfirm \
  --distpath dist \
  --workpath build \
  --specpath build \
  src/tunemeta/gui.py

chmod +x dist/tunemeta
echo "Built dist/tunemeta"
