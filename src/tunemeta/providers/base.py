from __future__ import annotations

from abc import ABC, abstractmethod

from tunemeta.models import TrackMetadata


class Provider(ABC):
    """A metadata source that can resolve an identifier to a TrackMetadata.

    Implement this to add a new source (MusicBrainz, Deezer, ...): it's the
    only interface the CLI depends on, so a new provider is a new file plus
    one line in providers/__init__.py's PROVIDERS registry.
    """

    #: Short name used to select this provider on the CLI, e.g. "itunes".
    name: str

    @abstractmethod
    def lookup(self, identifier: str) -> TrackMetadata:
        """Resolve a URL, ID, or free-text query to normalized track metadata.

        Raises LookupError if nothing matches.
        """
        raise NotImplementedError

    @abstractmethod
    def artwork_url(self, metadata: TrackMetadata, size: int) -> str | None:
        """Return an artwork URL for the given metadata sized to `size` px, if available."""
        raise NotImplementedError
