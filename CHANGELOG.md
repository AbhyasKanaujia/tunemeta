# Changelog

All notable changes to this project are documented in this file, from a
user's point of view. For technical/internal details, see [DEVLOG.md](DEVLOG.md).

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- The app now shows its version number, with an About window and a
  "Check for Updates" button.

### Fixed
- Some fields in the Track Info section (Title/Artist, Album/Album
  Artist, Genre/Year, Track #/Disc #) were slightly misaligned.

## [1.0.0] - 2026-09-11

### Added
- Desktop app for macOS, Windows, and Linux: pick an MP3, see what's
  already tagged on it, search for the correct track, review the
  result, and write it.
- Command-line tool: `tunemeta info`, `tunemeta art`, `tunemeta tag`.
- Cover art is resized sensibly when embedded instead of bloating the
  file with an oversized image.
- App icon.
