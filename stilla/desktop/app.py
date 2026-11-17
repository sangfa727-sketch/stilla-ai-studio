"""Optional PyWebView desktop entry point.

Run from source with: python -m stilla.desktop.app
Install the desktop runtime with: pip install -e ".[desktop]"
"""
from __future__ import annotations

import sys
from pathlib import Path

from stilla.desktop.workspace_api import DesktopWorkspaceAPI


def prototype_entrypoint() -> Path:
    """Resolve the UI from source or supported PyInstaller one-folder layouts."""
    relative_ui = Path("apps") / "desktop-prototype" / "index.html"
    candidates: list[Path] = []

    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        candidates.append(Path(bundle_root) / relative_ui)

    executable_dir = Path(sys.executable).resolve().parent
    candidates.extend(
        (
            executable_dir / "_internal" / relative_ui,
            executable_dir / relative_ui,
        )
    )

    if not bundle_root:
        source_root = Path(__file__).resolve().parents[2]
        candidates.append(source_root / relative_ui)

    checked: list[Path] = []
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved not in checked:
            checked.append(resolved)
            if resolved.is_file():
                return resolved

    locations = "\n".join(f"  - {path}" for path in checked)
    raise FileNotFoundError(
        "STILLA desktop UI (apps/desktop-prototype/index.html) was not found. "
        "Keep the complete _internal folder beside STILLA-AI-Studio.exe. "
        f"Checked locations:\n{locations}"
    )


def main() -> None:
    try:
        import webview
    except ImportError as exc:
        raise SystemExit(
            'PyWebView is optional. Install it with: pip install -e ".[desktop]"'
        ) from exc

    try:
        prototype = prototype_entrypoint()
    except FileNotFoundError as exc:
        raise SystemExit(str(exc)) from exc

    api = DesktopWorkspaceAPI()
    window = webview.create_window(
        "STILLA AI Studio",
        url=f"{prototype.as_uri()}?runtime=desktop",
        js_api=api,
        width=1440,
        height=900,
        min_size=(900, 640),
        text_select=True,
    )
    api._attach_window(window)

    # Force WebView2 on Windows; the default backend may import WinForms/pythonnet
    # before falling back, which can fail in a frozen one-folder package.
    # Serve bundled UI, CSS, and JavaScript through pywebview's loopback HTTP server.
    # Direct file:// navigation is unreliable in packaged Windows WebView2.
    webview.start(gui="edgechromium", debug=False, http_server=True)


if __name__ == "__main__":
    main()
