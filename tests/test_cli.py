from pathlib import Path

import piexif
from PIL import Image

from auto_shotframe.cli import main


def create_jpeg(path: Path, color: tuple[int, int, int]) -> None:
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
    Image.new("RGB", (160, 100), color).save(path, exif=exif)


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
