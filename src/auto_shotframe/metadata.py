from __future__ import annotations

import warnings
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

import piexif

from auto_shotframe.branding import Brand, normalize_manufacturer


@dataclass(frozen=True)
class PhotoMetadata:
    make: str | None
    brand: Brand | None
    camera: str | None
    lens: str | None
    iso: int | None
    aperture: float | None
    exposure_seconds: float | None
    focal_length_mm: float | None

    @property
    def shot_on_line(self) -> str | None:
        if self.brand is not None and self.brand.slug == "apple":
            return f"Shot on {self.camera}" if self.camera else None
        details = [value for value in (self.camera, self.lens) if value]
        return f"Shot on {' · '.join(details)}" if details else None

    @property
    def exposure_line(self) -> str | None:
        parts: list[str] = []
        if self.iso is not None:
            parts.append(f"ISO{self.iso}")
        if self.aperture is not None:
            parts.append(f"f/{_compact_number(self.aperture)}")
        if self.exposure_seconds is not None:
            parts.append(_format_shutter(self.exposure_seconds))
        if self.focal_length_mm is not None:
            parts.append(f"{_compact_number(self.focal_length_mm)}mm")
        return "  |  ".join(parts) if parts else None


def _decode(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    text = str(value).strip().strip("\x00")
    return text or None


def _rational_to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, tuple) and len(value) == 2:
        numerator, denominator = value
        if denominator == 0:
            return None
        return float(numerator) / float(denominator)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _compact_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.1f}".rstrip("0").rstrip(".")


def _format_shutter(seconds: float) -> str:
    if seconds <= 0:
        return "0s"
    if seconds < 1:
        reciprocal = 1 / seconds
        rounded = round(reciprocal)
        if abs(reciprocal - rounded) < 0.02:
            return f"1/{rounded}s"
        fraction = Fraction(seconds).limit_denominator(8000)
        return f"{fraction.numerator}/{fraction.denominator}s"
    return f"{_compact_number(seconds)}s"


def extract_metadata(exif_bytes: bytes | None) -> PhotoMetadata:
    exif = _load_exif(exif_bytes, warn=True)
    zeroth = exif.get("0th", {})
    exif_ifd = exif.get("Exif", {})

    make = _decode(zeroth.get(piexif.ImageIFD.Make))
    iso_value = exif_ifd.get(piexif.ExifIFD.ISOSpeedRatings)
    if isinstance(iso_value, tuple):
        iso_value = iso_value[0] if iso_value else None
    try:
        iso = int(iso_value) if iso_value is not None else None
    except (TypeError, ValueError):
        iso = None

    return PhotoMetadata(
        make=make,
        brand=normalize_manufacturer(make),
        camera=_decode(zeroth.get(piexif.ImageIFD.Model)),
        lens=_decode(exif_ifd.get(piexif.ExifIFD.LensModel)),
        iso=iso,
        aperture=_rational_to_float(exif_ifd.get(piexif.ExifIFD.FNumber)),
        exposure_seconds=_rational_to_float(exif_ifd.get(piexif.ExifIFD.ExposureTime)),
        focal_length_mm=_rational_to_float(exif_ifd.get(piexif.ExifIFD.FocalLength)),
    )


def _empty_exif() -> dict[str, Any]:
    return {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}


def _load_exif(
    exif_bytes: bytes | None,
    *,
    warn: bool = False,
) -> dict[str, Any]:
    if not exif_bytes:
        return _empty_exif()
    try:
        return piexif.load(exif_bytes)
    except (OSError, ValueError, TypeError, piexif.InvalidImageDataError) as error:
        if warn:
            warnings.warn(
                f"ignoring malformed EXIF data: {error}",
                RuntimeWarning,
                stacklevel=2,
            )
        return _empty_exif()


def sanitize_exif(
    exif_bytes: bytes | None,
    *,
    width: int,
    height: int,
) -> bytes | None:
    if not exif_bytes:
        return None
    exif = _load_exif(exif_bytes)
    zeroth = exif.get("0th", {})
    exif_ifd = exif.get("Exif", {})

    zeroth[piexif.ImageIFD.Orientation] = 1
    exif_ifd.pop(piexif.ExifIFD.BodySerialNumber, None)
    exif_ifd.pop(piexif.ExifIFD.LensSerialNumber, None)
    exif_ifd.pop(piexif.ExifIFD.MakerNote, None)
    exif_ifd.pop(piexif.ExifIFD.ImageUniqueID, None)
    exif_ifd.pop(piexif.ExifIFD.CameraOwnerName, None)
    exif_ifd[piexif.ExifIFD.PixelXDimension] = width
    exif_ifd[piexif.ExifIFD.PixelYDimension] = height

    exif["0th"] = zeroth
    exif["Exif"] = exif_ifd
    exif["GPS"] = {}
    exif["1st"] = {}
    exif["thumbnail"] = None
    try:
        return piexif.dump(exif)
    except (ValueError, TypeError):
        return None
