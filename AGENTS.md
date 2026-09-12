# AGENTS.md

- Env: use the project's `.venv` (`source .venv/bin/activate`). Don't install
  packages globally.
- Test: `pytest -v`. CI runs this on Python 3.9, 3.11, 3.13 — keep changes
  compatible with 3.9.
- No linter/formatter is configured; match existing style.
- Layout: CLI entry is `src/tunemeta/cli.py`. Metadata sources are
  **providers** (`src/tunemeta/providers/`), each implementing
  `lookup(identifier)` and `artwork_url(metadata, size)` per
  `providers/base.py`. Tagging/writing logic is in `tagging.py`, artwork
  resizing in `artwork.py`.
- Adding a provider: implement the interface in `providers/base.py`, register
  it, don't touch CLI or tagging code.
- Tests live in `tests/`, one file per module — add tests alongside code
  changes.
- Keep `CHANGELOG.md` up to date in line with `https://keepachangelog.com/en/1.1.0/`.
  It's user-facing ("what's new"), not a dev log — no internal/technical
  details (bug root causes, CI fixes, refactors). Put those in `DEVLOG.md`
  instead.
- Don't try to take screenshots ot automate UI testing with throwaway scripts, ask user to validate by providing a manual test. Just resart the app so that your changes take effect.

## Using the CLI to fix a file's tags

1. `tunemeta info "<query>"` first — never `tag` blind. Confirm title/artist
   match the file (check duration against the track length if unsure).
2. If the free-text search finds nothing or the wrong track, find the exact
   Apple Music song URL (web search) and pass that as the identifier instead
   of guessing at search terms.
3. `tunemeta tag <file> "<identifier>"` to write it. Use `--art-size` to
   control embedded cover size/file size (default 800px; drop to ~300 for a
   much smaller file) and `--no-art` to skip artwork entirely.
4. Rename the file to `Artist - Title.mp3` after tagging, using the tag
   values actually written (not the original filename).
