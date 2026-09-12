# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Version number and an "About tunemeta" dialog in the desktop app, with a
  "Check for Updates" button that compares against the latest GitHub release.
- `scripts/dev.py`: restarts the desktop app automatically on source changes.
- Test asserting `tunemeta.__version__` matches `pyproject.toml`.

### Fixed
- Track Info fields (Title/Artist, Album/Album Artist, ...) were misaligned
  by 6px in the second column — an XP.css rule meant to space a field's own
  label from its input was also matching sibling field wrappers.
- Release workflow's `GITHUB_TOKEN` lacked write access, so `gh release
  upload` was silently failing (403) even though builds succeeded.

### Changed
- README's example output no longer names a real copyrighted song.

## [1.0.0] - 2026-09-11

### Added
- CLI: `tunemeta info` / `art` / `tag` commands, iTunes provider, sensible
  cover art resizing (never upscales, capped at a sane max size).
- Desktop app (macOS/Windows/Linux) built with pywebview: pick a file, see
  what's already tagged before overwriting it, search, review, write.
- Packaging: PyInstaller builds for all three platforms, with a GitHub
  Actions workflow that builds and attaches installers to every release.
- App icon, embedded in the dock/taskbar/title bar and the packaged
  installers.
- GitHub Pages landing page with OS-aware download buttons pointing at
  the latest release.
- Issue templates (bug report, feature request) and `CONTRIBUTING.md`.
