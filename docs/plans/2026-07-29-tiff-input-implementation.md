# TIFF Input Implementation Plan

Date: 2026-07-29
Design: `docs/plans/2026-07-29-tiff-input-design.md`

## Objective

Add `.tif` and `.tiff` as supported inputs without changing the existing
share-ready JPEG output contract or adding a runtime dependency.

## Tasks

1. Extend input discovery and CLI copy to include TIFF.
2. Add a metadata fallback that serializes Pillow's `getexif()` mapping when
   `image.info["exif"]` is absent.
3. Keep only the first TIFF frame, preserve the embedded ICC profile, and
   convert the oriented image to 8-bit RGB before rendering.
4. Add tests for suffix discovery, IFD metadata, orientation, 16-bit input,
   first-frame behavior, source preservation, privacy sanitization, and batch
   failure isolation.
5. Update English and Chinese documentation, package description, keywords,
   and module copy.
6. Run formatting, linting, the complete test suite, package build, artifact
   inspection, and a clean virtual-environment install smoke test.
7. Commit and push the verified release candidate before resuming the PyPI
   0.1.0 release workflow.

## Orientation Note

Pillow's TIFF loader calls `ImageOps.exif_transpose(..., in_place=True)` at the
end of loading and removes the Orientation tag. The application's existing
`ImageOps.exif_transpose()` call is still retained as a format-independent
safety step. A pixel-direction integration test will ensure the TIFF path is
transposed exactly once.

## Done When

- JPEG, HEIC, HEIF, TIF, and TIFF inputs pass the same CLI workflow.
- TIFF camera metadata appears in the frame where Pillow exposes it.
- Exported JPEG metadata follows the existing privacy policy.
- The source TIFF remains byte-for-byte unchanged.
- The wheel and source distribution contain the documented runtime assets and
  install successfully in a clean environment.
