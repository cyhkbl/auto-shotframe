# Apple Shot-on Copy Design

Date: 2026-07-28
Status: Approved

## Goal

Make Apple/iPhone output read like finished photographic branding rather than a
literal dump of Apple's EXIF `LensModel` value.

## Decision

- For recognized Apple photos, render only the EXIF camera model in the first
  line, for example:

  ```text
  Shot on iPhone 15 Pro
  ```

- Never render Apple's EXIF `LensModel`, including values such as
  `iPhone 15 Pro back triple camera 6.765mm f/1.78`.
- If an Apple photo has no camera model, omit the `Shot on` line instead of
  falling back to its lens description.
- Keep ISO, aperture, shutter speed, and focal length in the exposure line.
- Keep camera-and-lens output unchanged for every non-Apple manufacturer.
- Preserve the source metadata fields in the sanitized output EXIF; this change
  affects display copy only.

## Alternatives Considered

1. **Hide Apple lens text entirely — selected.** This is stable across current
   and future iPhone EXIF wording and avoids duplicating focal length and
   aperture already shown below.
2. Strip only phrases such as `back triple camera`. This is fragile because
   Apple can change the wording, and the remaining focal-length text still
   duplicates the exposure line.
3. Translate Apple lens descriptions into labels such as `Main Camera`. This
   introduces assumptions about which physical camera produced the photo and is
   unnecessary for the intended clean presentation.

## Implementation

Make `PhotoMetadata.shot_on_line` brand-aware. Apple returns a model-only line;
all other brands continue joining camera and lens with a middle dot.

Add tests for:

- Apple with camera and lens metadata;
- Apple with only lens metadata;
- an existing non-Apple camera-and-lens result.

Regenerate the supplied iPhone 15 Pro preview and verify that the first line is
model-only while the exposure line is unchanged.
