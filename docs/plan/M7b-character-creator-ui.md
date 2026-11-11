# M7b — Character Creator and Library UI

- Status: browser UX prototype implemented; not production-connected.
- Branch: \`feat/m7b-character-creator-library-ui\`
- Depends on: M7a Character DNA / consistency core.

## Delivered

- Adds a dedicated Character Creator workspace to the existing desktop prototype navigation.
- Captures the M7a profile fields: identity, visual anchors, original comedy personality, voice description, language, and optional canonical seed.
- Provides a searchable character library with create, edit, revision increment, explicit delete confirmation, and profile selection.
- Imports PNG, JPEG, and WebP reference images (512 KiB maximum each; up to 20 per character) and displays local previews.
- Exports and imports versioned \`.stilla-character.json\` bundles, including reference previews, for backup and transfer between browser profiles.
- Copies a compact identity brief for manual use in the current story workflow.
- Uses responsive layouts and existing dark/light theme variables.

## Storage and safety boundary

This is a clickable browser prototype, not the connected desktop application. Profiles and image previews are held in browser \`localStorage\` under \`stilla.character-library.v1\`, with a 3 MiB total payload guard and a 30-character cap. Browser storage can be cleared by the user or browser; export bundles are the backup mechanism.

Reference paths in the profile are project-relative placeholders. The prototype does not write files into a STILLA project folder, does not call the Python character library, and does not upload media anywhere. Imported bundle data is treated as untrusted; preview data URLs are restricted to base64 PNG/JPEG/WebP. Delete is confirmation-gated.

## Explicitly not implemented

- No image generation or automatic visual analysis.
- No generated turnaround / expression sheet.
- No ComfyUI IP-Adapter, PuLID, InstantID, ControlNet, or other reference-conditioning adapter is claimed or invoked.
- No Storyboard/shot-plan binding or automatic prompt injection.
- No guarantee of pixel-identical identity across arbitrary generation models.
- No desktop filesystem bridge or project-folder persistence.

## Acceptance and next integration gates

- [ ] Verify the page in a real browser at desktop and mobile widths.
- [ ] Test create/edit/revision, refresh persistence, reference import/remove, export/import, quota failure, and confirmed deletion.
- [ ] Add browser-level automated tests when the desktop shell/test runner is selected.
- [ ] Connect the UI to a local application API backed by the validated M7a schema and safe project workspace.
- [ ] Copy approved references into project-local assets with content hashes and safe path validation.
- [ ] Verify the installed ComfyUI workflow and node availability before enabling reference-sheet generation or identity-conditioned generation.
- [ ] Bind the selected character to story scenes and persist the exact profile revision / fingerprint used by each shot.
