# tunemeta

[![CI](https://github.com/AbhyasKanaujia/tunemeta/actions/workflows/ci.yml/badge.svg)](https://github.com/AbhyasKanaujia/tunemeta/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Look up clean, accurate ID3 metadata and cover art for a song — by URL, ID,
or just a search — and write it straight into your MP3s.

Born out of a real annoyance: MP3s downloaded from random sites often carry
garbage tags (`Artist: SomeChannel - Topic`, blank comments, low-res or
oversized cover art). `tunemeta` looks the track up against a real catalog
and fixes it in one command.

```
$ tunemeta info "https://music.apple.com/us/song/baby-one-more-time-from-kung-fu-panda-4/1732596519"
{
  "title": "...Baby One More Time (from Kung Fu Panda 4)",
  "artist": "Tenacious D",
  "album": "Kung Fu Panda 4 (Original Motion Picture Soundtrack)",
  "album_artist": "Hans Zimmer & Steve Mazzaro",
  "genre": "Soundtrack",
  "year": 2024,
  ...
  "artwork_url": "https://.../1000x1000bb.jpg"
}
```

## Install

Not on PyPI yet — install straight from GitHub:

```
pip install git+https://github.com/AbhyasKanaujia/tunemeta.git
```

Or from a local clone:

```
git clone https://github.com/AbhyasKanaujia/tunemeta.git
cd tunemeta
pip install -e .
```

## Usage

**Print cleaned-up metadata as JSON:**

```
tunemeta info <url-or-id-or-search-text>
```

**Download cover art:**

```
tunemeta art <url-or-id-or-search-text> -o cover.jpg --size 1000
```

**Tag a local MP3 file directly** (looks the track up, writes ID3 tags and
embeds resized cover art in one step):

```
tunemeta tag song.mp3 <url-or-id-or-search-text>
```

Run `tunemeta <command> --help` for all options (artwork size, skipping
cover art, choosing a provider).

## Why not just embed the biggest cover art available?

Source artwork can be 3000x3000 or larger. Embedding it as-is can more than
double the size of a typical MP3 for no perceptible benefit in a player UI.
`tunemeta` re-encodes to a sensible size (800px by default when tagging) and
never upscales past the source's native resolution.

## Design

Metadata comes from pluggable **providers** (`src/tunemeta/providers/`).
Each provider implements a small interface — `lookup(identifier)` and
`artwork_url(metadata, size)` — so adding a new source doesn't touch the CLI
or tagging code. Only one ships today:

- **iTunes** — Apple's public, unauthenticated Search/Lookup API.

## Roadmap

- [x] iTunes provider
- [ ] MusicBrainz + Cover Art Archive provider (fully open, no API key)
- [ ] Deezer provider
- [ ] Last.fm provider (genre/tag data)
- [ ] `--provider` fallback chain (try multiple sources, take the first hit)
- [ ] Batch mode (tag a whole folder at once)

Have a source you'd like to see, or want to add one yourself? Open an issue
or a PR — the provider interface in `src/tunemeta/providers/base.py` is the
place to start.

## License

MIT — see [LICENSE](LICENSE).
