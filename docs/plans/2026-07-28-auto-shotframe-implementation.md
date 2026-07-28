# auto-shotframe Implementation Plan

Date: 2026-07-28

## Stage 1: Package Skeleton

- Add `pyproject.toml` using Hatchling and a `src/` layout.
- Add MIT `LICENSE`, README scaffold, package initializer, and CLI entry point.
- Add development dependencies for pytest, Ruff, build, and Twine.
- Verify the editable install and `auto-shotframe --help`.

## Stage 2: Pure Functions

- Implement safe output-name selection and generated-file detection.
- Implement EXIF rational formatting, manufacturer normalization, and display
  metadata construction.
- Implement layout calculations from the source short edge.
- Cover these functions with unit tests before integrating image rendering.

## Stage 3: Assets and Branding

- Add Inter under the SIL Open Font License.
- Add seven manufacturer SVG sources and generated transparent PNG derivatives.
- Record asset origins, versions, hashes, and trademark disclaimer.
- Implement package-resource lookup and user-logo override precedence.

## Stage 4: Rendering

- Correct source orientation and normalize input image mode.
- Create a blurred, darkened cover background.
- Render shadow, foreground image, logo, and responsive metadata text.
- Preserve ICC data and write sanitized EXIF.
- Save through a temporary sibling and atomically rename on success.

## Stage 5: CLI and Batch Processing

- Accept one JPEG file or one directory.
- Expose the approved layout and quality overrides.
- Skip generated outputs and process directory files deterministically.
- Continue after per-file failures and print a concise summary.
- Implement exit codes 0, 1, and 2.

## Stage 6: Verification and Documentation

- Add integration and visual snapshot tests.
- Exercise horizontal, vertical, missing-EXIF, malformed-EXIF, and collision cases.
- Build sdist and wheel, run `twine check`, install the wheel in a clean virtual
  environment, and smoke-test the console command.
- Complete README usage, customization, privacy, asset, and release sections.
- Run Ruff and the full pytest suite.

## Stage 7: Release Preparation

- Add a cross-platform GitHub Actions test matrix.
- Add a PyPI trusted-publishing workflow that only runs on an explicit GitHub
  release.
- Do not create a remote repository or publish a package without explicit user
  approval.

