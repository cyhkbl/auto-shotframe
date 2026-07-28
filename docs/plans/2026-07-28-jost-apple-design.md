# Jost Typography and Apple Branding Design

Date: 2026-07-28
Status: Approved

## Scope

Apply two changes to the unreleased `auto-shotframe` 0.1.0 package:

1. replace Inter with Jost for a more geometric, vintage-modern photographic
   presentation;
2. add Apple as the eighth recognized camera manufacturer.

PNG and HEIC input remain out of scope. Apple support applies to eligible JPEG
files containing Apple EXIF metadata.

## Typography

- Bundle Jost Light and Jost Regular under the SIL Open Font License 1.1.
- Use Jost Light for the `Shot on` line.
- Use Jost Regular for the exposure line and manufacturer-name fallback.
- Add letter spacing equal to approximately 4% of the font size on the first
  line and 2% on the exposure line.
- Preserve the current font-size ratios and information-area height.
- Fit calculations must include letter spacing so long camera and lens names
  continue to shrink rather than overflow.
- Remove Inter files and references from the wheel, documentation, tests, and
  third-party notices.

## Apple Branding

- Add `Apple` with slug `apple` to the brand registry.
- Recognize common EXIF make values including `Apple` and
  `Apple Computer, Inc.`.
- Bundle the Apple SVG from the same pinned Simple Icons 16.21.0 source used by
  the other applicable brand assets.
- Generate a transparent white runtime PNG.
- Permit `--logo-dir` override through a lowercase `apple.png`.
- Use EXIF `Model` and `LensModel` for the first line, for example:

  ```text
  Shot on iPhone 17 Pro · iPhone 17 Pro back camera
  ```

- Continue displaying ISO, aperture, shutter speed, and focal length from the
  existing EXIF parser.
- If an Apple JPEG has incomplete or stripped EXIF, omit only the missing
  fields under the existing fallback rules.

## Verification

- Add Apple manufacturer-alias and bundled-asset tests.
- Add letter-spacing measurement and rendering tests.
- Update the visual smoke test to exercise Jost.
- Update README and third-party notices.
- Rebuild sdist and wheel and verify that:
  - both Jost font weights are present;
  - Inter is absent;
  - Apple SVG and PNG are present;
  - the installed command renders an Apple-tagged JPEG successfully.

