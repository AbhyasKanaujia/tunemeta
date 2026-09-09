from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TrackMetadata:
    """Normalized track metadata, independent of which provider it came from."""

    title: str | None = None
    artist: str | None = None
    album: str | None = None
    album_artist: str | None = None
    genre: str | None = None
    year: int | None = None
    track_number: int | None = None
    track_total: int | None = None
    disc_number: int | None = None
    disc_total: int | None = None
    explicit: bool = False
    source_url: str | None = None
    artwork_url: str | None = None

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}
