# M7f — Storyboard Character Binding UI and Project Persistence

## Scope
- Add a dedicated character-binding workspace below Script & Storyboard.
- Load and save the versioned CharacterBoundShotPlan through the existing project-scoped desktop document bridge.
- Keep browser prototype data isolated by project in localStorage.
- Edit shot descriptions, duration and camera; add/remove shots; bind or unbind a saved character on an individual shot.
- Calculate canonical identity fingerprints with Web Crypto SHA-256 before creating a binding.
- Embed the exact validated character profile snapshot and revision in the storyboard document.
- Preserve other characters' bindings when one character is rebound or unbound.

## Integrity and safety
- Python remains authoritative: DesktopWorkspaceAPI validates every storyboard payload through CharacterBoundShotPlan.from_dict.
- No browser-supplied filesystem paths, provider calls, model downloads, ComfyUI workflow changes or external media transfer.
- Project ID scopes all desktop and browser persistence.
- Missing project, unavailable secure SHA-256, missing character or invalid shot data fail closed.
- Browser mode remains a prototype and does not claim durable desktop storage.
- Revision numbers are derived from local character metadata; embedded snapshots preserve the revision used by a saved shot. A durable current-profile revision ledger is a separate follow-up.

## Not included
- Cross-process locking, compare-and-swap writes, crash journal or multi-file transactions.
- Generation queue or ComfyUI reference conditioning.
- Reference image preview, asset garbage collection, Windows packaging or user-PC acceptance.

## Acceptance gates
- Python tests validate project-scoped storyboard round-trip and reject malformed binding documents.
- JavaScript syntax checks cover the new UI module and inline application script.
- CI must pass tests, Ruff and Vercel before requesting merge approval.
- Manual Windows acceptance must verify workspace selection, two-project isolation, restart persistence and Burmese UI rendering.
