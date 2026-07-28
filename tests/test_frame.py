from PIL import Image

from auto_shotframe.frame import FrameOptions, calculate_layout, render_frame
from auto_shotframe.metadata import PhotoMetadata

EMPTY_METADATA = PhotoMetadata(
    make=None,
    brand=None,
    camera=None,
    lens=None,
    iso=None,
    aperture=None,
    exposure_seconds=None,
    focal_length_mm=None,
)


def test_default_horizontal_layout() -> None:
    layout = calculate_layout(6000, 4000, FrameOptions())
    assert layout.canvas_width == 6240
    assert layout.canvas_height == 5040
    assert layout.image_x == 120
    assert layout.image_y == 160
    assert layout.info_height == 880


def test_default_vertical_layout() -> None:
    layout = calculate_layout(3000, 4500, FrameOptions())
    assert layout.canvas_width == 3180
    assert layout.canvas_height == 5280
    assert layout.image_x == 90
    assert layout.image_y == 120
    assert layout.info_height == 660


def test_render_frame_preserves_source_pixels_and_adds_canvas() -> None:
    source = Image.new("RGB", (200, 100), (20, 120, 200))
    result = render_frame(
        source,
        EMPTY_METADATA,
        options=FrameOptions(),
        show_logo=False,
    )
    assert result.mode == "RGB"
    assert result.size == (206, 126)
    assert result.getpixel((3, 4)) == source.getpixel((0, 0))
