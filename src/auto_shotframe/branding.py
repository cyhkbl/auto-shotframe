from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from pathlib import Path

from PIL import Image


@dataclass(frozen=True)
class Brand:
    display_name: str
    slug: str
    aliases: tuple[str, ...]


BRANDS = (
    Brand("Apple", "apple", ("APPLE", "APPLE COMPUTER, INC.")),
    Brand("Nikon", "nikon", ("NIKON", "NIKON CORPORATION")),
    Brand("Canon", "canon", ("CANON", "CANON INC.", "CANON INC")),
    Brand("Sony", "sony", ("SONY", "SONY CORPORATION")),
    Brand("Fujifilm", "fujifilm", ("FUJIFILM", "FUJI PHOTO FILM CO., LTD.")),
    Brand(
        "Panasonic",
        "panasonic",
        ("PANASONIC", "PANASONIC CORPORATION", "MATSUSHITA ELECTRIC"),
    ),
    Brand("Leica", "leica", ("LEICA", "LEICA CAMERA AG")),
    Brand("Hasselblad", "hasselblad", ("HASSELBLAD", "HASSELBLAD X")),
    Brand("OnePlus", "oneplus", ("ONEPLUS", "ONE PLUS")),
)

# Internal codes that manufacturers write into the EXIF Model tag, mapped to the
# product name people recognize. Keyed by brand slug and matched
# case-insensitively. Photos keep their original EXIF; this only changes the
# caption drawn on the frame.
DISPLAY_MODEL_NAMES: dict[str, dict[str, str]] = {
    "oneplus": {
        # OnePlus 8T regional variants: KB2000 China, KB2001 India, KB2003
        # Europe, KB2005 international. KB2007 is the T-Mobile 8T+ 5G.
        "KB2000": "OnePlus 8T",
        "KB2001": "OnePlus 8T",
        "KB2003": "OnePlus 8T",
        "KB2005": "OnePlus 8T",
        "KB2007": "OnePlus 8T+ 5G",
    },
}


def normalize_manufacturer(make: str | None) -> Brand | None:
    if not make:
        return None
    normalized = " ".join(make.strip().upper().split())
    for brand in BRANDS:
        if any(alias in normalized for alias in brand.aliases):
            return brand
    return None


def display_model_name(brand: Brand | None, model: str | None) -> str | None:
    """Return the human-readable camera name for a brand and EXIF model code."""
    if brand is None or not model:
        return model
    return DISPLAY_MODEL_NAMES.get(brand.slug, {}).get(model.strip().upper(), model)


def _custom_logo_path(brand: Brand, logo_dir: Path | None) -> Path | None:
    if logo_dir is None:
        return None
    for suffix in (".png", ".PNG"):
        candidate = logo_dir / f"{brand.slug}{suffix}"
        if candidate.is_file():
            return candidate
    return None


def load_logo(brand: Brand | None, logo_dir: Path | None = None) -> Image.Image | None:
    if brand is None:
        return None
    custom = _custom_logo_path(brand, logo_dir)
    if custom is not None:
        with Image.open(custom) as image:
            return image.convert("RGBA")

    asset = resources.files("auto_shotframe.assets").joinpath("logos", "png", f"{brand.slug}.png")
    if not asset.is_file():
        return None
    with asset.open("rb") as handle, Image.open(handle) as image:
        return image.convert("RGBA")
