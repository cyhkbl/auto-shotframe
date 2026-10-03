from PIL import Image

from auto_shotframe.frame import (
    FrameOptions,
    calculate_layout,
    fit_source_dimensions,
    render_frame,
)
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
    assert layout.canvas_width == 6840
    assert layout.canvas_height == 5400
    assert layout.image_x == 420
    assert layout.image_y == 520
    assert layout.info_height == 880
    assert layout.corner_radius == 160


def test_default_vertical_layout() -> None:
    layout = calculate_layout(3000, 4500, FrameOptions())
    assert layout.canvas_width == 3630
    assert layout.canvas_height == 5550
    assert layout.image_x == 315
    assert layout.image_y == 390
    assert layout.info_height == 660


def test_corner_radius_is_clamped_to_half_the_photo() -> None:
    layout = calculate_layout(40, 20, FrameOptions(corner_radius=0.9))
    assert layout.corner_radius == 10


def test_zero_corner_radius_keeps_square_corners() -> None:
    source = Image.new("RGB", (200, 100), (20, 120, 200))
    options = FrameOptions(
        corner_radius=0,
        blur=0,
        darken=0,
        shadow_blur=0,
        shadow_offset=0,
    )
    result = render_frame(source, EMPTY_METADATA, options=options, show_logo=False)
    layout = calculate_layout(200, 100, options)

    assert result.getpixel((layout.image_x, layout.image_y)) == (20, 120, 200)


def test_rounded_corners_expose_the_background() -> None:
    source = Image.new("RGB", (600, 400), (250, 250, 250))
    options = FrameOptions(
        corner_radius=0.05,
        blur=0,
        darken=1.0,
        shadow_blur=0,
        shadow_offset=0,
    )
    result = render_frame(source, EMPTY_METADATA, options=options, show_logo=False)
    layout = calculate_layout(600, 400, options)
    assert layout.corner_radius > 0

    # The extreme corner of the photo area is cut away and shows the darkened
    # background; a point past the radius keeps the original photo pixel.
    corner = result.getpixel((layout.image_x, layout.image_y))
    inset = layout.corner_radius + 3
    inside = result.getpixel((layout.image_x + inset, layout.image_y + inset))

    assert sum(corner) < sum(inside)
    assert inside == (250, 250, 250)


def test_render_frame_preserves_source_pixels_and_adds_canvas() -> None:
    source = Image.new("RGB", (200, 100), (20, 120, 200))
    options = FrameOptions()
    result = render_frame(
        source,
        EMPTY_METADATA,
        options=options,
        show_logo=False,
    )
    layout = calculate_layout(200, 100, options)

    assert result.mode == "RGB"
    assert result.size == (220, 135)
    # Sample past the rounded corner, where the pixel still belongs to the photo.
    inset = layout.corner_radius + 2
    assert (
        result.getpixel((layout.image_x + inset, layout.image_y + inset))
        == source.getpixel((0, 0))
    )


def test_fit_source_dimensions_limits_landscape_final_canvas() -> None:
    size = fit_source_dimensions(6000, 4000, FrameOptions(), max_long_edge=2160)
    layout = calculate_layout(*size, FrameOptions())

    assert size[0] < 6000
    assert max(layout.canvas_width, layout.canvas_height) == 2160


def test_fit_source_dimensions_limits_portrait_final_canvas() -> None:
    size = fit_source_dimensions(3000, 4500, FrameOptions(), max_long_edge=2160)
    layout = calculate_layout(*size, FrameOptions())

    assert size[1] < 4500
    assert max(layout.canvas_width, layout.canvas_height) == 2160


def test_fit_source_dimensions_does_not_upscale_small_photo() -> None:
    assert fit_source_dimensions(
        800,
        600,
        FrameOptions(),
        max_long_edge=2160,
    ) == (800, 600)
