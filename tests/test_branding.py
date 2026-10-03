import pytest
from PIL import Image

from auto_shotframe.branding import (
    BRANDS,
    display_model_name,
    load_logo,
    normalize_manufacturer,
)


@pytest.mark.parametrize(
    ("make", "expected"),
    [
        ("Apple", "Apple"),
        ("Apple Computer, Inc.", "Apple"),
        ("NIKON CORPORATION", "Nikon"),
        ("Canon Inc.", "Canon"),
        ("SONY", "Sony"),
        ("FUJIFILM", "Fujifilm"),
        ("Panasonic Corporation", "Panasonic"),
        ("LEICA CAMERA AG", "Leica"),
        ("Hasselblad", "Hasselblad"),
        ("OnePlus", "OnePlus"),
        ("ONEPLUS", "OnePlus"),
        ("oneplus", "OnePlus"),
        ("  OnePlus  ", "OnePlus"),
        ("OnePlus Technology (Shenzhen) Co., Ltd.", "OnePlus"),
    ],
)
def test_supported_manufacturers(make: str, expected: str) -> None:
    brand = normalize_manufacturer(make)
    assert brand is not None
    assert brand.display_name == expected


def test_unknown_manufacturer() -> None:
    assert normalize_manufacturer("Imaginary Camera Company") is None
    assert normalize_manufacturer(None) is None


@pytest.mark.parametrize(
    ("model", "expected"),
    [
        ("KB2000", "OnePlus 8T"),
        ("kb2000", "OnePlus 8T"),
        ("  KB2005  ", "OnePlus 8T"),
        ("KB2007", "OnePlus 8T+ 5G"),
        ("KB9999", "KB9999"),
        (None, None),
    ],
)
def test_oneplus_internal_model_codes_are_expanded(model, expected) -> None:
    brand = normalize_manufacturer("OnePlus")
    assert display_model_name(brand, model) == expected


def test_other_brands_and_unknown_brands_keep_the_exif_model() -> None:
    assert display_model_name(normalize_manufacturer("SONY"), "ILCE-7M4") == "ILCE-7M4"
    assert display_model_name(None, "KB2000") == "KB2000"


@pytest.mark.parametrize("brand", BRANDS, ids=lambda brand: brand.slug)
def test_every_supported_brand_has_a_runtime_logo(brand) -> None:
    logo = load_logo(brand)
    assert logo is not None
    assert logo.mode == "RGBA"
    assert logo.width > 0
    assert logo.height > 0


def test_custom_logo_takes_precedence(tmp_path) -> None:
    brand = normalize_manufacturer("SONY")
    assert brand is not None
    custom = tmp_path / "sony.png"
    Image.new("RGBA", (32, 24), (255, 0, 0, 255)).save(custom)

    logo = load_logo(brand, tmp_path)
    assert logo is not None
    assert logo.size == (32, 24)
    assert logo.getpixel((0, 0)) == (255, 0, 0, 255)
