# M7h — Transactional Character Reference Assets

## Scope

- Replace the desktop UI's two-step reference import + character save with one native bridge operation that imports the selected image and appends its metadata as a single immutable character revision.
- Preserve the existing import_character_reference bridge method for backward compatibility; the current Character Creator uses the new transactional method.
- Use the current character revision as a required compare-and-swap token so a stale window cannot attach an image to a newer profile.
- Persist a bounded, project-local transaction journal before writing the image and character revision.
- Recover interrupted operations under the project lock: retain an asset only when an immutable character revision references the exact project-relative path and SHA-256; otherwise remove the matching importer-owned asset.
- Run conservative orphan cleanup during desktop character-library loading. Only importer-owned PNG/JPEG/WebP files under characters/references/<character_id>/ are candidates. References present in any historical revision remain protected.
- Keep browser-only reference previews and localStorage behavior unchanged.
- Update the Windows CI job to exercise the desktop workspace API and reference transaction tests.

## Integrity and security

- The source file is opened as a regular file with O_NOFOLLOW where the platform supports it; a symbolic-link check is performed before opening.
- Native file picker only; JavaScript never supplies a filesystem path.
- Import limit remains 10 MiB; accepted formats remain PNG/JPEG/WebP signature checks with SHA-256 metadata. This is not a full image decoder or malware scan.
- A maximum of 20 references per character remains enforced by the existing schema and is checked before writing.
- The transaction journal has a strict schema, 4 KiB read bound, validated identifiers/extensions/checksums, and is stored under the selected project.
- The project lock serializes journal recovery, asset creation, revision-ledger commit, and cleanup across processes.
- Asset creation is exclusive and synced before the revision ledger is committed. If ledger commit fails, journal recovery removes only the matching uncommitted asset. If the process stops after the ledger commit, recovery verifies the immutable revision and keeps the asset.
- Corrupt journals, symlinks, mismatched checksums, and committed-but-missing assets fail closed and preserve evidence for manual recovery.
- Cleanup scans only the reserved importer directory and only recognized asset filenames. It never removes assets referenced by any immutable revision, including old revisions after a reference is removed from the current profile.
- Existing Qwen2.5/Bionic, ComfyUI, local endpoints, model files, and runtime configuration are not changed. No user media is uploaded and no cloud API/model download is introduced.

## Not included

- Desktop preview rendering for project-local references.
- Full PNG/JPEG/WebP decoding, metadata stripping, or content scanning.
- ComfyUI IP-Adapter/PuLID/InstantID or any other reference-conditioning integration.
- Automatic three-way merge for concurrent character edits.
- Windows installer packaging, phone-native app packaging, or physical-device acceptance.

## Acceptance gates

- Python tests cover atomic import and revision creation, stale-revision rejection, ledger-write rollback, interrupted pre-commit recovery, post-commit recovery, checksum validation, historical-reference retention, project isolation, invalid image rejection, and malformed-journal fail-closed behavior.
- Node regression tests verify the bridge forwards the expected revision and calls the transactional API.
- Linux CI runs the full Python suite, Ruff, JavaScript syntax checks, and browser-state tests.
- Windows CI runs project-lock, revision, desktop workspace API, and reference-transaction tests.
- CI and Vercel Preview must pass before merge approval is requested.
- Manual Windows acceptance remains required for PyWebView native dialogs, file permissions, Burmese font rendering, restart recovery, and two-window stale-save behavior.
