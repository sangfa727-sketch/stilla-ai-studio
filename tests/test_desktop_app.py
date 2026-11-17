from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from stilla.desktop import app as desktop_app
from stilla.desktop.app import prototype_entrypoint


def test_source_runtime_resolves_prototype_from_repository(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)

    prototype = prototype_entrypoint()

    assert prototype.name == "index.html"
    assert prototype.parent.name == "desktop-prototype"
    assert prototype.is_file()


def test_frozen_runtime_resolves_prototype_from_bundle_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prototype = tmp_path / "apps" / "desktop-prototype" / "index.html"
    prototype.parent.mkdir(parents=True)
    prototype.write_text("<!doctype html>", encoding="utf-8")
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)

    assert prototype_entrypoint() == prototype


def test_onedir_runtime_resolves_prototype_from_internal_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    executable_dir = tmp_path / "stilla-windows-desktop"
    prototype = (
        executable_dir / "_internal" / "apps" / "desktop-prototype" / "index.html"
    )
    prototype.parent.mkdir(parents=True)
    prototype.write_text("<!doctype html>", encoding="utf-8")
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    monkeypatch.setattr(
        sys, "executable", str(executable_dir / "STILLA-AI-Studio.exe")
    )

    assert prototype_entrypoint() == prototype


def test_missing_prototype_reports_checked_locations_on_separate_lines(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path / "_internal"), raising=False)
    monkeypatch.setattr(sys, "executable", str(tmp_path / "STILLA-AI-Studio.exe"))

    with pytest.raises(FileNotFoundError, match="Checked locations") as error:
        prototype_entrypoint()

    assert "\n  - " in str(error.value)
    assert "\\n  - " not in str(error.value)


def test_main_starts_edge_webview_with_local_http_server(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prototype = tmp_path / "apps" / "desktop-prototype" / "index.html"
    prototype.parent.mkdir(parents=True)
    prototype.write_text("<!doctype html>", encoding="utf-8")
    window = object()
    calls: dict[str, object] = {}

    class FakeAPI:
        def _attach_window(self, attached_window: object) -> None:
            calls["attached_window"] = attached_window

    def create_window(title: str, **kwargs: object) -> object:
        calls["window_title"] = title
        calls["window_options"] = kwargs
        return window

    def start(**kwargs: object) -> None:
        calls["start_options"] = kwargs

    monkeypatch.setattr(desktop_app, "prototype_entrypoint", lambda: prototype)
    monkeypatch.setattr(desktop_app, "DesktopWorkspaceAPI", FakeAPI)
    monkeypatch.setitem(
        sys.modules,
        "webview",
        SimpleNamespace(create_window=create_window, start=start),
    )

    desktop_app.main()

    assert calls["window_title"] == "STILLA AI Studio"
    assert calls["attached_window"] is window
    assert calls["window_options"]["url"] == f"{prototype.as_uri()}?runtime=desktop"
    assert calls["start_options"] == {
        "gui": "edgechromium",
        "debug": False,
        "http_server": True,
    }
