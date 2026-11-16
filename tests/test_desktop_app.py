from __future__ import annotations

import sys
from pathlib import Path

from stilla.desktop.app import prototype_entrypoint


def test_source_runtime_resolves_prototype_from_repository() -> None:
    prototype = prototype_entrypoint()

    assert prototype.name == "index.html"
    assert prototype.parent.name == "desktop-prototype"
    assert prototype.is_file()


def test_frozen_runtime_resolves_prototype_from_bundle_root(
    tmp_path: Path, monkeypatch
) -> None:
    prototype = tmp_path / "apps" / "desktop-prototype" / "index.html"
    prototype.parent.mkdir(parents=True)
    prototype.write_text("<!doctype html>", encoding="utf-8")
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)

    assert prototype_entrypoint() == prototype
