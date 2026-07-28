from PIL import Image, ImageStat

from auto_shotframe.branding import normalize_manufacturer
from auto_shotframe.frame import FrameOptions, render_frame
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
