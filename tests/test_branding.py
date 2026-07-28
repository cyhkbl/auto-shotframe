import pytest
from PIL import Image

from auto_shotframe.branding import BRANDS, load_logo, normalize_manufacturer


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
    ],
)
def test_supported_manufacturers(make: str, expected: str) -> None:
    brand = normalize_manufacturer(make)
    assert brand is not None
    assert brand.display_name == expected


def test_unknown_manufacturer() -> None:
    assert normalize_manufacturer("Imaginary Camera Company") is None
    assert normalize_manufacturer(None) is None


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
