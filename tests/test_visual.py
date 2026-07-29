from PIL import Image, ImageDraw, ImageStat

from auto_shotframe.branding import normalize_manufacturer
from auto_shotframe.frame import (
    FrameOptions,
    _fit_font,
    _tracked_text_length,
    calculate_layout,
    render_frame,
)
from auto_shotframe.metadata import PhotoMetadata


def test_reference_style_visual_ranges() -> None:
    source = Image.new("RGB", (600, 400))
    pixels = source.load()
    for y in range(source.height):
        for x in range(source.width):
            pixels[x, y] = (
                round(20 + 90 * x / source.width),
                round(70 + 100 * y / source.height),
                round(170 - 60 * y / source.height),
            )

    metadata = PhotoMetadata(
        make="NIKON CORPORATION",
        brand=normalize_manufacturer("NIKON CORPORATION"),
        camera="NIKON Z 50",
        lens="NIKKOR Z DX 50-250mm f/4.5-6.3 VR",
        iso=100,
        aperture=5.6,
        exposure_seconds=1 / 500,
        focal_length_mm=150,
    )
    framed = render_frame(source, metadata, options=FrameOptions())

    assert framed.size == (624, 504)
    assert framed.getpixel((12, 16)) == source.getpixel((0, 0))

    info = framed.crop((0, 416, 624, 504))
    extrema = ImageStat.Stat(info).extrema
    assert max(channel[1] - channel[0] for channel in extrema) > 150


def test_jost_tracking_is_included_in_fit_width() -> None:
    canvas = Image.new("RGB", (400, 100))
    draw = ImageDraw.Draw(canvas)
    text = "Shot on iPhone 17 Pro"
    font, tracking = _fit_font(
        draw,
        text,
        max_width=220,
        start_size=30,
        min_size=10,
        weight=300,
        tracking_ratio=0.04,
    )

    assert tracking == round(font.size * 0.04)
    assert _tracked_text_length(draw, text, font=font, tracking=tracking) <= 220


def test_opaque_text_has_no_dark_stroke_pixels() -> None:
    source = Image.new("RGB", (600, 400), "white")
    metadata = PhotoMetadata(
        make=None,
        brand=None,
        camera="TEST CAMERA",
        lens=None,
        iso=None,
        aperture=None,
        exposure_seconds=None,
        focal_length_mm=None,
    )
    options = FrameOptions(
        blur=0,
        darken=0,
        shadow_blur=0,
        shadow_offset=0,
    )

    framed = render_frame(source, metadata, options=options, show_logo=False)
    layout = calculate_layout(*source.size, options)
    info = framed.crop(
        (
            0,
            layout.info_y + 2,
            layout.canvas_width,
            layout.canvas_height,
        )
    )
    darkest_channel = min(channel[0] for channel in ImageStat.Stat(info).extrema)

    assert darkest_channel >= 245
    assert darkest_channel < 255
