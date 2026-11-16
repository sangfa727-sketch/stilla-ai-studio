"""Optional PyWebView desktop entry point.

Run from source with: python -m stilla.desktop.app
Install the desktop runtime with: pip install -e ".[desktop]"
"""
from __future__ import annotations

import sys
from pathlib import Path

from stilla.desktop.workspace_api import DesktopWorkspaceAPI


def prototype_entrypoint() -> Path:
    """Resolve the prototype from source or the PyInstaller one-folder bundle."""
    bundle_root = getattr(sys, "_MEIPASS", None)
    root = Path(bundle_root) if bundle_root else Path(__file__).resolve().parents[2]
    return root / "apps" / "desktop-prototype" / "index.html"


def main() -> None:
    try:
        import webview
    except ImportError as exc:
        raise SystemExit(
            'PyWebView is optional. Install it with: pip install -e ".[desktop]"'
        ) from exc

    prototype = prototype_entrypoint()
    if not prototype.is_file():
        raise SystemExit(f"Desktop prototype entry point not found: {prototype}")

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
    webview.start(debug=False)


if __name__ == "__main__":
    main()
