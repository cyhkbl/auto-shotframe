from pathlib import Path

import piexif
import pytest
from PIL import Image, ImageCms

from auto_shotframe.cli import _read_exif_bytes, _resolved_quality, build_parser, main
from auto_shotframe.frame import FrameOptions, calculate_layout


def create_jpeg(
    path: Path,
    color: tuple[int, int, int],
    size: tuple[int, int] = (160, 100),
) -> None:
    exif = piexif.dump(
        {
            "0th": {
                piexif.ImageIFD.Make: b"SONY",
                piexif.ImageIFD.Model: b"ILCE-7M4",
            },
            "Exif": {
                piexif.ExifIFD.ISOSpeedRatings: 200,
                piexif.ExifIFD.FNumber: (28, 10),
                piexif.ExifIFD.ExposureTime: (1, 250),
                piexif.ExifIFD.FocalLength: (50, 1),
            },
            "GPS": {},
            "1st": {},
            "thumbnail": None,
        }
    )
    Image.new("RGB", size, color).save(path, exif=exif)


def create_apple_heic(path: Path) -> None:
    exif = piexif.dump(
        {
            "0th": {
                piexif.ImageIFD.Make: b"Apple",
                piexif.ImageIFD.Model: b"iPhone 17 Pro",
            },
            "Exif": {
                piexif.ExifIFD.LensModel: b"iPhone 17 Pro back triple camera",
                piexif.ExifIFD.ISOSpeedRatings: 64,
                piexif.ExifIFD.FNumber: (18, 10),
                piexif.ExifIFD.ExposureTime: (1, 120),
                piexif.ExifIFD.FocalLength: (24, 5),
            },
            "GPS": {
                piexif.GPSIFD.GPSLatitudeRef: b"N",
                piexif.GPSIFD.GPSLatitude: ((31, 1), (14, 1), (0, 1)),
            },
            "1st": {},
            "thumbnail": None,
        }
    )
    Image.new("RGB", (160, 100), (35, 95, 150)).save(path, format="HEIF", exif=exif)


def create_tiff(
    path: Path,
    image: Image.Image | None = None,
    *,
    orientation: int = 1,
    icc_profile: bytes | None = None,
) -> None:
    exif = piexif.dump(
        {
            "0th": {
                piexif.ImageIFD.Make: b"NIKON CORPORATION",
                piexif.ImageIFD.Model: b"NIKON Z 8",
                piexif.ImageIFD.Orientation: orientation,
            },
            "Exif": {
                piexif.ExifIFD.ISOSpeedRatings: 500,
                piexif.ExifIFD.FNumber: (56, 10),
                piexif.ExifIFD.ExposureTime: (1, 1600),
                piexif.ExifIFD.FocalLength: (16, 1),
            },
            "GPS": {
                piexif.GPSIFD.GPSLatitudeRef: b"N",
                piexif.GPSIFD.GPSLatitude: ((31, 1), (14, 1), (0, 1)),
            },
            "1st": {},
            "thumbnail": None,
        }
    )
    source = image or Image.new("RGB", (160, 100), (35, 95, 150))
    source.save(
        path,
        format="TIFF",
        compression="raw",
        exif=exif,
        icc_profile=icc_profile,
    )


def test_single_file_cli_creates_sibling_and_preserves_source(tmp_path: Path) -> None:
    source = tmp_path / "photo.jpg"
    create_jpeg(source, (10, 80, 160))
    original_bytes = source.read_bytes()

    assert main([str(source), "--no-logo"]) == 0
    output = tmp_path / "photo_framed.jpg"
    assert output.is_file()
    assert source.read_bytes() == original_bytes

    with Image.open(output) as framed:
        assert framed.size == (166, 126)
        cleaned = piexif.load(framed.info["exif"])
        assert cleaned["GPS"] == {}


@pytest.mark.parametrize("suffix", [".TIF", ".tiff"])
def test_tiff_ifd_metadata_orientation_and_privacy(
    tmp_path: Path,
    suffix: str,
) -> None:
    source = tmp_path / f"oriented{suffix}"
    pixels = Image.new("RGB", (80, 60), "red")
    pixels.paste("blue", (40, 0, 80, 60))
    icc_profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    create_tiff(source, pixels, orientation=6, icc_profile=icc_profile)
    original_bytes = source.read_bytes()

    with Image.open(source) as opened:
        opened.load()
        assert opened.info.get("exif") is None
        recovered = piexif.load(_read_exif_bytes(opened))
        assert recovered["0th"][piexif.ImageIFD.Make] == b"NIKON CORPORATION"
        assert recovered["Exif"][piexif.ExifIFD.ISOSpeedRatings] == 500
        assert recovered["GPS"]

    assert main([str(source), "--no-logo"]) == 0
    output = tmp_path / "oriented_framed.jpg"
    assert source.read_bytes() == original_bytes

    with Image.open(output) as framed:
        assert framed.format == "JPEG"
        assert framed.info["icc_profile"] == icc_profile
        layout = calculate_layout(60, 80, FrameOptions())
        top = framed.getpixel((layout.image_x + 30, layout.image_y + 10))
        bottom = framed.getpixel((layout.image_x + 30, layout.image_y + 70))
        assert top[0] > 220 and top[2] < 35
        assert bottom[2] > 220 and bottom[0] < 35

        cleaned = piexif.load(framed.info["exif"])
        assert cleaned["0th"][piexif.ImageIFD.Make] == b"NIKON CORPORATION"
        assert cleaned["0th"][piexif.ImageIFD.Model] == b"NIKON Z 8"
        assert cleaned["0th"][piexif.ImageIFD.Orientation] == 1
        assert cleaned["Exif"][piexif.ExifIFD.PixelXDimension] == framed.width
        assert cleaned["Exif"][piexif.ExifIFD.PixelYDimension] == framed.height
        assert cleaned["GPS"] == {}


def test_16_bit_tiff_flattens_to_8_bit_rgb_jpeg(tmp_path: Path) -> None:
    source = tmp_path / "sixteen-bit.tiff"
    Image.new("I;16", (120, 80), 32768).save(source, format="TIFF")

    assert main([str(source), "--no-logo"]) == 0

    with Image.open(tmp_path / "sixteen-bit_framed.jpg") as framed:
        assert framed.format == "JPEG"
        assert framed.mode == "RGB"


def test_multi_page_tiff_uses_only_first_frame(tmp_path: Path) -> None:
    source = tmp_path / "pages.tif"
    first = Image.new("RGB", (120, 80), "red")
    second = Image.new("RGB", (120, 80), "blue")
    first.save(source, format="TIFF", save_all=True, append_images=[second])

    assert main([str(source), "--no-logo"]) == 0

    with Image.open(tmp_path / "pages_framed.jpg") as framed:
        layout = calculate_layout(120, 80, FrameOptions())
        center = framed.getpixel(
            (
                layout.image_x + layout.image_width // 2,
                layout.image_y + layout.image_height // 2,
            )
        )
        assert center[0] > 220 and center[2] < 35


def test_batch_continues_after_a_broken_tiff(tmp_path: Path) -> None:
    create_tiff(tmp_path / "good.tif")
    (tmp_path / "broken.tiff").write_bytes(b"this is not a tiff")

    assert main([str(tmp_path), "--no-logo"]) == 1
    assert (tmp_path / "good_framed.jpg").is_file()
    assert not (tmp_path / "broken_framed.jpg").exists()


def test_directory_cli_skips_generated_files(tmp_path: Path) -> None:
    create_jpeg(tmp_path / "one.jpg", (10, 20, 30))
    create_jpeg(tmp_path / "two.JPEG", (30, 20, 10))
    create_jpeg(tmp_path / "old_framed.jpg", (0, 0, 0))

    assert main([str(tmp_path), "--no-logo"]) == 0
    assert (tmp_path / "one_framed.jpg").is_file()
    assert (tmp_path / "two_framed.jpg").is_file()
    assert not (tmp_path / "old_framed_framed.jpg").exists()


def test_batch_continues_after_a_broken_jpeg(tmp_path: Path) -> None:
    create_jpeg(tmp_path / "good.jpg", (10, 20, 30))
    (tmp_path / "broken.jpg").write_bytes(b"this is not a jpeg")

    assert main([str(tmp_path), "--no-logo"]) == 1
    assert (tmp_path / "good_framed.jpg").is_file()
    assert not (tmp_path / "broken_framed.jpg").exists()


def test_directory_with_only_generated_files_is_a_successful_noop(
    tmp_path: Path,
) -> None:
    create_jpeg(tmp_path / "old_framed.jpg", (10, 20, 30))
    assert main([str(tmp_path)]) == 0


@pytest.mark.parametrize("suffix", [".HEIC", ".heif"])
def test_apple_heif_creates_jpeg_with_sanitized_exif(
    tmp_path: Path,
    suffix: str,
) -> None:
    source = tmp_path / f"IMG_0001{suffix}"
    create_apple_heic(source)
    original_bytes = source.read_bytes()

    assert main([str(source)]) == 0
    output = tmp_path / "IMG_0001_framed.jpg"
    assert output.is_file()
    assert source.read_bytes() == original_bytes

    with Image.open(output) as framed:
        assert framed.format == "JPEG"
        cleaned = piexif.load(framed.info["exif"])
        assert cleaned["0th"][piexif.ImageIFD.Make] == b"Apple"
        assert cleaned["GPS"] == {}


def test_social_original_and_custom_output_sizes(tmp_path: Path) -> None:
    source = tmp_path / "large.jpg"
    create_jpeg(source, (10, 80, 160), size=(2400, 1600))

    assert main([str(source), "--no-logo"]) == 0
    with Image.open(tmp_path / "large_framed.jpg") as social:
        assert max(social.size) == 2160
        cleaned = piexif.load(social.info["exif"])
        assert cleaned["Exif"][piexif.ExifIFD.PixelXDimension] == social.width
        assert cleaned["Exif"][piexif.ExifIFD.PixelYDimension] == social.height

    assert main([str(source), "-o", "--no-logo"]) == 0
    with Image.open(tmp_path / "large_framed_2.jpg") as original:
        assert original.size == (2496, 2016)

    assert main([str(source), "--max-long-edge", "1000", "--no-logo"]) == 0
    with Image.open(tmp_path / "large_framed_3.jpg") as custom:
        assert max(custom.size) == 1000


def test_quality_defaults_follow_output_mode() -> None:
    parser = build_parser()

    assert _resolved_quality(parser.parse_args(["photo.jpg"])) == 92
    assert _resolved_quality(parser.parse_args(["photo.jpg", "-o"])) == 95
    assert _resolved_quality(parser.parse_args(["photo.jpg", "--quality", "87"])) == 87


def test_original_size_and_max_long_edge_are_mutually_exclusive() -> None:
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["photo.jpg", "-o", "--max-long-edge", "1080"])


def test_max_long_edge_must_be_positive(tmp_path: Path) -> None:
    source = tmp_path / "photo.jpg"
    create_jpeg(source, (10, 80, 160))

    with pytest.raises(SystemExit):
        main([str(source), "--max-long-edge", "0"])
