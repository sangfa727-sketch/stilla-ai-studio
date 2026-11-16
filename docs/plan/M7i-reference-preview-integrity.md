# M7i — Desktop Reference Preview and Asset Integrity

## Scope

- Add a narrow PyWebView bridge method that loads one reference image only when its asset ID is present in the selected project's current character profile.
- Restrict previews to the canonical project-local path `characters/references/<character_id>/<asset_id>.<extension>`; never accept a filesystem path from JavaScript and never return a local path.
- Open assets as regular files without following symlinks where the platform supports `O_NOFOLLOW`; verify the file size, image container, declared dimensions, and stored SHA-256 before returning a data URL.
- Parse PNG IHDR, JPEG SOF, and WebP VP8/VP8L/VP8X dimensions with the standard library. Reject missing/truncated headers, dimensions over 10,000 pixels on either side, or more than 40 million pixels.
- Use Pillow's `verify()` plus a second full `load()` pass before a new desktop reference is committed or previewed. Keep the embedded browser's native `Image.decode()` check before rendering and verify decoded dimensions against backend metadata. This is not a malware scanner and does not rewrite or sanitize source images.
- Keep preview data in a two-entry in-memory cache only; do not copy desktop image bytes into browser localStorage or upload them to a cloud service.
- Preserve the existing browser localStorage format and decode browser-uploaded/bundled previews before accepting them.
- Correct the Character Creator's event handlers so create/select/search/save/import/remove/delete actions refresh the rendered workspace and rebind its event listeners. Previously, several handlers called the markup-producing `render()` function without applying the returned markup, leaving the visible view stale.
- Preserve character identity fields, immutable revision history, storyboard bindings, legacy bridge methods, and the existing Qwen/Bionic and ComfyUI configuration.

## Integrity and security

- The bridge accepts only validated project ID, character ID, and 32-character asset ID values.
- A reference must be present in that character's current validated profile; another project or character cannot use the asset ID to read a file.
- The stored path must match the canonical importer-owned directory and filename for the character. Symlinked directories/files, non-regular files, path escapes, extension mismatches, missing checksums, and digest mismatches fail closed.
- The response contains only a MIME type, data URL, size, digest, and bounded dimensions. It never exposes the workspace root or a filesystem path.
- Each preview is limited by the existing 10 MiB asset cap. Browser decoding additionally enforces a 10,000-pixel side limit and 40-megapixel budget.
- The backend performs container/header, dimension, and full pixel-decode validation through the optional Pillow image extra; the embedded browser performs an additional decode before rendering. No claim is made that this detects malware, steganography, or every polyglot file.
- Existing browser-only data remains browser-local. Desktop preview cache entries are transient memory and are not persisted.
- No model downloads, cloud APIs, user-media uploads, production deployment, or changes to Qwen2.5/Bionic, ComfyUI, local endpoints, model files, or runtime configuration.

## Acceptance tests

- Python tests cover PNG/JPEG/WebP metadata parsing, malformed/truncated headers, excessive dimensions, valid full decode, corrupt pixel streams, verified preview data URLs, project/character ownership, checksum mismatch, and symlink rejection.
- Transactional import fixtures use a structurally valid small PNG so the new dimension/header checks exercise real containers rather than signature-only bytes.
- Node tests cover bridge forwarding, accepted preview decode, invalid data URLs, browser decode errors, pixel limits, and Character Creator refresh behavior.
- Linux CI must install `.[dev,image]` and run the full Python suite, Ruff, JavaScript syntax checks, and all Node regression tests.
- Windows CI must install `.[dev,image]` and continue to run project-lock, revision, desktop workspace, image validation, and transactional reference tests.
- Vercel Preview must be Ready before merge approval is requested.
- Manual Windows acceptance remains required for PyWebView rendering, native dialogs, Burmese fonts, project restart recovery, two-window conflict behavior, and local GPU smoke tests. Phone browser viewport and physical-device acceptance remain user-side checks.

## Explicitly not included

- ComfyUI IP-Adapter, PuLID, InstantID, or other identity-conditioning workflow execution.
- Image metadata stripping, antivirus/malware scanning, or server-side pixel decoding.
- Automatic three-way character merge.
- Windows installer, Android/iOS native package, or offline phone project-folder persistence.
