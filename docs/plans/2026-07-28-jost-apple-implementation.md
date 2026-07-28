# Jost Typography and Apple Branding Implementation Plan

Date: 2026-07-28

## 1. Assets

- Download Jost Light and Regular from the pinned Google Fonts source.
- Bundle the OFL license and record source hashes.
- Remove Inter font files and notices.
- Add the pinned Apple SVG and regenerate all runtime PNG logos.

## 2. Branding

- Add Apple aliases and slug to the brand registry.
- Update custom-logo documentation.
- Extend parameterized brand and asset tests.

## 3. HEIF Input

- Add `pillow-heif>=1.5.0` and register its Pillow opener.
- Generalize input discovery and validation from JPEG-only to supported photo
  suffixes.
- Decode HEIC/HEIF primary images and reuse the existing JPEG output pipeline.
- Add Apple HEIF fixtures and integration tests.

## 4. Typography

- Add font-weight selection to the internal font loader.
- Add letter-spaced measurement and drawing helpers.
- Include tracking in font fitting and centering.
- Use Light with 4% tracking for the first line and Regular with 2% tracking for
  the exposure line.

## 5. Documentation and Tests

- Update README features, supported-logo list, and typography notes.
- Update third-party notices and checksums.
- Add unit coverage for tracked text measurement and Apple EXIF rendering.
- Run Ruff and the full pytest suite.

## 6. Release Artifacts

- Rebuild sdist and wheel.
- Run Twine checks and inspect wheel contents.
- Force-install the rebuilt wheel into a clean environment.
- Render an Apple-tagged HEIC and visually inspect the JPEG result.
- Replace the 0.1.0 deliverables and commit the implementation.
