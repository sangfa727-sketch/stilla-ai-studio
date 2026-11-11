# M7c — Versioned Storyboard Character Binding

- Status: domain contract implemented; desktop UI and project persistence integration remain pending.
- Branch: `feat/m7c-storyboard-character-binding`
- Depends on: M7a Character DNA and M7b Character Creator.

## Delivered in this increment

- A versioned character snapshot stores the validated M7a profile alongside its revision number.
- A shot binding pins a specific shot to a character ID, exact profile revision, and SHA-256 identity fingerprint.
- A storyboard document validates that every binding points to an existing shot and an embedded matching profile snapshot.
- Rebinding selected shots replaces only that character's binding on those shots; bindings for other characters and shots remain unchanged.
- Reusing a revision number with different identity data is rejected. A new revision can be added without rewriting older shot bindings.
- Shot prompt compilation resolves only the snapshots explicitly bound to that shot. Missing or inconsistent data fails closed.
- Serialization uses strict field allow-lists and bounded snapshot/binding counts.

## Data integrity decisions

The exact profile snapshot is embedded in the storyboard binding document. This deliberately avoids resolving a historical shot against the mutable "current character" record. The fingerprint is recomputed from the validated profile and compared at load/compile time.

A profile revision is an application-level sequence number supplied by the caller; this module does not silently invent or increment revisions. Callers must allocate revisions monotonically and persist the returned document as part of the project transaction.

## Not yet connected

- The browser Character Creator still stores profiles in browser localStorage only.
- The desktop prototype has no local application API or filesystem bridge.
- The storyboard binding document is JSON-serializable but is not yet read/written through the project workspace storage layer.
- No UI selector, storyboard editor, generation queue, ComfyUI workflow, or GPU inference is connected.
- This does not prove reference-conditioned identity consistency or pixel-identical generation.
- No cloud provider or model download is used.

## Next integration gate

1. Select/establish the desktop runtime and a loopback-only local application API.
2. Add atomic, project-relative persistence for the bound storyboard document and reference assets, including symlink/path traversal checks.
3. Connect Character Creator to the local API while preserving browser export/import compatibility.
4. Add storyboard UI selection and display the exact revision/fingerprint pinned to each shot.
5. Add browser/API end-to-end tests for project isolation, concurrent edits, restart recovery, and failed writes.
6. Verify installed ComfyUI nodes and workflow capabilities before exposing any reference-conditioning action.

Do not mark M7c production-ready until the local desktop runtime, durable project persistence, UI/API round trip, and real local provider acceptance tests pass.
