"""Dev loop for the desktop app: restarts tunemeta-gui whenever source changes.

Not a true in-process hot reload (the window resets each time), but it beats
manually killing and relaunching the app after every edit. No new dependency:
just polls mtimes on a short interval.

Usage: python scripts/dev.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import time

WATCH_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src", "tunemeta"))
WATCH_EXTENSIONS = (".py", ".css")
POLL_INTERVAL_SECONDS = 0.5


def snapshot() -> dict[str, float]:
    mtimes = {}
    for root, _dirs, files in os.walk(WATCH_DIR):
        if "__pycache__" in root:
            continue
        for name in files:
            if name.endswith(WATCH_EXTENSIONS):
                path = os.path.join(root, name)
                mtimes[path] = os.path.getmtime(path)
    return mtimes


def start_app() -> subprocess.Popen:
    return subprocess.Popen([sys.executable, "-m", "tunemeta.gui"])


def main() -> None:
    last = snapshot()
    proc = start_app()
    print(f"tunemeta dev: watching {WATCH_DIR} (Ctrl+C to stop)")

    try:
        while True:
            time.sleep(POLL_INTERVAL_SECONDS)
            current = snapshot()
            if current != last:
                last = current
                print("Change detected, restarting...")
                proc.terminate()
                proc.wait()
                proc = start_app()
    except KeyboardInterrupt:
        pass
    finally:
        proc.terminate()
        proc.wait()


if __name__ == "__main__":
    main()
