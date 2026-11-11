"""Optional PyWebView desktop entry point.

Run with: python -m stilla.desktop.app
Install the optional runtime with: pip install -e ".[desktop]"
"""
from __future__ import annotations

from pathlib import Path

from stilla.desktop.workspace_api import DesktopWorkspaceAPI


def main() -> None:
    try:
        import webview
    except ImportError as exc:
        raise SystemExit(
            'PyWebView is optional. Install it with: pip install -e ".[desktop]"'
        ) from exc

    prototype = (
        Path(__file__).resolve().parents[2]
        / "apps"
        / "desktop-prototype"
        / "index.html"
    )
    if not prototype.is_file():
        raise SystemExit(f"Desktop prototype entry point not found: {prototype}")

    api = DesktopWorkspaceAPI()
    window = webview.create_window(
        "STILLA AI Studio",
        url=prototype.as_uri(),
        js_api=api,
        width=1440,
        height=900,
        min_size=(900, 640),
        text_select=True,
    )
    api.attach_window(window)
    webview.start(debug=False)


if __name__ == "__main__":
    main()
