from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request

from tunemeta.models import TrackMetadata
from tunemeta.providers.base import Provider

LOOKUP_URL = "https://itunes.apple.com/lookup"
SEARCH_URL = "https://itunes.apple.com/search"

_TRACK_ID_RE = re.compile(r"[?&]i=(\d+)")
_COLLECTION_ID_RE = re.compile(r"/id(\d+)|/(\d+)(?:\?|$)")
_ARTWORK_SIZE_RE = re.compile(r"/\d+x\d+bb\.jpg$")


class ITunesProvider(Provider):
    """Looks up track metadata via Apple's public iTunes Search/Lookup API.

    No API key required. Apple informally rate-limits this endpoint
    (roughly 20 requests/minute), so it's fine for interactive use but not
    for bulk scraping.
    """

    name = "itunes"

    def lookup(self, identifier: str) -> TrackMetadata:
        result = self._fetch(self._resolve_params(identifier))
        return self._to_metadata(result)

    def artwork_url(self, metadata: TrackMetadata, size: int) -> str | None:
        if not metadata.artwork_url:
            return None
        return _ARTWORK_SIZE_RE.sub(f"/{size}x{size}bb.jpg", metadata.artwork_url)

    @staticmethod
    def _resolve_params(identifier: str) -> dict:
        identifier = identifier.strip()

        if identifier.isdigit():
            return {"id": identifier}

        if "music.apple.com" in identifier:
            track_match = _TRACK_ID_RE.search(identifier)
            if track_match:
                return {"id": track_match.group(1)}
            collection_match = _COLLECTION_ID_RE.search(identifier)
            if collection_match:
                return {"id": collection_match.group(1) or collection_match.group(2)}
            raise ValueError(f"Could not extract an ID from URL: {identifier}")

        # Not a URL or a bare ID: treat as a free-text search, take the top hit.
        return {"term": identifier, "entity": "song", "limit": "1", "_search": True}

    @staticmethod
    def _fetch(params: dict) -> dict:
        params = dict(params)
        is_search = params.pop("_search", False)
        base_url = SEARCH_URL if is_search else LOOKUP_URL
        url = base_url + "?" + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.load(resp)
        if not data.get("resultCount"):
            raise LookupError(f"No iTunes results for {params}")
        return data["results"][0]

    @staticmethod
    def _to_metadata(result: dict) -> TrackMetadata:
        year = int(result["releaseDate"][:4]) if result.get("releaseDate") else None
        return TrackMetadata(
            title=result.get("trackName"),
            artist=result.get("artistName"),
            album=result.get("collectionName"),
            album_artist=result.get("collectionArtistName") or result.get("artistName"),
            genre=result.get("primaryGenreName"),
            year=year,
            track_number=result.get("trackNumber"),
            track_total=result.get("trackCount"),
            disc_number=result.get("discNumber"),
            disc_total=result.get("discCount"),
            explicit=result.get("trackExplicitness") == "explicit",
            source_url=result.get("trackViewUrl"),
            artwork_url=result.get("artworkUrl100"),
        )
