# STILLA Studio Information Architecture

- Status: M1 proposal; validate through a clickable prototype and task-based usability checks.
- Product target: PC-first creator studio; Android will have a touch-first information architecture over shared project concepts, not a compressed copy of the desktop UI.
- Non-goal: a single long home page that exposes every feature at once.

## Primary navigation

1. **Projects** — recent projects, create/open/import, recovery notices, templates, storage location.
2. **Script & Storyboard** — brief, audience/platform, script versions, scene list, narration, shot notes, storyboard frames.
3. **Generate** — image/video generation requests, model/runtime selection, prompt controls, seed/settings when supported, queue and job detail.
4. **Edit Studio** — timeline editing, preview, media bin, tracks, clip properties, captions, audio, undo/redo.
5. **Assets & History** — searchable generated/imported assets, provenance, model and prompt metadata, prior job outcomes.
6. **Export** — target preset, resolution/frame rate/codec, destination, estimated size where available, validation, queue and completed exports.
7. **Settings** — appearance, language, model/runtime locations, performance, storage, privacy, shortcuts, diagnostics.

Each destination is a distinct route/workspace with its own information hierarchy. Do not place all tools in a vertically stacked dashboard. Projects is a launchpad, not the whole application.

## Navigation and state rules

- Keep the active project name and save/recovery state visible in the app shell.
- Show Local/Offline or Remote/Online state explicitly for the active capability; never infer offline capability from a generic green status.
- Preserve navigation context when opening an asset, generation job, or export detail; provide an obvious way back to its parent workflow.
- Deep-linkable internal routes should restore project and selected-item context where valid.
- Unsaved changes require clear save/discard/cancel handling. Destructive actions require confirmation and a recoverable undo path when feasible.
- Long-running tasks survive route changes and appear in a persistent task queue; task detail exposes progress, cancel/retry, logs safe for users, and a clear terminal outcome.
- Empty, loading, unavailable-model, insufficient-hardware, permission-denied, failed, and offline states must each explain the next useful action.
- Do not rely on color alone for status. Pair iconography with labels and accessible names.

## PC and Android boundaries

- Share project schema, workflow state, asset metadata, validation rules, and generation-job contracts.
- Keep platform navigation, input interactions, media adapters, model runtime adapters, and performance policies platform-specific.
- Desktop may use persistent side navigation, keyboard shortcuts, resizable work areas, and multi-track timeline.
- Android should use touch-sized controls, a simplified focused editing surface, explicit background-task behavior, and mobile-compatible model choices. Never promise that a desktop 7B model or desktop image/video model runs on a phone.

## Security and privacy boundaries

- UI validation is convenience only; the application core must validate paths, imported metadata, prompts, export destinations, and project schema.
- Project imports and media metadata are untrusted input. Never automatically execute embedded workflows or arbitrary scripts from a project.
- Local/remote provider choice must be explicit, and the UI must disclose when prompts/media leave the device.
- Do not put credentials in project files, logs, generated metadata, or source control.
- Display actual model/runtime availability and hardware constraints; do not present unsupported generation options as ready.

## Validation gates

Before declaring the IA accepted:
- Build a clickable prototype with all seven primary destinations.
- Test first-run project creation/import, script revision, generation failure/retry, timeline edit/undo, asset provenance lookup, export validation, and offline/unavailable-model recovery.
- Verify keyboard-only navigation, visible focus, labels, reasonable zoom behavior, and dark/light contrast.
- Record observed completion, error/recovery, and task-confusion evidence; do not claim usability success without test results.
