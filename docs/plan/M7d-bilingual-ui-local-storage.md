# M7d — Bilingual UI and Local Project Storage Foundation

## Scope
- Add a persistent English (EN) / Burmese (MY) UI language preference, selectable from the top bar and Settings.
- Localize the workspace shell, settings, workflow pages, and Character Creator labels/messages while keeping character dialogue language independent.
- Preserve existing dark/light theme behavior and browser character bundle compatibility.
- Document the existing Python project workspace and the missing desktop bridge honestly.

## Current architecture evidence
- `apps/desktop-prototype` is static HTML/CSS/Vanilla JS and can be opened directly in a browser.
- `stilla/media/workspace.py` provides a Python `ProjectWorkspace` with project-scoped JSON documents, bounded payloads, atomic writes, and basic symlink/path checks.
- No packaged desktop runtime, HTTP bridge, filesystem picker, or browser-to-Python transport currently exists.

## Security gates before enabling a desktop bridge
- Loopback-only listener, per-launch random capability token, strict Origin/Host checks, CSRF protection, bounded request bodies and timeouts.
- User-selected workspace root allow-list; no arbitrary path supplied by UI.
- Resolve every project/document path under its canonical project root; reject symlinks and traversal at operation time.
- Strict schemas and media MIME/size/hash validation; never execute imported workflows.
- Atomic writes plus optimistic concurrency/revision checks; safe conflict response instead of last-write-wins.
- Separate project IDs and storage roots; cross-project access tests.
- Restart/recovery, concurrent writer, malformed request, origin spoof, DNS-rebinding/Host header, symlink race and path traversal tests.

## Explicit non-goals in this stage
- Do not claim the browser prototype is a real desktop app or that browser-local Character Creator data is already stored in project folders.
- Do not change Bionic/Qwen settings, download models, call cloud APIs, or transfer user media.
- Do not expose ComfyUI reference conditioning until installed workflows/nodes are inventoried and tested locally.
- Do not claim user-PC or GPU acceptance from CI.

## Acceptance
- EN and MY selectable from every page without reload; preference survives refresh.
- Both language controls remain synchronized; English remains the default and fallback.
- Dynamic page rendering and Character Creator rerenders remain translated.
- Node syntax checks, Python test suite, Ruff and Vercel preview pass.
- Manual Windows visual review remains required before production-ready status.
