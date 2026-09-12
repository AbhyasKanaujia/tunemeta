from __future__ import annotations

import re

from mutagen.id3 import APIC, ID3, ID3NoHeaderError, TALB, TCON, TDRC, TIT2, TPE1, TPE2, TPOS, TRCK

from tunemeta.models import TrackMetadata

_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


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


def read_tags(path: str) -> dict:
    """Read the ID3 tags currently on a file, for display only.

    Mirrors the frames write_tags() writes (TIT2/TPE1/TALB/TPE2/TCON/TDRC/
    TRCK/TPOS) so "current tags" reflects exactly what this tool would
    overwrite. Frames that aren't present are simply absent from the result.
    """
    try:
        tags = ID3(path)
    except ID3NoHeaderError:
        return {}

    def text(frame_id: str) -> str | None:
        frame = tags.get(frame_id)
        return str(frame.text[0]) if frame and frame.text else None

    simple_frames = (
        ("TIT2", "title"),
        ("TPE1", "artist"),
        ("TALB", "album"),
        ("TPE2", "album_artist"),
        ("TCON", "genre"),
    )
    result: dict[str, str] = {}
    for frame_id, key in simple_frames:
        value = text(frame_id)
        if value is not None:
            result[key] = value
    if (value := text("TDRC")) is not None:
        result["year"] = value.split("-")[0]
    if (value := text("TRCK")) is not None:
        result["track_number"] = value.split("/")[0]
    if (value := text("TPOS")) is not None:
        result["disc_number"] = value.split("/")[0]
    return result


def sensible_filename(metadata: TrackMetadata, extension: str) -> str:
    """Build an "Artist - Title<extension>" filename from metadata.

    Falls back to whichever of artist/title is present, or "Untitled" if
    neither is. Characters invalid in filenames on Windows/macOS/Linux are
    stripped rather than replaced, to keep the result readable.
    """
    parts = [part for part in (metadata.artist, metadata.title) if part]
    name = " - ".join(parts) if parts else "Untitled"
    name = _INVALID_FILENAME_CHARS.sub("", name)
    name = re.sub(r"\s+", " ", name).strip(" .") or "Untitled"
    return f"{name}{extension}"


def read_artwork(path: str) -> tuple[bytes, str] | None:
    """Read the cover art currently embedded on a file, if any."""
    try:
        tags = ID3(path)
    except ID3NoHeaderError:
        return None
    frames = tags.getall("APIC")
    if not frames:
        return None
    return frames[0].data, frames[0].mime or "image/jpeg"
