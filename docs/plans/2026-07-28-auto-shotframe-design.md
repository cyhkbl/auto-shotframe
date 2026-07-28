# auto-shotframe Design

Date: 2026-07-28
Status: Approved

## Goal

Build and publish a cross-platform Python command-line tool that accepts a JPEG
file or a directory of JPEG files, creates a photography information frame, and
writes each result beside its source without modifying or overwriting the source.

The default composition is based on the supplied references:

- a blurred, darkened extension of the source photo as the background;
- the complete source photo inset above a bottom information area;
- a camera-manufacturer logo;
- a `Shot on` line containing camera and lens information;
- an exposure line containing ISO, aperture, shutter speed, and focal length.

## Product and Packaging

- GitHub repository: `auto-shotframe`
- PyPI distribution: `auto-shotframe`
- console command: `auto-shotframe`
- import package: `auto_shotframe`
- license: MIT for project code
- supported Python versions: 3.10 through 3.13
- supported systems: macOS, Windows, and Linux
- packaging: `pyproject.toml`, `src/` layout, Hatchling
- runtime dependencies: Pillow and piexif

The repository and wheel include the selected manufacturer SVG files and
pre-rendered PNG derivatives. Third-party assets keep their source and license
records in `THIRD_PARTY_NOTICES.md`. The README states that trademarks belong to
their respective owners and that this project is not affiliated with or endorsed
by those manufacturers.

## Project Structure

```text
auto-shotframe/
├── pyproject.toml
├── README.md
├── LICENSE
├── THIRD_PARTY_NOTICES.md
├── src/auto_shotframe/
│   ├── cli.py
│   ├── frame.py
│   ├── metadata.py
│   ├── branding.py
│   ├── naming.py
│   └── assets/
│       ├── logos/svg/
│       ├── logos/png/
│       └── fonts/
└── tests/
```

Responsibilities:

- `cli.py`: argument parsing, file discovery, batch orchestration, summaries,
  and process exit codes.
- `frame.py`: canvas sizing, background generation, shadows, typography, logo
  placement, and image composition.
- `metadata.py`: EXIF parsing and normalization, display formatting, orientation
  handling, and privacy filtering.
- `branding.py`: manufacturer normalization and logo lookup.
- `naming.py`: safe output names and collision handling.

## Input and Output

```bash
auto-shotframe photo.jpg
auto-shotframe ./photos/
```

- Inputs are `.jpg` and `.jpeg`, matched case-insensitively.
- Directory input processes only the immediate directory, not subdirectories.
- Existing generated files matching `_framed` or `_framed_N` are skipped.
- The default result is `<stem>_framed.jpg`.
- If that name exists, the tool selects `<stem>_framed_2.jpg`, then increments
  until it finds an unused name.
- Existing files are never overwritten.
- The source is never modified.
- Output is written to a temporary sibling and atomically renamed only after a
  successful save.

## Default Layout

For a source image of width `W`, height `H`, and short edge `S`:

- left margin: `0.03 × S`
- right margin: `0.03 × S`
- top margin: `0.04 × S`
- bottom information area: `0.22 × S`
- output width: `W + 0.06 × S`
- output height: `H + 0.26 × S`
- Gaussian background blur radius: `0.03 × S`
- background darkening: 20%
- foreground shadow blur: `0.015 × S`
- foreground shadow offset: `0.008 × S`
- maximum logo height: `0.05 × S`

The source photo is orientation-corrected and shown completely without cropping
or stretching. The blurred background fills the entire output canvas. Font sizes
and spacing scale from `S`; overlong text shrinks to fit rather than being cut.

The first text line is:

```text
Shot on <camera model> · <lens model>
```

The second line is:

```text
ISO<value> | f/<value> | <shutter>s | <focal length>mm
```

Missing fields are omitted cleanly. If all display metadata is absent, the tool
still creates a frame and does not render empty placeholders.

The defaults can be overridden with:

```text
--quality
--margin
--top-margin
--info-height
--blur
--darken
--logo-dir
--no-logo
```

## Branding

The first release recognizes:

- Nikon
- Canon
- Sony
- Fujifilm
- Panasonic
- Leica
- Hasselblad

EXIF manufacturer values such as `NIKON CORPORATION` are normalized before
lookup. A user-supplied logo directory takes precedence over built-in assets.
When the manufacturer is recognized but no image is available, the normalized
manufacturer name is rendered as text. Unknown manufacturers receive no logo.

SVG sources are retained for provenance and future regeneration. Runtime
composition uses pre-rendered transparent PNG files so installation does not
require Cairo, ImageMagick, or another native SVG renderer.

## Metadata and Privacy

- Apply EXIF orientation before composition and reset the output orientation.
- Preserve the ICC profile and non-sensitive photography metadata when possible.
- Preserve camera, lens, ISO, aperture, exposure time, focal length, capture
  time, and copyright metadata.
- Remove GPS metadata.
- Remove camera and lens serial-number metadata.
- Default JPEG quality is 95.
- Malformed EXIF produces a warning but does not prevent framing.

## Failure Behavior

- A single-file failure leaves no partial final file.
- Batch mode continues after per-file failures.
- The final summary reports successful, skipped, and failed counts.
- Exit code 0: all requested files succeeded or were intentionally skipped.
- Exit code 1: at least one file failed during batch processing.
- Exit code 2: invalid arguments, missing input, or no eligible files.

## Fonts and Assets

Inter is bundled for consistent Latin typography on all supported platforms,
along with its SIL Open Font License. Asset-loading code uses package resources
so installed wheels behave the same as source checkouts.

## Testing

Use pytest for:

- rational EXIF conversion and display formatting;
- missing and malformed EXIF;
- manufacturer aliases and logo precedence;
- privacy filtering;
- orientation correction;
- collision-safe naming;
- generated-file skipping;
- horizontal and vertical layout calculations;
- single-file and directory CLI behavior;
- partial batch failures and exit codes.

Fixed fixture photos provide visual snapshot coverage with tolerance for small
JPEG encoder differences. CI runs Python 3.10 through 3.13 across macOS, Windows,
and Linux. Release validation builds both sdist and wheel, installs the wheel in
a clean environment, exercises the console command, and runs `twine check`.

## Out of Scope for the First Release

- graphical user interface;
- recursive directory traversal;
- RAW, HEIC, TIFF, PNG, or video input;
- fixed social-media canvas ratios;
- Lightroom-native plug-in;
- multiple visual templates;
- publishing a GitHub remote or uploading to PyPI without explicit approval.

