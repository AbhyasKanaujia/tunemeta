# Developer Log

Technical/internal notes on how this project has been built — not a
user-facing changelog. See [CHANGELOG.md](CHANGELOG.md) for what's new
from a user's perspective.

## 2026-09-12 (4)

- The v1.0.3 release (first built after c3b56d5, "Embed the version in
  release installer filenames") broke the direct download links in
  README.md and docs/index.html: they hit
  `releases/latest/download/tunemeta-macos.dmg`, but the workflow now
  only produces `tunemeta-v1.0.3-macos.dmg`, a 404. That commit renamed
  the asset instead of also keeping a plain-named copy. Fixed
  release.yml to `cp` (not `mv`) before renaming and upload both the
  versioned and plain-named file for each platform, so per-release
  filenames stay distinct *and* the stable "latest" links keep working.
  Patched the already-published v1.0.3 release by hand (downloaded the
  versioned assets, re-uploaded copies under the plain names) so it
  doesn't need a re-cut.

## 2026-09-12 (3)

- Fixed `CERTIFICATE_VERIFY_FAILED` on iTunes lookups/search and artwork
  downloads. `urlopen()` was using the interpreter's default SSL context,
  which trusts whatever root certs the OS has linked in — a link that's
  often missing, and always missing in the PyInstaller-built `.app`,
  which doesn't inherit the system keychain at all. Added `net.py` with
  a shared SSL context pinned to `certifi`'s CA bundle, and routed the
  three `urlopen` call sites (itunes.py, artwork.py, gui.py's update
  check) through it. PyInstaller already ships a hook that bundles
  certifi's `cacert.pem`, so no packaging changes were needed.

## 2026-09-12 (2)

- Added the rename-on-write checkbox and `tagging.sensible_filename()`.
  First pass nested the checkbox `<input>` inside its `<label>`, which
  broke XP.css: its checkbox skin hides the real input
  (`opacity:0; position:fixed`) and draws the box/checkmark via the
  label's `:before`/`:after`, matched with an adjacent-sibling selector
  (`input[type=checkbox]+label`) that only fires when the two are
  siblings, not parent/child. Fixed by placing them as siblings inside a
  `.field-row`, per XP.css's own convention.
- Release installers (`tunemeta-macos.dmg`, `tunemeta-windows.exe`,
  `tunemeta-linux`) had the same filename on every release, so v1.0.1 and
  v1.0.2 downloads were indistinguishable once saved to disk. Release
  builds now embed the tag (`tunemeta-v1.0.2-macos.dmg`, etc.), falling
  back to `dev` on manual `workflow_dispatch` runs that have no tag.

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
