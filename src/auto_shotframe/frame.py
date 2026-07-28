from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from auto_shotframe.branding import load_logo
from auto_shotframe.metadata import PhotoMetadata


@dataclass(frozen=True)
class FrameOptions:
    margin: float = 0.03
    top_margin: float = 0.04
    info_height: float = 0.22
    blur: float = 0.03
    darken: float = 0.20
    shadow_blur: float = 0.015
    shadow_offset: float = 0.008
    logo_height: float = 0.05

    def validate(self) -> None:
        for name in (
            "margin",
            "top_margin",
            "info_height",
            "blur",
            "shadow_blur",
            "shadow_offset",
            "logo_height",
        ):
            value = getattr(self, name)
            if value < 0 or value > 1:
                raise ValueError(f"{name.replace('_', '-')} must be between 0 and 1")
        if self.info_height == 0:
            raise ValueError("info-height must be greater than 0")
        if self.darken < 0 or self.darken > 1:
            raise ValueError("darken must be between 0 and 1")


@dataclass(frozen=True)
class Layout:
    canvas_width: int
    canvas_height: int
    image_x: int
    image_y: int
    image_width: int
    image_height: int
    info_y: int
    info_height: int
    short_edge: int


def calculate_layout(width: int, height: int, options: FrameOptions) -> Layout:
    if width <= 0 or height <= 0:
        raise ValueError("image dimensions must be positive")
    options.validate()
    short_edge = min(width, height)
    side = round(options.margin * short_edge)
    top = round(options.top_margin * short_edge)
    info = max(1, round(options.info_height * short_edge))
    return Layout(
        canvas_width=width + (2 * side),
        canvas_height=height + top + info,
        image_x=side,
        image_y=top,
        image_width=width,
        image_height=height,
        info_y=top + height,
        info_height=info,
        short_edge=short_edge,
    )


def _cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_width, target_height = size
    scale = max(target_width / image.width, target_height / image.height)
    resized = image.resize(
        (max(1, round(image.width * scale)), max(1, round(image.height * scale))),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - target_width) // 2
    top = (resized.height - target_height) // 2
    return resized.crop((left, top, left + target_width, top + target_height))


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    asset = resources.files("auto_shotframe.assets").joinpath("fonts", "Inter-Regular.ttf")
    if asset.is_file():
        with asset.open("rb") as handle:
            return ImageFont.truetype(BytesIO(handle.read()), size=max(1, size))
    return ImageFont.load_default(size=max(1, size))


def _fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    *,
    max_width: int,
    start_size: int,
    min_size: int,
) -> ImageFont.ImageFont:
    size = max(start_size, min_size)
    while size > min_size:
        font = _load_font(size)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= 1
    return _load_font(min_size)


def _scaled_logo(logo: Image.Image, max_width: int, max_height: int) -> Image.Image:
    scale = min(max_width / logo.width, max_height / logo.height, 1)
    return logo.resize(
        (max(1, round(logo.width * scale)), max(1, round(logo.height * scale))),
        Image.Resampling.LANCZOS,
    )


def render_frame(
    image: Image.Image,
    metadata: PhotoMetadata,
    *,
    options: FrameOptions,
    logo_dir: Path | None = None,
    show_logo: bool = True,
) -> Image.Image:
    layout = calculate_layout(image.width, image.height, options)
    canvas_size = (layout.canvas_width, layout.canvas_height)

    background = _cover(image, canvas_size).filter(
        ImageFilter.GaussianBlur(radius=max(0, options.blur * layout.short_edge))
    )
    if options.darken:
        background = Image.blend(
            background,
            Image.new("RGB", canvas_size, "black"),
            options.darken,
        )
    canvas = background.convert("RGBA")

    shadow = Image.new("L", canvas_size, 0)
    shadow_draw = ImageDraw.Draw(shadow)
    offset = round(options.shadow_offset * layout.short_edge)
    shadow_draw.rectangle(
        (
            layout.image_x + offset,
            layout.image_y + offset,
            layout.image_x + layout.image_width + offset,
            layout.image_y + layout.image_height + offset,
        ),
        fill=105,
    )
    shadow = shadow.filter(
        ImageFilter.GaussianBlur(radius=max(0, options.shadow_blur * layout.short_edge))
    )
    canvas.paste((0, 0, 0, 255), (0, 0), shadow)
    canvas.alpha_composite(image.convert("RGBA"), (layout.image_x, layout.image_y))

    draw = ImageDraw.Draw(canvas)
    logo = load_logo(metadata.brand, logo_dir) if show_logo else None
    logo_height = max(1, round(options.logo_height * layout.short_edge))
    logo_max_width = max(1, round(layout.canvas_width * 0.22))
    line_one = metadata.shot_on_line
    line_two = metadata.exposure_line

    elements: list[tuple[str, object]] = []
    if logo is not None:
        logo = _scaled_logo(logo, logo_max_width, logo_height)
        elements.append(("logo", logo))
    elif show_logo and metadata.brand is not None:
        elements.append(("brand", metadata.brand.display_name))
    if line_one:
        elements.append(("line_one", line_one))
    if line_two:
        elements.append(("line_two", line_two))

    if elements:
        gap = max(2, round(0.012 * layout.short_edge))
        max_text_width = max(1, layout.canvas_width - (4 * layout.image_x))
        rendered: list[tuple[str, object, int]] = []
        for kind, value in elements:
            if kind == "logo":
                rendered.append((kind, value, value.height))
                continue
            start = round((0.026 if kind in {"brand", "line_one"} else 0.021) * layout.short_edge)
            font = _fit_font(
                draw,
                str(value),
                max_width=max_text_width,
                start_size=max(6, start),
                min_size=max(5, round(0.012 * layout.short_edge)),
            )
            bbox = draw.textbbox((0, 0), str(value), font=font)
            rendered.append((kind, (str(value), font), bbox[3] - bbox[1]))

        total_height = sum(height for _, _, height in rendered) + gap * (len(rendered) - 1)
        cursor_y = layout.info_y + max(0, (layout.info_height - total_height) // 2)
        for kind, value, element_height in rendered:
            if kind == "logo":
                logo_image = value
                x = (layout.canvas_width - logo_image.width) // 2
                canvas.alpha_composite(logo_image, (x, cursor_y))
            else:
                text, font = value
                text_width = round(draw.textlength(text, font=font))
                x = (layout.canvas_width - text_width) // 2
                draw.text(
                    (x, cursor_y),
                    text,
                    font=font,
                    fill=(240, 240, 240, 235),
                    stroke_width=1,
                    stroke_fill=(0, 0, 0, 90),
                )
            cursor_y += element_height + gap

    return canvas.convert("RGB")
