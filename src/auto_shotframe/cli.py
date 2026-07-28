from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path

from PIL import Image, ImageOps

from auto_shotframe import __version__
from auto_shotframe.frame import FrameOptions, render_frame
from auto_shotframe.metadata import extract_metadata, sanitize_exif
from auto_shotframe.naming import (
    count_generated_inputs,
    discover_inputs,
    is_jpeg,
    next_output_path,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="auto-shotframe",
        description="Add a blurred EXIF frame to JPEG photos.",
    )
    parser.add_argument("input", type=Path, help="a JPEG file or a directory")
    parser.add_argument("--quality", type=int, default=95, help="JPEG quality (1-100)")
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


def _process_photo(
    source: Path,
    *,
    options: FrameOptions,
    quality: int,
    logo_dir: Path | None,
    show_logo: bool,
) -> Path:
    output = next_output_path(source)
    temporary = output.with_name(f".{output.name}.{uuid.uuid4().hex}.tmp")
    try:
        with Image.open(source) as opened:
            opened.load()
            raw_exif = opened.info.get("exif")
            icc_profile = opened.info.get("icc_profile")
            metadata = extract_metadata(raw_exif)
            oriented = ImageOps.exif_transpose(opened).convert("RGB")

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
    if args.input.is_file() and not is_jpeg(args.input):
        parser.error("input file must have a .jpg or .jpeg extension")
    if args.quality < 1 or args.quality > 100:
        parser.error("quality must be between 1 and 100")
    if args.logo_dir is not None and not args.logo_dir.is_dir():
        parser.error(f"logo directory does not exist: {args.logo_dir}")
    options = FrameOptions(
        margin=args.margin,
        top_margin=args.top_margin,
        info_height=args.info_height,
        blur=args.blur,
        darken=args.darken,
    )
    try:
        options.validate()
    except ValueError as error:
        parser.error(str(error))
    return options


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    options = _validate_args(parser, args)
    inputs = discover_inputs(args.input)
    skipped = count_generated_inputs(args.input)
    if not inputs:
        if skipped:
            print(f"summary: 0 created, {skipped} skipped, 0 failed")
            return 0
        print("error: no eligible JPEG files found", file=sys.stderr)
        return 2

    succeeded = 0
    failed = 0
    for source in inputs:
        try:
            output = _process_photo(
                source,
                options=options,
                quality=args.quality,
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
