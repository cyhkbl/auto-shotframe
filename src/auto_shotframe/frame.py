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
    corner_radius: float = 0.0

    def validate(self) -> None:
        for name in (
            "margin",
            "top_margin",
            "info_height",
            "blur",
            "shadow_blur",
            "shadow_offset",
            "logo_height",
            "corner_radius",
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
    corner_radius: int


def calculate_layout(width: int, height: int, options: FrameOptions) -> Layout:
    if width <= 0 or height <= 0:
        raise ValueError("image dimensions must be positive")
    options.validate()
    short_edge = min(width, height)
    side = round(options.margin * short_edge)
    top = round(options.top_margin * short_edge)
    info = max(1, round(options.info_height * short_edge))
    radius = min(
        round(options.corner_radius * short_edge),
        width // 2,
        height // 2,
    )
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
        corner_radius=max(0, radius),
    )


def fit_source_dimensions(
    width: int,
    height: int,
    options: FrameOptions,
    *,
    max_long_edge: int,
) -> tuple[int, int]:
    if max_long_edge <= 0:
        raise ValueError("max-long-edge must be greater than 0")
    current = calculate_layout(width, height, options)
    if max(current.canvas_width, current.canvas_height) <= max_long_edge:
        return width, height

    landscape = width >= height
    dominant = width if landscape else height
    low = 1
    high = dominant - 1
    best: tuple[int, int] | None = None

    while low <= high:
        candidate = (low + high) // 2
        if landscape:
            candidate_width = candidate
            candidate_height = max(1, round(height * candidate / width))
        else:
            candidate_height = candidate
            candidate_width = max(1, round(width * candidate / height))
        layout = calculate_layout(candidate_width, candidate_height, options)
        if max(layout.canvas_width, layout.canvas_height) <= max_long_edge:
            best = candidate_width, candidate_height
            low = candidate + 1
        else:
            high = candidate - 1

    if best is None:
        raise ValueError("max-long-edge is too small for the framed layout")
    return best


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


def _load_font(
    size: int,
    *,
    weight: int = 400,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    asset = resources.files("auto_shotframe.assets").joinpath("fonts", "Jost-Variable.ttf")
    if asset.is_file():
        with asset.open("rb") as handle:
            font = ImageFont.truetype(BytesIO(handle.read()), size=max(1, size))
        font.set_variation_by_axes([weight])
        return font
    return ImageFont.load_default(size=max(1, size))


def _tracked_text_length(
    draw: ImageDraw.ImageDraw,
    text: str,
    *,
    font: ImageFont.ImageFont,
    tracking: int,
) -> float:
    glyph_width = sum(draw.textlength(character, font=font) for character in text)
    return glyph_width + max(0, len(text) - 1) * tracking


def _draw_tracked_text(
    draw: ImageDraw.ImageDraw,
    position: tuple[float, float],
    text: str,
    *,
    font: ImageFont.ImageFont,
    tracking: int,
    fill: tuple[int, int, int, int],
    stroke_width: int,
    stroke_fill: tuple[int, int, int, int],
) -> None:
    cursor_x, y = position
    for index, character in enumerate(text):
        draw.text(
            (cursor_x, y),
            character,
            font=font,
            fill=fill,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )
        cursor_x += draw.textlength(character, font=font)
        if index < len(text) - 1:
            cursor_x += tracking


def _fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    *,
    max_width: int,
    start_size: int,
    min_size: int,
    weight: int,
    tracking_ratio: float,
) -> tuple[ImageFont.ImageFont, int]:
    size = max(start_size, min_size)
    while size > min_size:
        font = _load_font(size, weight=weight)
        tracking = round(size * tracking_ratio)
        if _tracked_text_length(draw, text, font=font, tracking=tracking) <= max_width:
            return font, tracking
        size -= 1
    return _load_font(min_size, weight=weight), round(min_size * tracking_ratio)


def _scaled_logo(logo: Image.Image, max_width: int, max_height: int) -> Image.Image:
    scale = min(max_width / logo.width, max_height / logo.height, 1)
    return logo.resize(
        (max(1, round(logo.width * scale)), max(1, round(logo.height * scale))),
        Image.Resampling.LANCZOS,
    )


def _corner_tile(radius: int, corner: str, *, supersample: int) -> Image.Image:
    """Render one anti-aliased rounded-rectangle corner as an ``L`` mask tile."""
    scale = max(1, supersample)
    size = max(1, radius * scale)
    # Centre of the corner arc inside the tile. The visible quadrant is the one
    # that fills towards the middle of the rectangle.
    centres = {
        "tl": (size, size),
        "tr": (0, size),
        "bl": (size, 0),
        "br": (0, 0),
    }
    centre_x, centre_y = centres[corner]
    tile = Image.new("L", (size, size), 0)
    ImageDraw.Draw(tile).ellipse(
        (centre_x - size, centre_y - size, centre_x + size, centre_y + size),
        fill=255,
    )
    return tile.resize((radius, radius), Image.Resampling.LANCZOS)


def _rounded_mask(size: tuple[int, int], radius: int, *, supersample: int = 4) -> Image.Image:
    """Build an anti-aliased rounded-rectangle mask for the framed photo."""
    width, height = size
    mask = Image.new("L", (width, height), 255)
    radius = max(0, min(radius, width // 2, height // 2))
    if radius == 0:
        return mask
    for corner, box in (
        ("tl", (0, 0)),
        ("tr", (width - radius, 0)),
        ("bl", (0, height - radius)),
        ("br", (width - radius, height - radius)),
    ):
        mask.paste(_corner_tile(radius, corner, supersample=supersample), box)
    return mask


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
    photo = image.convert("RGBA")
    if layout.corner_radius:
        photo_mask = _rounded_mask(
            (layout.image_width, layout.image_height),
            layout.corner_radius,
        )
        photo.putalpha(photo_mask)

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
    offset = round(options.shadow_offset * layout.short_edge)
    if layout.corner_radius:
        # Reuse the photo mask so the shadow follows the rounded silhouette
        # instead of poking out square corners behind the photo.
        shadow.paste(105, (layout.image_x + offset, layout.image_y + offset), photo_mask)
    else:
        ImageDraw.Draw(shadow).rectangle(
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
    canvas.alpha_composite(photo, (layout.image_x, layout.image_y))

    draw = ImageDraw.Draw(canvas)
    text_overlay = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_overlay)
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
            weight = 400
            tracking_ratio = 0.04 if kind in {"brand", "line_one"} else 0.02
            font, tracking = _fit_font(
                draw,
                str(value),
                max_width=max_text_width,
                start_size=max(6, start),
                min_size=max(5, round(0.012 * layout.short_edge)),
                weight=weight,
                tracking_ratio=tracking_ratio,
            )
            bbox = draw.textbbox((0, 0), str(value), font=font)
            rendered.append((kind, (str(value), font, tracking), bbox[3] - bbox[1]))

        total_height = sum(height for _, _, height in rendered) + gap * (len(rendered) - 1)
        cursor_y = layout.info_y + max(0, (layout.info_height - total_height) // 2)
        for kind, value, element_height in rendered:
            if kind == "logo":
                logo_image = value
                x = (layout.canvas_width - logo_image.width) // 2
                canvas.alpha_composite(logo_image, (x, cursor_y))
            else:
                text, font, tracking = value
                text_width = _tracked_text_length(draw, text, font=font, tracking=tracking)
                x = (layout.canvas_width - text_width) / 2
                _draw_tracked_text(
                    text_draw,
                    (x, cursor_y),
                    text,
                    font=font,
                    tracking=tracking,
                    fill=(248, 248, 248, 255),
                    stroke_width=0,
                    stroke_fill=(0, 0, 0, 0),
                )
            cursor_y += element_height + gap

        canvas = Image.alpha_composite(canvas, text_overlay)

    return canvas.convert("RGB")
