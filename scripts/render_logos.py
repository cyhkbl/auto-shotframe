"""Regenerate runtime PNG logos from the bundled SVG sources.

This maintainer script requires resvg-py. It is deliberately not a runtime
dependency because generated PNG files are committed and shipped in the wheel.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw
from resvg_py import svg_to_bytes

ROOT = Path(__file__).resolve().parents[1]
SVG_DIR = ROOT / "src" / "auto_shotframe" / "assets" / "logos" / "svg"
PNG_DIR = ROOT / "src" / "auto_shotframe" / "assets" / "logos" / "png"

COLORS = {
    "apple": "#FFFFFF",
    "canon": "#CC0000",
    "fujifilm": "#FFFFFF",
    "hasselblad": "#FFFFFF",
    "leica": "#FFFFFF",
    "nikon": "#111111",
    "oneplus": "#EB0027",
    "panasonic": "#FFFFFF",
    "sony": "#FFFFFF",
}


def render_source(path: Path) -> Image.Image:
    png = svg_to_bytes(svg_path=str(path), width=2048)
    with Image.open(BytesIO(png)) as rendered:
        image = rendered.convert("RGBA")
    alpha = image.getchannel("A")
    bounds = alpha.getbbox()
    if bounds is None:
        raise ValueError(f"SVG rendered without visible pixels: {path}")
    return image.crop(bounds)


def fit(image: Image.Image, max_size: tuple[int, int]) -> Image.Image:
    max_width, max_height = max_size
    scale = min(max_width / image.width, max_height / image.height)
    return image.resize(
        (max(1, round(image.width * scale)), max(1, round(image.height * scale))),
        Image.Resampling.LANCZOS,
    )


def recolor(image: Image.Image, color: str) -> Image.Image:
    colored = Image.new("RGBA", image.size, color)
    colored.putalpha(image.getchannel("A"))
    return colored


def add_badge(image: Image.Image, background: str, *, roundness: float) -> Image.Image:
    padding = max(12, round(image.height * 0.25))
    size = (image.width + 2 * padding, image.height + 2 * padding)
    badge = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge)
    draw.rounded_rectangle(
        (0, 0, size[0] - 1, size[1] - 1),
        radius=round(size[1] * roundness),
        fill=background,
    )
    badge.alpha_composite(image, (padding, padding))
    return badge


def build_logo(path: Path) -> Image.Image:
    slug = path.stem
    source = render_source(path)
    source = recolor(source, COLORS[slug])
    source = fit(source, (1024, 220))
    if slug == "nikon":
        return add_badge(source, "#FFE100", roundness=0.08)
    if slug == "leica":
        return add_badge(source, "#E30613", roundness=0.50)
    return source


def main() -> None:
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    for source in sorted(SVG_DIR.glob("*.svg")):
        output = PNG_DIR / f"{source.stem}.png"
        build_logo(source).save(output, optimize=True)
        print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
