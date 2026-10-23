# STILLA Studio Desktop Workspace Wireframe Specification

- Status: implementation-ready UX specification for the next prototype; visual styling remains open to usability testing.
- Target: desktop/PC first. The layout must scale to the user's 16 GB RAM / RTX 3050 6 GB class of machine and avoid implying every model fits locally.
- Design intent: premium, focused, professional creator tool with distinct workflow pages, not a one-page dashboard or a pile of unrelated cards.

## Application shell

### Global frame
- **Top bar:** STILLA identity, project switcher/name, save state, undo/redo, task-queue indicator, active Local/Offline or Remote/Online label, window-level actions.
- **Left navigation rail:** Projects, Script & Storyboard, Generate, Edit Studio, Assets & History, Export, Settings. Use icons plus readable labels; collapse only when a visible accessible expansion control is available.
- **Main workspace:** route-specific content. Each route owns its primary task and page-level actions.
- **Task queue drawer/panel:** persistent across route changes; shows queued/running/succeeded/failed/cancelled jobs. Each task has details and supported cancel/retry actions.
- **Notifications:** concise, non-blocking messages; important failures remain visible in task history and are not toast-only.

### Projects
- Project list/table with thumbnail, title, modified time, location, and recovery status.
- Primary actions: New project, Open project, Import media/project.
- A short “continue recent work” region is acceptable; do not embed script editor, generator, timeline, and export controls here.
- New project flow asks only for necessary details; advanced project settings remain optional.

### Script & Storyboard
- **Left:** scenes/outline with reorder and selection.
- **Center:** script editor and selected-scene content.
- **Right:** scene properties, narration/visual intent, duration, and optional generation guidance.
- Clear script version history and explicit revision actions.
- Storyboard frame generation is an explicit action; preview and metadata before accepting a frame into the project.
- Do not silently overwrite approved script text or storyboard frames.

### Generate
- Dedicated image/video creation workspace, not mixed into the editing timeline by default.
- **Main area:** prompt/brief and result preview/gallery for the selected job.
- **Settings inspector:** selected local model/runtime, dimensions/duration where supported, quality/steps where supported, seed when supported, output path, hardware-fit warning.
- **Queue area:** queued/running/finished/failed states, progress only when runtime provides meaningful progress, cancel/retry, safe error detail.
- Advanced graph/workflow mode is a later opt-in; beginner mode uses a guided form and safe defaults.
- Distinguish “model not installed”, “runtime unavailable”, “not enough memory/VRAM”, “unsupported feature”, and “job failed”.

### Edit Studio
- **Preview monitor:** prominent, aspect-ratio-aware playback/seek controls and safe preview scaling.
- **Media bin:** imported/generated assets, search/filter, duration/type, missing-media indicators.
- **Timeline:** separate video/audio/caption tracks, time ruler, snapping, clip trim/move, zoom/scroll, playhead, track visibility/lock.
- **Inspector:** context-sensitive clip/audio/caption properties for the selected item.
- **History:** undo/redo for editing operations; operations should be atomic and failure-safe.
- Keep export settings on the Export page, while showing a clear route/action to open Export.
- Keyboard shortcuts must be discoverable and never the only way to perform an operation.

### Assets & History
- Searchable assets and jobs with type, source, created time, status, and project association.
- Preserve prompt/model/version/seed and generation settings when the runtime supplies them.
- Clearly distinguish imported media from generated output and avoid claiming provenance that is unavailable.
- Failed jobs show a readable reason, retry eligibility, and links to related input/output where safe.

### Export
- Preset and custom settings are distinct, understandable choices.
- Show only codecs and settings supported by the installed export engine.
- Validate missing media, invalid destination, unsupported settings, and disk-space concerns where detectable before starting.
- Queue export as a job; allow cancellation when supported and clearly identify partial output cleanup behavior.
- Never imply a successful export until the file is verified to exist and basic metadata checks pass.

### Settings
- Group settings by General, Appearance, Language, Models & Runtimes, Storage, Performance, Privacy, Shortcuts, and Diagnostics.
- Show model paths and runtime health without silently moving or deleting user data.
- Include a “test connection” action for the configured local provider; show sanitized errors and a next step.
- Changes to paths or runtimes require validation and a clear cancel/restore option.

## Interaction and visual system

- Use a restrained premium palette, clear typographic hierarchy, consistent spacing, and purposeful motion; prioritize readability over decorative glass effects.
- Dark and light themes must both maintain contrast, visible focus, and legible disabled/error states.
- Prefer aligned work areas and contextual inspectors over excessive floating cards.
- Empty states explain how to begin; loading states preserve layout; error states state what happened and what can be done next.
- Use confirmation for destructive operations and provide undo/recovery where feasible.
- Autosave should expose saving/saved/error states and use atomic writes plus recovery snapshots in the core, not just a visual indicator.
- Respect keyboard navigation, screen scaling, and reduced-motion preferences.

## Acceptance checklist

- [ ] All seven primary destinations are separately navigable.
- [ ] Projects is a launchpad, not a giant all-features page.
- [ ] Edit Studio clearly separates preview, media bin, timeline, and inspector.
- [ ] Queue remains available across route changes.
- [ ] Local/Remote state is explicit and accurate.
- [ ] Model/runtime and hardware limitations are disclosed before jobs start.
- [ ] Failure, retry, cancel, and recovery states are represented.
- [ ] Dark/light themes and keyboard focus are specified.
- [ ] Core validates untrusted inputs independent of UI controls.
- [ ] A clickable prototype and task-based usability evidence are required before final UI acceptance.
