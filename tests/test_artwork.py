import io

from PIL import Image

from tunemeta.artwork import MAX_REASONABLE_SIZE, resize_jpeg


def _make_png(size):
    img = Image.new("RGB", size, color=(200, 50, 50))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_resize_jpeg_downscales_to_requested_size():
    source = _make_png((2000, 2000))
    result = resize_jpeg(source, 500)
    with Image.open(io.BytesIO(result)) as img:
        assert img.format == "JPEG"
        assert img.width == 500
        assert img.height == 500


def test_resize_jpeg_never_upscales():
    source = _make_png((300, 300))
    result = resize_jpeg(source, 1000)
    with Image.open(io.BytesIO(result)) as img:
        assert img.width == 300
        assert img.height == 300


def test_resize_jpeg_clamps_to_max_reasonable_size():
    source = _make_png((4000, 4000))
    result = resize_jpeg(source, 4000)
    with Image.open(io.BytesIO(result)) as img:
        assert img.width == MAX_REASONABLE_SIZE
        assert img.height == MAX_REASONABLE_SIZE
