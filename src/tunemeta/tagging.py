from __future__ import annotations

from mutagen.id3 import APIC, ID3, ID3NoHeaderError, TALB, TCON, TDRC, TIT2, TPE1, TPE2, TPOS, TRCK

from tunemeta.models import TrackMetadata


def write_tags(path: str, metadata: TrackMetadata, artwork_jpeg: bytes | None = None) -> None:
    """Write normalized metadata (and optional cover art) into an MP3's ID3v2 tag.

    Replaces existing text frames for the fields we know about; frames for
    fields tunemeta doesn't touch (comments, lyrics, custom frames, ...) are
    left alone. Passing artwork_jpeg replaces any existing embedded picture.
    """
    try:
        tags = ID3(path)
    except ID3NoHeaderError:
        tags = ID3()

    if metadata.title:
        tags.setall("TIT2", [TIT2(encoding=3, text=metadata.title)])
    if metadata.artist:
        tags.setall("TPE1", [TPE1(encoding=3, text=metadata.artist)])
    if metadata.album:
        tags.setall("TALB", [TALB(encoding=3, text=metadata.album)])
    if metadata.album_artist:
        tags.setall("TPE2", [TPE2(encoding=3, text=metadata.album_artist)])
    if metadata.genre:
        tags.setall("TCON", [TCON(encoding=3, text=metadata.genre)])
    if metadata.year:
        tags.setall("TDRC", [TDRC(encoding=3, text=str(metadata.year))])
    if metadata.track_number:
        track = str(metadata.track_number)
        if metadata.track_total:
            track += f"/{metadata.track_total}"
        tags.setall("TRCK", [TRCK(encoding=3, text=track)])
    if metadata.disc_number:
        disc = str(metadata.disc_number)
        if metadata.disc_total:
            disc += f"/{metadata.disc_total}"
        tags.setall("TPOS", [TPOS(encoding=3, text=disc)])

    if artwork_jpeg is not None:
        tags.setall(
            "APIC",
            [
                APIC(
                    encoding=3,
                    mime="image/jpeg",
                    type=3,  # front cover
                    desc="cover",
                    data=artwork_jpeg,
                )
            ],
        )

    tags.save(path, v2_version=3)
