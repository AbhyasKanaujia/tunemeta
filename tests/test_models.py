from tunemeta.models import TrackMetadata


def test_to_dict_includes_all_fields():
    metadata = TrackMetadata(title="Song", artist="Artist", year=2024)
    data = metadata.to_dict()
    assert data["title"] == "Song"
    assert data["artist"] == "Artist"
    assert data["year"] == 2024
    assert data["album"] is None
