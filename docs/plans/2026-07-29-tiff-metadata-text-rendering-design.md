# TIFF Metadata and Text Rendering Design

Date: 2026-07-29
Status: Approved

## Context

Two real Sony ILCE-7CR TIFF exports exposed two independent issues:

1. The frame displayed camera and exposure data correctly, but the exported
   JPEG omitted EXIF because TIFF `FileSource` and `SceneType` values were
   serialized as integers that `piexif.dump()` rejects.
2. Text looked soft on a bright information background because an intended
   translucent black stroke was drawn directly into an RGBA canvas and then
   converted to RGB. The conversion discarded alpha and left a solid black
   outline.

## Metadata Design

Metadata extraction for frame copy remains unchanged. Before writing JPEG EXIF:

- discard `FileSource` and `SceneType`;
- discard TIFF image-layout fields such as bit depth, compression, strip
  offsets, strip byte counts, and other source-image storage details;
- discard XMP, IPTC, and Photoshop ImageResources;
- discard the TIFF EXIF offset and embedded ICC tag because JPEG EXIF offsets
  are rebuilt and ICC is already written through the JPEG ICC segment;
- continue discarding GPS, serial numbers, MakerNote, image unique ID, owner
  name, thumbnails, and other existing privacy-sensitive fields;
- preserve useful photographic EXIF such as make, model, lens, exposure,
  capture time, focal length, and metering data;
- set Orientation to 1 and update output pixel dimensions.

The known Pillow warning for malformed multi-entry TIFF tag 33723 is suppressed
only while loading TIFF input and only for that exact warning. Other decoding
warnings and failures remain visible.

## Text Rendering Design

Keep Jost, current font sizes, weights, tracking, and layout. Draw text into a
transparent RGBA overlay, then alpha-composite that overlay onto the opaque
canvas. The existing one-pixel black stroke remains at its intended partial
opacity instead of becoming solid black during RGB conversion.

This keeps text readable on bright backgrounds without adding a panel or
changing the visual identity.

## Alternatives Considered

1. **Destination-safe filtering plus correct alpha compositing — selected.**
   It fixes both real files while preserving useful photographic metadata and
   the existing visual design.
2. Normalize only `FileSource` and `SceneType`. This is smaller but retains
   TIFF-only, XMP, IPTC, and Photoshop payloads that do not belong in the social
   JPEG output.
3. Use a strict EXIF allowlist and remove the text stroke entirely. This is
   predictable but would drop more metadata than requested and reduce text
   contrast on bright backgrounds.

## Verification

- Add a sanitizer regression test containing Sony-style integer
  `FileSource`/`SceneType` values and TIFF-only fields.
- Confirm useful camera and exposure EXIF remains while discarded fields are
  absent.
- Add a rendering test proving the translucent stroke is blended rather than
  converted to pure black.
- Run all existing JPEG, HEIF, TIFF, privacy, sizing, and visual tests.
- Reprocess both 150 MB Sony TIFF files and verify:
  - no tag 33723 warning is printed;
  - text is visually sharper at 100%;
  - output JPEG contains sanitized EXIF and the original ICC profile;
  - source TIFF files remain untouched.
