from mutagen.id3 import ID3

from tunemeta.models import TrackMetadata
from tunemeta.tagging import read_tags, sensible_filename, write_tags


def test_write_tags_sets_expected_frames(tmp_path):
    mp3_path = tmp_path / "song.mp3"
    mp3_path.write_bytes(b"")  # ID3v2 tags can be written regardless of audio content

    metadata = TrackMetadata(
        title="...Baby One More Time (from Kung Fu Panda 4)",
        artist="Tenacious D",
        album="Kung Fu Panda 4 (Original Motion Picture Soundtrack)",
        album_artist="Hans Zimmer & Steve Mazzaro",
        genre="Soundtrack",
        year=2024,
        track_number=22,
        track_total=22,
        disc_number=1,
        disc_total=1,
    )

    write_tags(str(mp3_path), metadata, artwork_jpeg=b"\xff\xd8\xff\xd9")  # minimal JPEG marker bytes

    tags = ID3(str(mp3_path))
    assert tags["TIT2"].text == ["...Baby One More Time (from Kung Fu Panda 4)"]
    assert tags["TPE1"].text == ["Tenacious D"]
    assert tags["TALB"].text == ["Kung Fu Panda 4 (Original Motion Picture Soundtrack)"]
    assert tags["TPE2"].text == ["Hans Zimmer & Steve Mazzaro"]
    assert tags["TCON"].text == ["Soundtrack"]
    assert tags["TRCK"].text == ["22/22"]
    assert tags["TPOS"].text == ["1/1"]
    assert tags["APIC:cover"].data == b"\xff\xd8\xff\xd9"


def test_write_tags_skips_missing_fields(tmp_path):
    mp3_path = tmp_path / "song.mp3"
    mp3_path.write_bytes(b"")

    write_tags(str(mp3_path), TrackMetadata(title="Only Title"))

    tags = ID3(str(mp3_path))
    assert tags["TIT2"].text == ["Only Title"]
    assert "TPE1" not in tags
    assert "APIC:cover" not in tags


def test_write_tags_preserves_unrelated_existing_frames(tmp_path):
    from mutagen.id3 import TCOM

    mp3_path = tmp_path / "song.mp3"
    mp3_path.write_bytes(b"")

    tags = ID3()
    tags.setall("TCOM", [TCOM(encoding=3, text="Max Martin")])
    tags.save(str(mp3_path), v2_version=3)

    write_tags(str(mp3_path), TrackMetadata(title="New Title"))

    tags = ID3(str(mp3_path))
    assert tags["TIT2"].text == ["New Title"]
    assert tags["TCOM"].text == ["Max Martin"]


def test_read_tags_returns_empty_dict_when_untagged(tmp_path):
    mp3_path = tmp_path / "song.mp3"
    mp3_path.write_bytes(b"")

    assert read_tags(str(mp3_path)) == {}


def test_read_tags_reflects_what_write_tags_wrote(tmp_path):
    mp3_path = tmp_path / "song.mp3"
    mp3_path.write_bytes(b"")

    metadata = TrackMetadata(
        title="Faasle",
        artist="Aditya Rikhari",
        album="Faasle - Single",
        album_artist="Aditya Rikhari",
        genre="Indian",
        year=2021,
        track_number=1,
        track_total=1,
        disc_number=1,
        disc_total=1,
    )
    write_tags(str(mp3_path), metadata)

    assert read_tags(str(mp3_path)) == {
        "title": "Faasle",
        "artist": "Aditya Rikhari",
        "album": "Faasle - Single",
        "album_artist": "Aditya Rikhari",
        "genre": "Indian",
        "year": "2021",
        "track_number": "1",
        "disc_number": "1",
    }


def test_sensible_filename_combines_artist_and_title():
    metadata = TrackMetadata(title="Faasle", artist="Aditya Rikhari")
    assert sensible_filename(metadata, ".mp3") == "Aditya Rikhari - Faasle.mp3"


def test_sensible_filename_falls_back_to_whatever_is_present():
    assert sensible_filename(TrackMetadata(title="Faasle"), ".mp3") == "Faasle.mp3"
    assert sensible_filename(TrackMetadata(artist="Aditya Rikhari"), ".mp3") == "Aditya Rikhari.mp3"
    assert sensible_filename(TrackMetadata(), ".mp3") == "Untitled.mp3"


def test_sensible_filename_strips_invalid_characters():
    metadata = TrackMetadata(title="Why? / How.", artist="AC/DC")
    assert sensible_filename(metadata, ".mp3") == "ACDC - Why How.mp3"
