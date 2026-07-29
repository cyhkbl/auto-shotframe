# Opaque Typography Implementation Plan

Date: 2026-07-29
Design: `docs/plans/2026-07-29-opaque-typography-design.md`

## Tasks

1. Update the visual regression to require fully opaque, stroke-free text.
2. Use Jost weight 400 for every information text line.
3. Keep the existing first-line and second-line font-size ratios and tracking.
4. Render light-white text with full opacity and zero stroke width.
5. Run Ruff, the complete test suite, and package checks.
6. Reprocess both supplied Sony TIFF files, verify metadata and source
   preservation, and inspect 100% text crops.
7. Commit and push the verified change to GitHub.

## Done When

- No intentional transparency or outline remains in information text.
- Both lines use Jost 400 while retaining their existing size hierarchy.
- Horizontal and vertical Sony examples look crisp at 100%.
- Existing metadata and format behavior remains unchanged.
