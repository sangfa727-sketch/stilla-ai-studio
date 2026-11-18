# M7l-B — Desktop ComfyUI Capability Report UI

## Scope

M7l-B exposes the already-implemented M7l-A read-only capability inspector in the Windows desktop Settings page. It displays the detected ComfyUI version, bounded node-class count, exact supported IPAdapter and InstantID class names, required sockets, schema validity, and missing/partial states.

The report is informational only. `generation_ready=false`. The UI rejects malformed reports and any report that claims generation readiness.

## Local-only boundary

- The operation is available only through the existing PyWebView desktop bridge.
- It accepts the same validated loopback-only ComfyUI base URL as M7j.
- It reads only `/system_stats` and `/object_info`.
- Redirects remain disabled and the response reader remains bounded.
- No prompts, workflows, image data, model paths, or project media are sent.
- No custom nodes or models are installed, downloaded, updated, or reconfigured.
- Browser preview does not attempt to access the user's local ComfyUI service.

## UI and safety

- All server-derived node names and socket names are rendered through DOM `textContent`, never HTML parsing.
- The UI validates report shape, status enums, node counts, and the mandatory `generation_ready=false` flag.
- The operation is read-only and does not change project documents, character identity revisions, Storyboard bindings, or browser-local data.
- English and Burmese labels are provided.
- The Settings grid collapses using the existing mobile breakpoints; this is code-level responsive support, not physical-device acceptance.

## Automated acceptance

Run:

```powershell
python -m pytest tests/test_comfyui_capabilities.py tests/test_comfyui_diagnostics.py tests/test_comfyui_capabilities_api.py -q
python -m pytest
ruff check .
node --check apps/desktop-prototype/comfyui-capabilities-ui.js
node --check apps/desktop-prototype/desktop-bridge.js
node --test tests/js/*.test.js
```

Tests use fake ComfyUI catalogs and a fake PyWebView bridge. They do not prove that the user's installed ComfyUI node pack is compatible.

## Windows laptop acceptance — required before M7l-C

1. Start the user's existing ComfyUI exactly as currently configured.
2. Launch STILLA Desktop and open **Settings → ComfyUI**.
3. Keep the existing local endpoint (`http://127.0.0.1:8188`, unless the user's current setting differs).
4. Run **Inspect installed conditioning nodes**.
5. Record the displayed ComfyUI version, IPAdapter/InstantID status, exact class names, required sockets, and missing nodes.
6. Do not install or update nodes to make the report green.

If the report is partial or unsupported, M7l-C must remain blocked until an explicit, reviewed adapter plan is written for the exact installed schema. Unknown node names must not be guessed or fuzzy-matched.

## Next gate

M7l-C may compile a workflow only after the real laptop capability report is reviewed. Workflow compilation must remain separate from generation approval and must pin the exact character revision and reference asset digests. A future generation action must require explicit user confirmation and must not be triggered by capability discovery.
