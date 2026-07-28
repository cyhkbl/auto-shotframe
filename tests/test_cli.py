from pathlib import Path

import piexif
import pytest
from PIL import Image

from auto_shotframe.cli import _resolved_quality, build_parser, main


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
