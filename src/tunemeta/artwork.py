from __future__ import annotations

import io
import urllib.request

from PIL import Image

MAX_REASONABLE_SIZE = 1200  # embedding larger than this bloats file size for little visible gain


def fetch(url: str) -> bytes:
    """Download raw image bytes from a URL."""
    with urllib.request.urlopen(url, timeout=15) as resp:
        return resp.read()


def resize_jpeg(image_bytes: bytes, size: int, quality: int = 85) -> bytes:
    """Re-encode image bytes as a square JPEG at most `size` px per side.

    Never upscales past the source's native resolution, and clamps to
    MAX_REASONABLE_SIZE to keep embedded artwork from ballooning file size
    (a 3000x3000 cover can add several MB to a small MP3 for no audible or
    visible benefit at typical playback UI sizes).
    """
    size = min(size, MAX_REASONABLE_SIZE)
    with Image.open(io.BytesIO(image_bytes)) as img:
        img = img.convert("RGB")
        target = min(size, max(img.width, img.height))
        img.thumbnail((target, target), Image.LANCZOS)
        out = io.BytesIO()
        img.save(out, format="JPEG", quality=quality)
        return out.getvalue()
