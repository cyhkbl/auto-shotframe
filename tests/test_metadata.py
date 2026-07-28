import piexif
import pytest

from auto_shotframe.metadata import extract_metadata, sanitize_exif


def sample_exif() -> bytes:
    return piexif.dump(
        {
            "0th": {
                piexif.ImageIFD.Make: b"NIKON CORPORATION",
                piexif.ImageIFD.Model: b"NIKON Z 50",
                piexif.ImageIFD.Orientation: 6,
            },
            "Exif": {
                piexif.ExifIFD.LensModel: b"NIKKOR Z DX 50-250mm f/4.5-6.3 VR",
                piexif.ExifIFD.ISOSpeedRatings: 100,
                piexif.ExifIFD.FNumber: (56, 10),
                piexif.ExifIFD.ExposureTime: (1, 500),
                piexif.ExifIFD.FocalLength: (150, 1),
                piexif.ExifIFD.BodySerialNumber: b"PRIVATE-BODY",
                piexif.ExifIFD.LensSerialNumber: b"PRIVATE-LENS",
            },
            "GPS": {
                piexif.GPSIFD.GPSLatitudeRef: b"N",
                piexif.GPSIFD.GPSLatitude: ((31, 1), (12, 1), (0, 1)),
            },
            "1st": {},
            "thumbnail": None,
        }
    )


def test_extract_and_format_metadata() -> None:
    metadata = extract_metadata(sample_exif())
    assert metadata.brand is not None
    assert metadata.brand.display_name == "Nikon"
    assert metadata.shot_on_line == ("Shot on NIKON Z 50 · NIKKOR Z DX 50-250mm f/4.5-6.3 VR")
    assert metadata.exposure_line == "ISO100  |  f/5.6  |  1/500s  |  150mm"


def test_apple_shot_on_line_uses_camera_model_only() -> None:
    exif = piexif.dump(
        {
            "0th": {
                piexif.ImageIFD.Make: b"Apple",
                piexif.ImageIFD.Model: b"iPhone 15 Pro",
            },
            "Exif": {
                piexif.ExifIFD.LensModel: (b"iPhone 15 Pro back triple camera 6.765mm f/1.78"),
            },
            "GPS": {},
            "1st": {},
            "thumbnail": None,
        }
    )

    metadata = extract_metadata(exif)

    assert metadata.lens == "iPhone 15 Pro back triple camera 6.765mm f/1.78"
    assert metadata.shot_on_line == "Shot on iPhone 15 Pro"


def test_apple_lens_without_camera_model_does_not_create_shot_on_line() -> None:
    exif = piexif.dump(
        {
            "0th": {piexif.ImageIFD.Make: b"Apple"},
            "Exif": {
                piexif.ExifIFD.LensModel: b"iPhone back triple camera",
            },
            "GPS": {},
            "1st": {},
            "thumbnail": None,
        }
    )

    assert extract_metadata(exif).shot_on_line is None


def test_sanitize_exif_removes_sensitive_values_and_updates_dimensions() -> None:
    cleaned = sanitize_exif(sample_exif(), width=6400, height=4800)
    assert cleaned is not None
    result = piexif.load(cleaned)
    assert result["GPS"] == {}
    assert result["0th"][piexif.ImageIFD.Orientation] == 1
    assert piexif.ExifIFD.BodySerialNumber not in result["Exif"]
    assert piexif.ExifIFD.LensSerialNumber not in result["Exif"]
    assert result["Exif"][piexif.ExifIFD.PixelXDimension] == 6400
    assert result["Exif"][piexif.ExifIFD.PixelYDimension] == 4800
    assert result["Exif"][piexif.ExifIFD.ISOSpeedRatings] == 100


def test_missing_or_invalid_exif_is_safe() -> None:
    with pytest.warns(RuntimeWarning, match="malformed EXIF"):
        metadata = extract_metadata(b"not exif")
    assert metadata.shot_on_line is None
    assert metadata.exposure_line is None
    assert sanitize_exif(None, width=100, height=100) is None
