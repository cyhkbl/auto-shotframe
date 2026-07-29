# TIFF Metadata and Text Rendering Implementation Plan

Date: 2026-07-29
Design: `docs/plans/2026-07-29-tiff-metadata-text-rendering-design.md`

## Tasks

1. Add a focused TIFF-load helper that suppresses only Pillow's known tag 33723
   multi-entry warning.
2. Refactor EXIF sanitization so TIFF storage, XMP, IPTC, Photoshop,
   `FileSource`, and `SceneType` fields are removed before `piexif.dump()`.
3. Preserve the existing photographic EXIF fields, privacy removals,
   Orientation reset, output dimensions, and separate ICC handling.
4. Draw all textual elements on a transparent overlay and alpha-composite the
   overlay onto the frame before converting to RGB.
5. Add unit and integration regressions for Sony-style TIFF EXIF values,
   structural-field removal, warning suppression, ICC preservation, and
   non-black translucent text strokes.
6. Update both README languages to document that TIFF-only metadata containers
   are not copied to the JPEG.
7. Run Ruff, the complete test suite, package build checks, and clean-install
   smoke tests.
8. Reprocess both supplied Sony TIFF files, inspect 100% text crops, verify
   output EXIF/ICC, then commit and push the result.

## Done When

- Both supplied Sony TIFF files process without the tag 33723 warning.
- Their JPEGs contain useful sanitized EXIF and the original ICC profile.
- `FileSource`, `SceneType`, TIFF layout fields, XMP, IPTC, and Photoshop
  resources are absent.
- Text no longer has a solid black halo on bright backgrounds.
- Existing JPEG and HEIF behavior remains covered by passing tests.
