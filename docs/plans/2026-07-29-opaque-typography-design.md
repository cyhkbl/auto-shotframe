# Opaque Typography Design

Date: 2026-07-29
Status: Approved

## Goal

Make frame information text look crisp at social-media output sizes, especially
on bright blurred backgrounds.

## Selected Design

- Use Jost Regular weight 400 for both information lines.
- Keep the first line at the current larger size and 4% tracking.
- Keep the second line at the current smaller size and 2% tracking.
- Render text as fully opaque light white.
- Remove the text stroke completely.
- Keep logo sizing, information-area height, spacing, background treatment, and
  all metadata copy unchanged.

The different font sizes preserve hierarchy even though both lines use the same
weight.

## Alternatives Considered

1. **Opaque Jost 400 with no stroke — selected.** This is the cleanest and
   sharpest treatment and stays close to the supplied references.
2. Opaque text with a solid one-pixel dark stroke. This improves contrast but
   reintroduces a visible outline and makes small text feel heavier.
3. Opaque text over a darker information background. This is readable but
   changes the overall frame mood more than necessary.

## Verification

- Add a pixel-level test proving the text area contains no dark stroke pixels.
- Keep existing layout, sizing, metadata, TIFF, JPEG, and HEIF tests passing.
- Reprocess the two supplied Sony TIFF files.
- Inspect horizontal and vertical 100% text crops.
- Verify the source TIFF files remain unchanged and output EXIF/ICC remains
  intact.
