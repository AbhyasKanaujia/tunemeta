from tunemeta.providers.base import Provider
from tunemeta.providers.itunes import ITunesProvider

#: Registry of available providers, keyed by the name used on the CLI (--provider).
#: New sources (MusicBrainz, Deezer, ...) register here without touching the CLI.
PROVIDERS: dict[str, Provider] = {
    "itunes": ITunesProvider(),
}

DEFAULT_PROVIDER = "itunes"

__all__ = ["Provider", "ITunesProvider", "PROVIDERS", "DEFAULT_PROVIDER"]
