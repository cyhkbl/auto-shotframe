from __future__ import annotations

import re
from pathlib import Path

JPEG_SUFFIXES = {".jpg", ".jpeg"}
_GENERATED_STEM = re.compile(r"_framed(?:_\d+)?$", re.IGNORECASE)


def is_jpeg(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in JPEG_SUFFIXES


def is_generated(path: Path) -> bool:
    return bool(_GENERATED_STEM.search(path.stem))


def next_output_path(source: Path) -> Path:
    candidate = source.with_name(f"{source.stem}_framed.jpg")
    counter = 2
    while candidate.exists():
        candidate = source.with_name(f"{source.stem}_framed_{counter}.jpg")
        counter += 1
    return candidate


def discover_inputs(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path] if is_jpeg(input_path) else []
    if not input_path.is_dir():
        return []
    return sorted(
        (path for path in input_path.iterdir() if is_jpeg(path) and not is_generated(path)),
        key=lambda path: path.name.casefold(),
    )


def count_generated_inputs(input_path: Path) -> int:
    if not input_path.is_dir():
        return 0
    return sum(1 for path in input_path.iterdir() if is_jpeg(path) and is_generated(path))
