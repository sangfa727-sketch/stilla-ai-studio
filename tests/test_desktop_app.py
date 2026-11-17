from __future__ import annotations

import sys
from pathlib import Path

import pytest

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


def test_missing_prototype_reports_all_checked_locations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path / "_internal"), raising=False)
    monkeypatch.setattr(sys, "executable", str(tmp_path / "STILLA-AI-Studio.exe"))

    with pytest.raises(FileNotFoundError, match="Checked locations"):
        prototype_entrypoint()
