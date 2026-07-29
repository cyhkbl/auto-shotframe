# TIFF Input Design

Date: 2026-07-29
Status: Approved

## Goal

Accept common camera-exported TIFF photos while keeping the existing
social-ready JPEG output workflow. Lossless TIFF output is explicitly out of
scope.

## Supported Input

- Accept `.tif` and `.tiff` case-insensitively for single-file and directory
  input.
- Decode with Pillow's built-in TIFF/libtiff support and introduce no new
  runtime dependency.
- Process only the first image in a multi-page TIFF.
- Apply TIFF orientation before sizing and framing.
- Convert decoded input to 8-bit RGB for the current rendering pipeline.

Unsupported compression variants and damaged files follow the existing failure
behavior: report the file and continue processing the rest of a directory.

## Metadata

TIFF often exposes EXIF through TIFF IFD mappings rather than
`image.info["exif"]`. When raw EXIF bytes are absent:

1. read Pillow's `Image.getexif()` mapping;
2. serialize it to EXIF bytes;
3. feed those bytes into the existing metadata extraction and sanitization
   functions.

This keeps recognized camera, lens, exposure, and ICC information where
available. The existing privacy rules continue removing GPS, serial numbers,
MakerNote, unique ID, and owner name from the JPEG output.

## Output

- Always create a sibling JPEG such as `photo_framed.jpg`.
- Keep the default social-ready final-canvas long edge of at most 2160 pixels.
- Keep `-o/--original-size` as pixel-size preservation only.
- A 16-bit TIFF is converted to 8-bit RGB and is therefore not lossless.
- Never modify the source TIFF.

## Alternatives Considered

1. **Pillow TIFF support — selected.** It covers the intended 8-bit JPEG output
   without adding a dependency.
2. Add `tifffile`. This is stronger for scientific, multi-page, and high-bit
   TIFF workflows but unnecessary when the output is flattened 8-bit JPEG.
3. Run external `exiftool`. This has broad metadata support but would introduce
   a non-Python system dependency and complicate cross-platform installation.

## Verification

- Test `.tif` and `.tiff` discovery.
- Test TIFF IFD make, model, orientation, and output EXIF dimensions.
- Test a 16-bit TIFF can produce an 8-bit JPEG.
- Test only the first frame of a multi-page TIFF is used.
- Test the source remains byte-for-byte unchanged and output GPS is removed.
- Run the full JPEG and HEIF regression suite.
- Update both README languages, package description, and keywords.
- Build and clean-install the release candidate before PyPI publication.
