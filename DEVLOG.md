# Developer Log

Technical/internal notes on how this project has been built — not a
user-facing changelog. See [CHANGELOG.md](CHANGELOG.md) for what's new
from a user's perspective.

## 2026-09-12

- Fixed the Track Info field misalignment: XP.css's `.field-row-stacked
  *+*` rule (meant to space a field's own label from its input) was also
  matching sibling field wrappers in the 2-column grid, pushing every
  second column down by its margin-top. Overrode with a more specific
  selector.
- Added version display + About dialog + Check for Updates, backed by
  `tunemeta.__version__` and the GitHub releases API.
- Added `scripts/dev.py`: restarts the desktop app on source file changes
  during development, instead of manual kill/relaunch.
- Added a test asserting `tunemeta.__version__` matches `pyproject.toml`'s
  version field, so they can't drift apart.
- Added `CHANGELOG.md` and this dev log, per AGENTS.md's Keep a Changelog
  convention (previously not being followed).
- README restructured: screenshot and download links moved near the top,
  for someone landing directly on the repo rather than the website.
- Landing page got a real demo screenshot (a genuinely public-domain/CC0
  track, tags stripped, searched, correctly re-tagged).

## 2026-09-11

- Built the desktop app from scratch (pywebview + XP.css): staged flow
  (choose file -> search -> review -> write), a "current tags" preview
  before overwriting, file size/artwork dimensions shown.
- Packaging: PyInstaller build scripts for macOS/Windows/Linux;
  `.github/workflows/release.yml` builds and attaches installers to
  every GitHub release.
- App icon generated (.icns/.ico/.png), padded to match macOS icon
  conventions, wired into dock/taskbar/title bar and the packaged
  installers.
- macOS DMG uses `create-dmg` for a real drag-to-Applications layout
  instead of a bare volume.
- GitHub Pages landing page, issue templates (bug report/feature
  request), CONTRIBUTING.md.
- Tagged and released v1.0.0. Found the release workflow's default
  `GITHUB_TOKEN` lacked write access (uploads were silently 403'ing
  even though builds succeeded) and fixed it with an explicit
  `permissions: contents: write`.
