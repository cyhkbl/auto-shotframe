from __future__ import annotations

import argparse
import os
import sys
import uuid
import warnings
from pathlib import Path

from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

from auto_shotframe import __version__
from auto_shotframe.frame import FrameOptions, fit_source_dimensions, render_frame
from auto_shotframe.metadata import extract_metadata, sanitize_exif
from auto_shotframe.naming import (
    count_generated_inputs,
    discover_inputs,
    is_supported_image,
    next_output_path,
)

register_heif_opener()

SOCIAL_MAX_LONG_EDGE = 2160
SOCIAL_QUALITY = 92
ORIGINAL_QUALITY = 95


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="auto-shotframe",
        description="Add a blurred EXIF frame to JPEG, HEIF, and TIFF photos.",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="a JPEG/HEIC/HEIF/TIFF file or a directory",
    )
    parser.add_argument(
        "--quality",
        type=int,
        help="JPEG quality (1-100; default: 92, or 95 with --original-size)",
    )
    sizing = parser.add_mutually_exclusive_group()
    sizing.add_argument(
        "-o",
        "--original-size",
        action="store_true",
        help="keep the source pixel dimensions (still re-encodes as JPEG)",
    )
    sizing.add_argument(
        "--max-long-edge",
        type=int,
        default=SOCIAL_MAX_LONG_EDGE,
        metavar="N",
        help="maximum final canvas long edge (default: 2160)",
    )
    parser.add_argument(
        "--margin",
        type=float,
        default=0.03,
        help="left/right margin as a short-edge ratio (default: 0.03)",
    )
    parser.add_argument(
        "--top-margin",
        type=float,
        default=0.04,
        help="top margin as a short-edge ratio (default: 0.04)",
    )
    parser.add_argument(
        "--info-height",
        type=float,
        default=0.22,
        help="bottom information area as a short-edge ratio (default: 0.22)",
    )
    parser.add_argument(
        "--corner-radius",
        type=float,
        default=0.0,
        help="photo corner radius as a short-edge ratio, 0 for square (default: 0)",
    )
    parser.add_argument(
        "--blur",
        type=float,
        default=0.03,
        help="background blur radius as a short-edge ratio (default: 0.03)",
    )
    parser.add_argument(
        "--darken",
        type=float,
        default=0.20,
        help="background darkening from 0 to 1 (default: 0.20)",
    )
    parser.add_argument(
        "--logo-dir",
        type=Path,
        help="directory containing custom lowercase PNG logos",
    )
    parser.add_argument("--no-logo", action="store_true", help="hide the manufacturer logo")
    parser.add_argument("--version", action="version", version=__version__)
    return parser


def _read_exif_bytes(image: Image.Image) -> bytes | None:
    raw_exif = image.info.get("exif")
    if isinstance(raw_exif, bytes):
        return raw_exif
    if isinstance(raw_exif, bytearray):
        return bytes(raw_exif)

    exif = image.getexif()
    if not exif:
        return None
    try:
        return exif.tobytes()
    except (OSError, TypeError, ValueError):
        return None


def _process_photo(
    source: Path,
    *,
    options: FrameOptions,
    quality: int,
    max_long_edge: int | None,
    logo_dir: Path | None,
    show_logo: bool,
) -> Path:
    output = next_output_path(source)
    temporary = output.with_name(f".{output.name}.{uuid.uuid4().hex}.tmp")
    try:
        with Image.open(source) as opened:
            with warnings.catch_warnings():
                if source.suffix.lower() in {".tif", ".tiff"}:
                    warnings.filterwarnings(
                        "ignore",
                        message=(
                            r"Metadata Warning, tag 33723 had too many entries: "
                            r"\d+, expected 1"
                        ),
                        category=UserWarning,
                        module=r"PIL\.TiffImagePlugin",
                    )
                opened.load()
                raw_exif = _read_exif_bytes(opened)
            icc_profile = opened.info.get("icc_profile")
            metadata = extract_metadata(raw_exif)
            oriented = ImageOps.exif_transpose(opened).convert("RGB")

        if max_long_edge is not None:
            target_size = fit_source_dimensions(
                oriented.width,
                oriented.height,
                options,
                max_long_edge=max_long_edge,
            )
            if target_size != oriented.size:
                oriented = oriented.resize(target_size, Image.Resampling.LANCZOS)

        framed = render_frame(
            oriented,
            metadata,
            options=options,
            logo_dir=logo_dir,
            show_logo=show_logo,
        )
        exif = sanitize_exif(
            raw_exif,
            width=framed.width,
            height=framed.height,
        )
        save_options: dict[str, object] = {
            "format": "JPEG",
            "quality": quality,
            "optimize": True,
            "subsampling": 0,
        }
        if exif:
            save_options["exif"] = exif
        if icc_profile:
            save_options["icc_profile"] = icc_profile
        framed.save(temporary, **save_options)
        os.replace(temporary, output)
        return output
    finally:
        temporary.unlink(missing_ok=True)


def _validate_args(
    parser: argparse.ArgumentParser,
    args: argparse.Namespace,
) -> FrameOptions:
    if not args.input.exists():
        parser.error(f"input does not exist: {args.input}")
    if args.input.is_file() and not is_supported_image(args.input):
        parser.error(
            "input file must have a .jpg, .jpeg, .heic, .heif, .tif, or .tiff extension"
        )
    if args.quality is not None and (args.quality < 1 or args.quality > 100):
        parser.error("quality must be between 1 and 100")
    if args.max_long_edge <= 0:
        parser.error("max-long-edge must be greater than 0")
    if args.logo_dir is not None and not args.logo_dir.is_dir():
        parser.error(f"logo directory does not exist: {args.logo_dir}")
    options = FrameOptions(
        margin=args.margin,
        top_margin=args.top_margin,
        info_height=args.info_height,
        blur=args.blur,
        darken=args.darken,
        corner_radius=args.corner_radius,
    )
    try:
        options.validate()
    except ValueError as error:
        parser.error(str(error))
    return options


def _resolved_quality(args: argparse.Namespace) -> int:
    if args.quality is not None:
        return args.quality
    return ORIGINAL_QUALITY if args.original_size else SOCIAL_QUALITY


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    options = _validate_args(parser, args)
    quality = _resolved_quality(args)
    max_long_edge = None if args.original_size else args.max_long_edge
    inputs = discover_inputs(args.input)
    skipped = count_generated_inputs(args.input)
    if not inputs:
        if skipped:
            print(f"summary: 0 created, {skipped} skipped, 0 failed")
            return 0
        print("error: no eligible JPEG, HEIF, or TIFF files found", file=sys.stderr)
        return 2

    succeeded = 0
    failed = 0
    for source in inputs:
        try:
            output = _process_photo(
                source,
                options=options,
                quality=quality,
                max_long_edge=max_long_edge,
                logo_dir=args.logo_dir,
                show_logo=not args.no_logo,
            )
        except Exception as error:
            failed += 1
            print(f"failed: {source.name}: {error}", file=sys.stderr)
        else:
            succeeded += 1
            print(f"created: {output}")

    print(f"summary: {succeeded} created, {skipped} skipped, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
