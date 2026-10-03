# auto-shotframe

English |
[简体中文](https://github.com/SeanYancy/auto-shotframe/blob/main/README.zh-CN.md)

`auto-shotframe` is a cross-platform command-line tool that turns JPEG, HEIF,
and TIFF photos into framed, share-ready JPEGs with a blurred background, camera
branding, and EXIF shooting information.

It reads a photo such as:

```text
photo.heic
```

and creates a sibling without touching the source:

```text
photo_framed.jpg
```

If the name already exists, the next result is `photo_framed_2.jpg`.

## Features

- accepts one JPEG, HEIC, HEIF, TIF, or TIFF photo, or a directory containing
  them;
- preserves the complete photo without cropping or stretching;
- creates a proportional blurred and darkened background;
- optionally rounds the photo corners, with a drop shadow that follows the same
  rounded silhouette;
- reads camera, lens, ISO, aperture, shutter speed, and focal length from EXIF;
- recognizes Apple, Nikon, Canon, Sony, Fujifilm, Panasonic, Leica,
  Hasselblad, and OnePlus;
- expands internal model codes such as OnePlus `KB2000` into the marketed name
  (`OnePlus 8T`) for the caption only, leaving EXIF untouched;
- includes built-in manufacturer marks and supports custom PNG overrides;
- bundles Jost and uses Light/Regular weights with photographic letter spacing;
- creates a social-ready 2160-pixel long edge by default, drawing text only
  after the source photo reaches its final working size;
- removes GPS and device-identifying metadata from exported results;
- preserves common photographic EXIF and ICC color data;
- works on macOS, Windows, and Linux with Python 3.10 or newer.

## Installation

From PyPI:

```bash
python -m pip install auto-shotframe
```

From a source checkout:

```bash
python -m pip install .
```

## Usage

Frame one JPEG, HEIF, or TIFF photo:

```bash
auto-shotframe /path/to/photo.heic
```

Frame every supported photo in one directory:

```bash
auto-shotframe /path/to/photos/
```

Directory processing is intentionally non-recursive. Files that already end in
`_framed` or `_framed_N` are skipped.

## Output Size

The default output is optimized for social sharing. Its final framed canvas has
a maximum long edge of 2160 pixels. Smaller photos are never enlarged. The
source photo is resized first, then the frame, logo, and text are rendered at the
final working size.

Keep the source pixel dimensions:

```bash
auto-shotframe photo.jpg -o
```

`-o` is short for `--original-size`. It disables resizing but is not lossless:
adding a frame still requires JPEG encoding.

Choose another final-canvas limit:

```bash
auto-shotframe photo.jpg --max-long-edge 1080
```

## Options

```text
--quality N          JPEG quality; default: 92, or 95 with --original-size
-o, --original-size  keep source pixel dimensions; still encodes as JPEG
--max-long-edge N    maximum final canvas long edge; default: 2160
--margin R           left/right margin as a short-edge ratio; default: 0.105
--top-margin R       top margin as a short-edge ratio; default: 0.130
--info-height R      information-area ratio; default: 0.22
--corner-radius R    photo corner radius as a short-edge ratio; default: 0.040
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
apple.png
nikon.png
canon.png
sony.png
fujifilm.png
panasonic.png
leica.png
hasselblad.png
oneplus.png
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
| Left/right margin | 10.5% |
| Top margin | 13% |
| Bottom information area | 22% |
| Photo corner radius | 4% |
| Background blur radius | 3% |
| Background darkening | 20% |
| Logo maximum height | 5% |

The photo is inset by the margin on the left, right, and top, and the
information area occupies the bottom. This build defaults to a wide, rounded
frame that leaves plenty of blurred background; pass smaller values for a
tighter, squarer frame:

```bash
# tighter frame, closer to upstream defaults
auto-shotframe photo.jpg --margin 0.03 --top-margin 0.04 --corner-radius 0
```

The first line contains the camera and lens. For Apple photos it contains only
the iPhone model, avoiding raw descriptions such as `back triple camera`. The
second line contains ISO, aperture, shutter speed, and focal length. Missing
fields are omitted instead of showing empty placeholders.

Some manufacturers record an internal code instead of the product name. Those
codes are expanded for the caption while the exported EXIF keeps the original
value:

| EXIF Make | EXIF Model | Caption |
| --- | --- | --- |
| `OnePlus` | `KB2000` | `OnePlus 8T` |
| `OnePlus` | `KB2001` | `OnePlus 8T` |
| `OnePlus` | `KB2003` | `OnePlus 8T` |
| `OnePlus` | `KB2005` | `OnePlus 8T` |
| `OnePlus` | `KB2007` | `OnePlus 8T+ 5G` |

Brand matching ignores letter case and surrounding whitespace, so `OnePlus`,
`ONEPLUS`, and `oneplus` are all recognized.

## Metadata and Privacy

The framed result preserves common photographic EXIF fields and the source ICC
profile when present. It removes:

- GPS metadata;
- camera and lens serial-number fields;
- maker notes, which can contain vendor-specific identifiers;
- image unique ID and camera owner name.
- TIFF storage fields plus XMP, IPTC, and Photoshop resource containers when
  exporting a TIFF input to JPEG.

The source JPEG, HEIF, or TIFF photo is never modified.

## HEIF Notes

`.heic` and `.heif` inputs use the primary image in the container and always
produce a sibling JPEG. 10-bit and 12-bit HEIF photos are rendered to an 8-bit
SDR result. HDR gain maps, auxiliary depth images, additional container images,
and Live Photo video are not copied to the framed output.

iPhone originals commonly provide camera model, lens, ISO, aperture, shutter
speed, and focal length through EXIF. Screenshots, social-media downloads, and
other re-exports may have some or all of those fields removed; missing values are
simply omitted from the frame.

## TIFF Notes

`.tif` and `.tiff` inputs use the first image and always produce a sibling JPEG.
Camera-exported TIFF metadata is read from TIFF IFD/EXIF fields when Pillow
exposes it. Multi-page TIFF files use only their first page.

The current output pipeline is intentionally not lossless: 16-bit TIFF data is
flattened to an 8-bit RGB JPEG. `-o/--original-size` prevents pixel resizing but
does not preserve TIFF bit depth or compression. Unsupported TIFF compression
variants and damaged files are reported without stopping the remaining files in
a directory batch.

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
