# Social Output and First Release Implementation Plan

Date: 2026-07-28

## 1. Add Output-size Tests

- Test final-canvas fitting for landscape and portrait photos.
- Test that already-small photos are not enlarged.
- Test that `-o` preserves the current original-size canvas.
- Test `--max-long-edge`, quality resolution, and mutual exclusion.

## 2. Implement Target-first Rendering

- Add a helper that calculates the source size required for a maximum framed
  long edge.
- Apply orientation before sizing.
- Resize the source with Lanczos before calling `render_frame`.
- Resolve quality to 92 for social mode and 95 for original-size mode unless the
  user passes `--quality`.
- Keep save, metadata, and collision behavior unchanged.

## 3. Add Chinese Documentation and Package Metadata

- Write `README.zh-CN.md` with feature, installation, usage, privacy, HEIF, and
  social-sizing sections.
- Add reciprocal language links.
- Update English usage and option documentation.
- Include the Chinese README in the sdist.
- Add project URLs for GitHub and issue reporting.

## 4. Visual and Automated QA

- Run Ruff and all tests.
- Render the supplied iPhone photo in default, original-size, and custom
  long-edge modes.
- Produce a comparison image and record dimensions and file sizes.
- Build wheel and sdist, run Twine, and inspect included assets and metadata.
- Install the wheel in a clean environment and process JPEG and HEIF inputs.

## 5. Commit, Push, and Publish

- Commit implementation and verification updates.
- Push `main`.
- Configure or verify the pending PyPI Trusted Publisher.
- Publish GitHub release `v0.1.0`.
- Monitor the publish workflow.
- Verify the PyPI page and install version 0.1.0 from the public index.
