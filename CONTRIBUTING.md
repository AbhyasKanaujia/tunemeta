# Contributing

## Report a bug

Open a [bug report](https://github.com/AbhyasKanaujia/tunemeta/issues/new?template=bug_report.yml). Include whether you hit it in the desktop app or the CLI, your OS, and the exact steps.

## Request a feature

Open a [feature request](https://github.com/AbhyasKanaujia/tunemeta/issues/new?template=feature_request.yml) describing the problem you're trying to solve, not just the solution.

## Contribute code

1. Fork the repo and clone it.
2. `pip install -e ".[dev,gui]"` (add `,build` too if you want to test packaging).
3. Make your change.
4. Run the tests: `pytest -v`.
5. If you touched the desktop app, actually launch it (`tunemeta-gui` or `python -m tunemeta.gui`) and click through the change — the test suite doesn't cover the UI.
6. Open a pull request explaining what the change does and why.

### Where things live

- `src/tunemeta/providers/` — metadata sources. Each provider implements `lookup()` and `artwork_url()` (see `providers/base.py`); adding a new one (MusicBrainz, Deezer, ...) is a new file plus one line in `providers/__init__.py`, no CLI or tagging code changes needed.
- `src/tunemeta/tagging.py` / `artwork.py` — reading/writing ID3 tags and cover art.
- `src/tunemeta/cli.py` — the `tunemeta` command line tool.
- `src/tunemeta/gui.py` — the desktop app (pywebview + XP.css).
- `packaging/` — PyInstaller build scripts for macOS/Windows/Linux; `.github/workflows/release.yml` runs them on every GitHub release.

### Adding a provider

The provider interface is intentionally small — `lookup(identifier) -> TrackMetadata` and `artwork_url(metadata, size) -> str | None`. Look at `providers/itunes.py` for a working example, and check `tests/test_itunes_provider.py` for the pattern tests follow.
