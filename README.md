# auto-shotframe

`auto-shotframe` is a cross-platform command-line tool that turns JPEG photos
into framed, share-ready images with a blurred background, camera branding, and
EXIF shooting information.

It reads a photo such as:

```text
photo.jpg
```

and creates a sibling without touching the source:

```text
photo_framed.jpg
```

If the name already exists, the next result is `photo_framed_2.jpg`.

## Features

- accepts one JPEG or a directory of JPEG files;
- preserves the complete photo without cropping or stretching;
- creates a proportional blurred and darkened background;
- reads camera, lens, ISO, aperture, shutter speed, and focal length from EXIF;
- recognizes Nikon, Canon, Sony, Fujifilm, Panasonic, Leica, and Hasselblad;
- includes built-in manufacturer marks and supports custom PNG overrides;
- removes GPS and device-identifying metadata from exported results;
- preserves common photographic EXIF and ICC color data;
- works on macOS, Windows, and Linux with Python 3.10 or newer.

## Installation

From PyPI after the first release:

```bash
python -m pip install auto-shotframe
```

From a source checkout:

```bash
python -m pip install .
```

## Usage

Frame one JPEG:

```bash
auto-shotframe /path/to/photo.jpg
```

Frame every JPEG in one directory:

```bash
auto-shotframe /path/to/photos/
```

Directory processing is intentionally non-recursive. Files that already end in
`_framed` or `_framed_N` are skipped.

## Options

```text
--quality N          JPEG quality from 1 to 100; default: 95
--margin R           left/right margin as a short-edge ratio; default: 0.03
--top-margin R       top margin as a short-edge ratio; default: 0.04
--info-height R      information-area ratio; default: 0.22
--blur R             blur radius ratio; default: 0.03
--darken R           background darkening from 0 to 1; default: 0.20
--logo-dir PATH      directory containing custom lowercase PNG logos
--no-logo            hide the manufacturer logo
--version            print the installed version
```

Example:

```bash
auto-shotframe photo.jpg --quality 92 --darken 0.30 --info-height 0.25
```

## Custom Logos

Pass a directory containing any of these lowercase filenames:

```text
nikon.png
canon.png
sony.png
fujifilm.png
panasonic.png
leica.png
hasselblad.png
```

Transparent PNG files work best:

```bash
auto-shotframe photo.jpg --logo-dir ./my-logos
```

Custom assets take precedence over built-in assets. If a recognized brand has no
usable image, its name is rendered as text.

## Default Layout

All dimensions scale from the source photo's short edge:

| Element | Default |
| --- | ---: |
| Left/right margin | 3% |
| Top margin | 4% |
| Bottom information area | 22% |
| Background blur radius | 3% |
| Background darkening | 20% |
| Logo maximum height | 5% |

The first line contains the camera and lens. The second contains ISO, aperture,
shutter speed, and focal length. Missing fields are omitted instead of showing
empty placeholders.

## Metadata and Privacy

The framed result preserves common photographic EXIF fields and the source ICC
profile when present. It removes:

- GPS metadata;
- camera and lens serial-number fields;
- maker notes, which can contain vendor-specific identifiers;
- image unique ID and camera owner name.

The source JPEG is never modified.

## Development

```bash
python -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest
.venv/bin/ruff check .
```

On Windows, replace `.venv/bin/python` with `.venv\Scripts\python`.

Regenerate runtime PNG logos from the bundled SVG sources:

```bash
.venv/bin/python scripts/render_logos.py
```

## Assets and Trademarks

Font and logo origins are recorded in
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). All product names,
trademarks, and registered trademarks are the property of their respective
owners. Their use identifies metadata recorded by the camera and does not imply
affiliation, sponsorship, or endorsement.

## License

Project code is released under the MIT License. Bundled third-party assets remain
subject to the terms and notices recorded in `THIRD_PARTY_NOTICES.md`.
