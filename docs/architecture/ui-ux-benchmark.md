# STILLA UI/UX Benchmark and Design Principles

- Status: Research baseline; validate against working prototypes before treating as final.
- Date: 2026-10-24
- Scope: PC-first desktop experience, with an architecture that can later support Android.
- Rule: Learn from public projects; do not copy their branding, layouts wholesale, or source code without license/provenance review.

## Reference projects and transferable lessons

### Shotcut — practical editing workspace
Reference: https://www.shotcut.org/
Strengths to study:
- Dockable panels let experienced editors arrange a workspace around their workflow.
- Clear separation between playlist/media, filters/properties, history, jobs/encoding, and preview.
- Broad media compatibility through FFmpeg/MLT-based capabilities.
Potential weakness / risk for STILLA:
- A panel-rich desktop interface can feel technical and intimidating to new creators.
STILLA decision:
- Ship a calm default workspace with a small number of named areas; keep advanced panels optional and searchable.
- Make export queue and current job state visible without requiring users to find a hidden panel.

### Kdenlive — professional timeline conventions
Reference: https://docs.kdenlive.org/en/
Strengths to study:
- Familiar editing workspace: project bin, clip monitor, project monitor, timeline, and customizable workspace layouts.
- Multi-track editing and keyboard shortcuts support efficient repeat work.
Potential weakness / risk:
- Customizable widgets and many controls can increase cognitive load for beginners.
STILLA decision:
- Preserve standard editing concepts and predictable shortcuts, but introduce them progressively.
- Provide a beginner workspace and an advanced workspace without maintaining two different editing engines.

### ComfyUI — power and workflow transparency
Reference: https://github.com/Comfy-Org/ComfyUI
Strengths to study:
- Explicit, reusable workflows and graph-based control for complex generation.
- Local-first execution, queueing, and advanced model controls.
Potential weakness / risk:
- A node graph exposes implementation detail and can be too complex for a simple prompt-to-result task.
STILLA decision:
- Use guided forms and sensible presets as the default. Offer a separate advanced workflow view only when an engine supports it.
- Show model requirements, queue state, progress, and failure details; never imply a job succeeded before the output is validated.

### InvokeAI — unified creative workspace
Reference: https://github.com/invoke-ai/InvokeAI
Strengths to study:
- Generation, canvas editing, galleries, metadata, and workflows share a creative workspace.
- Saved generation metadata helps users reproduce or remix results.
Potential weakness / risk:
- A unified workspace can become crowded if every tool is visible at once or panels compete for attention.
STILLA decision:
- Keep generated assets attached to the project/scene and preserve prompt, seed, model, settings, and provenance when available.
- Reveal advanced settings contextually; use clear project navigation and saved workspace presets.

### Cutaway — engine/UI separation
Reference: https://github.com/S07K/cutaway
Strengths to study:
- The project describes framework-independent engines, adapters, and presentation layers; the UI does not own core editing logic.
- Undo/redo, captions, preview, and export are treated as parts of a complete editing loop.
Potential weakness / risk:
- A browser-first architecture may not directly meet STILLA's Windows GPU-runtime and Android native-storage needs.
STILLA decision:
- Adopt the separation principle, not its entire technology stack. Keep domain logic and project formats independent of desktop UI and platform-specific media/runtime adapters.

## STILLA's proposed design principles

1. Workflow-first information architecture:
   - Create/Import
   - Script
   - Storyboard
   - Generate
   - Edit
   - Export
   Keep project navigation stable across these stages and allow users to revisit earlier stages without losing work.

2. One main action per screen:
   - Use a clear primary action and secondary actions with consistent hierarchy.
   - Avoid showing every model parameter, filter, and export option by default.

3. Preview before commitment:
   - Show editable AI drafts and preview settings before generating or exporting.
   - Confirm destructive operations; provide undo for reversible editing actions.

4. Durable project and asset history:
   - Autosave project state where safe, show save status, and recover after crashes.
   - Preserve prompt/model/settings/seed/source links for generated assets when supported.
   - Keep failed/cancelled outputs distinct from completed outputs.

5. Honest offline and hardware status:
   - Clearly label Local/Offline, Remote/Online, model-not-installed, insufficient-memory risk, and unavailable capabilities.
   - Do not offer a generation mode as available until the selected provider/model passes capability checks.
   - Explain whether a model must be downloaded before offline use.

6. Progressive disclosure:
   - Beginner mode uses presets, plain-language controls, and guided empty states.
   - Advanced mode exposes timeline precision, model controls, workflow graphs, and detailed diagnostics.
   - Do not hide essential status, errors, or privacy/network information.

7. Accessibility and internationalization:
   - Keyboard navigation and shortcuts; visible focus; adequate contrast; scalable text.
   - Avoid color-only status indicators; pair icons/colors with labels.
   - Use localization-ready layouts and test long translations, including Burmese and Thai.
   - Support reduced motion where practical.

8. Responsive PC-first layout:
   - Desktop: persistent project navigation, preview, inspector, timeline, and collapsible asset/job panels.
   - Small windows: panels collapse into drawers/tabs without losing current context.
   - Android: separate touch-first navigation and compact timeline controls; do not shrink the PC UI to phone size.

## Proposed initial desktop layout

- Top bar: project name, save state, undo/redo, hardware/local status, settings.
- Left rail: project assets, scenes, scripts, storyboard, generation history.
- Center: preview/canvas, contextual to the selected workflow stage.
- Right inspector: properties for the selected clip, scene, asset, or generation.
- Bottom: timeline in Edit stage; task queue/status can be opened without replacing the workspace.
- Global: searchable commands, clear empty states, visible errors, and keyboard shortcuts.

This is a starting hypothesis to validate with a clickable prototype and task-based tests, not a final locked design.

## Validation plan

Test representative users/tasks before locking the design:
- Import a clip and export a trimmed video without guidance.
- Create a script and revise one scene before accepting it.
- Generate an image and find its prompt/model/settings later.
- Recover from a failed generation and retry it.
- Determine whether a task is local/offline or remote/online.
- Find and correct an export setting.
Measure task completion, time, misclicks, recovery success, and user-reported confusion. Fix observed issues rather than treating visual polish as proof of usability.

## Licensing and reuse guardrails

- This document records design observations, not permission to copy code or assets.
- Before adopting any library, engine, model, icon pack, or source code, record the exact version, license, dependencies, redistribution obligations, and any attribution requirements.
- Prefer independent implementations of interaction principles when licensing or long-term maintenance is uncertain.
