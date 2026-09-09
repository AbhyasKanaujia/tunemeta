from unittest.mock import patch

import pytest

from tunemeta.providers.itunes import ITunesProvider

SAMPLE_RESULT = {
    "trackName": "...Baby One More Time (from Kung Fu Panda 4)",
    "artistName": "Tenacious D",
    "collectionName": "Kung Fu Panda 4 (Original Motion Picture Soundtrack)",
    "collectionArtistName": "Hans Zimmer & Steve Mazzaro",
    "primaryGenreName": "Soundtrack",
    "releaseDate": "2024-03-08T12:00:00Z",
    "trackNumber": 22,
    "trackCount": 22,
    "discNumber": 1,
    "discCount": 1,
    "trackExplicitness": "notExplicit",
    "trackViewUrl": "https://music.apple.com/us/album/x/1732595908?i=1732596519",
    "artworkUrl100": "https://is1-ssl.mzstatic.com/image/thumb/x/774.jpg/100x100bb.jpg",
}


@pytest.mark.parametrize(
    "identifier,expected_params",
    [
        ("1732596519", {"id": "1732596519"}),
        (
            "https://music.apple.com/us/song/x/1732595908?i=1732596519&uo=4",
            {"id": "1732596519"},
        ),
        ("baby one more time tenacious d", {"term": "baby one more time tenacious d", "entity": "song", "limit": "1", "_search": True}),
    ],
)
def test_resolve_params(identifier, expected_params):
    assert ITunesProvider._resolve_params(identifier) == expected_params


def test_lookup_maps_fields():
    provider = ITunesProvider()
    with patch.object(provider, "_fetch", return_value=SAMPLE_RESULT):
        metadata = provider.lookup("1732596519")

    assert metadata.title == "...Baby One More Time (from Kung Fu Panda 4)"
    assert metadata.artist == "Tenacious D"
    assert metadata.album == "Kung Fu Panda 4 (Original Motion Picture Soundtrack)"
    assert metadata.album_artist == "Hans Zimmer & Steve Mazzaro"
    assert metadata.genre == "Soundtrack"
    assert metadata.year == 2024
    assert metadata.track_number == 22
    assert metadata.disc_total == 1
    assert metadata.explicit is False


def test_lookup_raises_when_no_results():
    provider = ITunesProvider()
    with patch.object(provider, "_fetch", side_effect=LookupError("No iTunes results for {}")):
        with pytest.raises(LookupError):
            provider.lookup("0000000000")


def test_artwork_url_resizes():
    provider = ITunesProvider()
    with patch.object(provider, "_fetch", return_value=SAMPLE_RESULT):
        metadata = provider.lookup("1732596519")
    assert provider.artwork_url(metadata, 800) == "https://is1-ssl.mzstatic.com/image/thumb/x/774.jpg/800x800bb.jpg"


def test_artwork_url_none_when_missing():
    provider = ITunesProvider()
    result = dict(SAMPLE_RESULT)
    result["artworkUrl100"] = None
    with patch.object(provider, "_fetch", return_value=result):
        metadata = provider.lookup("1732596519")
    assert provider.artwork_url(metadata, 800) is None
