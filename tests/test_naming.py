from pathlib import Path

from auto_shotframe.naming import (
    count_generated_inputs,
    discover_inputs,
    is_generated,
    next_output_path,
)


def test_next_output_path_never_overwrites(tmp_path: Path) -> None:
    source = tmp_path / "photo.jpeg"
    source.touch()
    assert next_output_path(source) == tmp_path / "photo_framed.jpg"

    (tmp_path / "photo_framed.jpg").touch()
    (tmp_path / "photo_framed_2.jpg").touch()
    assert next_output_path(source) == tmp_path / "photo_framed_3.jpg"


def test_generated_name_detection_is_case_insensitive() -> None:
    assert is_generated(Path("photo_framed.JPG"))
    assert is_generated(Path("photo_FRAMED_12.jpeg"))
    assert not is_generated(Path("framed_photo.jpg"))


def test_directory_discovery_sorts_and_skips_outputs(tmp_path: Path) -> None:
    for name in (
        "B.jpeg",
        "a.JPG",
        "C.HEIC",
        "d.heif",
        "E.TIF",
        "f.tiff",
        "a_framed.jpg",
        "notes.txt",
    ):
        (tmp_path / name).touch()
    assert [path.name for path in discover_inputs(tmp_path)] == [
        "a.JPG",
        "B.jpeg",
        "C.HEIC",
        "d.heif",
        "E.TIF",
        "f.tiff",
    ]
    assert count_generated_inputs(tmp_path) == 1
