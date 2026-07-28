# Apple Shot-on Copy Implementation Plan

Date: 2026-07-28

## 1. Lock the Copy Rule with Tests

- Add an Apple metadata test whose camera and lens are both populated.
- Expect `Shot on iPhone 15 Pro`.
- Add an Apple lens-only fallback test and expect no first line.
- Retain the Nikon camera-and-lens expectation as a regression check.

## 2. Implement Brand-aware Display Copy

- Update `PhotoMetadata.shot_on_line`.
- Detect the normalized Apple brand by its stable `apple` slug.
- Use camera model only for Apple.
- Keep the current camera/lens join for every other brand.

## 3. Verify and Refresh Deliverables

- Run Ruff and the complete pytest suite.
- Process the supplied iPhone photo again.
- Verify Apple model-only copy, unchanged exposure values, sanitized GPS, and
  unchanged source bytes.
- Regenerate the eight-brand comparison so Apple reflects the new copy.
- Rebuild and check wheel and sdist, then update the release artifacts.
- Commit the implementation.
