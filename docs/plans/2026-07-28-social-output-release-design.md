# Social Output and First Release Design

Date: 2026-07-28
Status: Approved

## Goals

Prepare `auto-shotframe` 0.1.0 for photographs shared primarily to Xiaohongshu
and WeChat Moments, with Instagram as a secondary target. Avoid leaving a
roughly 6000-pixel framed image for a social platform to resize together with
its typography.

Also add Chinese documentation and publish the first release through PyPI
Trusted Publishing.

## Default Social Output

- Limit the final framed canvas to a 2160-pixel long edge by default.
- Never upscale an image whose framed canvas is already within that limit.
- Calculate the framed canvas size before rendering.
- When reduction is needed, resize the oriented source photo with Lanczos first.
- Render the blurred background, inset photo, logo, and Jost text only after the
  source reaches its final working size.
- Encode the result once as JPEG with 4:4:4 chroma sampling.
- Use JPEG quality 92 for the default social output.

The text cannot be stored separately from the photograph in a flattened JPEG.
Drawing it after the controlled source resize gives it clean edges at the
intended output scale and avoids an extra local resize of the completed frame.

## Original-size and Custom Output

- Add `-o` as a short alias for `--original-size`.
- Original-size mode bypasses the 2160-pixel limit and defaults to JPEG quality
  95.
- Original-size means no pixel resizing; it is not lossless because adding the
  frame still requires JPEG encoding.
- Add `--max-long-edge N` for an explicit final-canvas limit.
- `--max-long-edge` and `-o/--original-size` are mutually exclusive.
- `--quality N` overrides the mode-specific quality default.
- Reject non-positive `--max-long-edge` values with a clear CLI error.

## Metadata and Naming

Keep the current sibling naming, collision handling, orientation, ICC profile,
and privacy filtering. EXIF pixel dimensions must describe the reduced framed
output. The source file remains unchanged.

## Documentation

- Add a complete `README.zh-CN.md`.
- Put `English | 简体中文` navigation at the top of both README files.
- Include the Chinese README in the source distribution.
- Explain default social sizing, `-o`, custom long-edge sizing, and the
  distinction between original-size and lossless output.
- Add GitHub repository and issue-tracker links to package metadata.

## Verification

- Unit-test landscape, portrait, already-small, original-size, and invalid CLI
  cases.
- Run the existing JPEG and HEIF integration tests.
- Render the supplied iPhone photograph in default and original-size modes.
- Compare output dimensions, file sizes, metadata, and text crops.
- Run Ruff, pytest, package build, Twine checks, wheel-content inspection, and a
  clean wheel installation.

## Publication

- Release version `0.1.0`.
- Use the existing GitHub Actions workflow and PyPI Trusted Publishing.
- Configure a pending GitHub publisher for project `auto-shotframe`, owner
  `SeanYancy`, repository `auto-shotframe`, workflow `publish.yml`, and
  environment `pypi`.
- Publish a GitHub `v0.1.0` release only after all verification succeeds.
- Verify the PyPI project page and install `auto-shotframe==0.1.0` from PyPI in
  a fresh environment.
