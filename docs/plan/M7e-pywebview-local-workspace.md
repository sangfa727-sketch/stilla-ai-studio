# M7e — PyWebView Runtime and Local Workspace Bridge

## Decision

Use PyWebView as the first Windows desktop host for the existing HTML/CSS/vanilla-JS
prototype. Keep the Python application core as the persistence boundary. The runtime
is an optional dependency and does not replace the browser prototype or add a web server.

## Included in this slice

- Optional desktop dependency extra and python -m stilla.desktop.app entry point.
- Narrow JavaScript bridge: runtime info, native workspace-directory picker, project
  listing/creation, allow-listed project documents, validated character profile
  persistence, and native image picker/import.
- All project paths are derived from a selected workspace and validated project ID.
  JavaScript cannot submit arbitrary filesystem paths.
- Imported reference images are bounded to 10 MiB and checked against PNG/JPEG/WebP
  file signatures. Files are stored under project-relative paths with SHA-256 metadata.
- Project documents are bounded to 2 MiB; storyboard data is validated against the
  existing versioned character-binding domain model.
- Existing .stilla-character.json import/export format is unchanged.

## Security and limitations

- The bridge exposes no arbitrary file read/write, shell, subprocess, or URL-opening method.
- Native dialogs, project ID validation, allow-listed document names, resolved-path
  containment, symlink checks, bounded JSON, atomic character writes, and exclusive
  asset creation reduce filesystem attack surface.
- The current workspace implementation uses process-local locking only. Cross-process
  locking, durable compare-and-swap revisions, crash-recovery journal, and complete
  multi-file transactions remain follow-up work; this slice must not claim them.
- Image signature validation is not a full decoder/semantic malware scan. The importer
  does not execute or render imported files.
- The Projects page now uses the native workspace/project API in PyWebView. Character
  profiles are loaded and saved in the selected project; native reference imports store
  project-relative files and SHA-256 metadata. Browser mode retains localStorage and
  migrates the legacy browser library once into the first selected project.
- Native reference previews are not yet rendered in the desktop UI. Removing a reference
  persists its profile metadata removal but leaves the old asset file orphaned; safe
  garbage collection is pending.
- The displayed character revision counter is cached in browser storage, not a durable
  revision-history ledger. Clearing browser storage can reset the displayed counter; the
  current Python profile file stores only the latest validated profile.
- Storyboard binding UI persistence is not yet wired. The underlying bridge can save and
  validate storyboard documents, but no UI workflow currently submits those snapshots.
- Actual Windows packaging, native dialog behavior, Burmese font QA, and GPU/local-model
  smoke tests require acceptance on the user's PC.
- No ComfyUI reference-conditioning node is enabled or assumed by this change.
- Existing Bionic/Qwen endpoint, model weights, and ComfyUI configuration are untouched.

## Acceptance

- CI: Python tests, Ruff, and prototype JavaScript syntax checks pass.
- Native runtime: optional dependency imports and launches on Windows.
- UI integration CI: desktop bridge, project selection, and character persistence code
  pass Python and JavaScript checks.
- Manual acceptance: choose a workspace, create two isolated projects, save/reload
  documents and character profiles, import valid and invalid images, restart and verify
  persistence, and confirm no external network/media transfer.
