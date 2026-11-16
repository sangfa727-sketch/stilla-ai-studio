from __future__ import annotations

import base64
import binascii
import hashlib
import struct
import sys
import zlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from stilla.desktop.workspace_api import DesktopAPIError, DesktopWorkspaceAPI


def _png() -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
        )

    header = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    pixels = zlib.compress(b"\x00\x20\x80\xc0\xff")
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", pixels) + chunk(b"IEND", b"")


def _profile() -> dict:
    return {
        "schema_version": 1,
        "id": "hero_01",
        "name": "Pip",
        "species_or_type": "original forest creature",
        "visual": {
            "silhouette": "round pear shape",
            "body_proportions": "large head, short body",
            "face_shape": "soft oval",
            "eyes": "large amber eyes",
        },
        "personality": {},
        "references": [],
        "voice_description": "",
        "language": "en",
        "canonical_seed": None,
    }


def _import_reference(
    api: DesktopWorkspaceAPI, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[str, dict, bytes]:
    project_id = api.create_project("Preview project")["id"]
    api.save_character_profile(project_id, _profile(), expected_revision=0)
    payload = _png()
    source = tmp_path / "reference.png"
    source.write_bytes(payload)

    class FakeWindow:
        def create_file_dialog(self, *_args, **_kwargs):
            return [str(source)]

    monkeypatch.setitem(
        sys.modules,
        "webview",
        SimpleNamespace(OPEN_DIALOG=1, FOLDER_DIALOG=2),
    )
    api._attach_window(FakeWindow())
    result = api.import_character_reference_and_save(project_id, "hero_01", 1)
    return project_id, result["reference"], payload


def _asset_path(api: DesktopWorkspaceAPI, project_id: str, reference: dict) -> Path:
    return api._workspace.root / "projects" / project_id / reference["relative_path"]


def test_preview_returns_only_checksum_verified_project_asset(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    api = DesktopWorkspaceAPI(tmp_path / "workspace")
    project_id, reference, payload = _import_reference(api, tmp_path, monkeypatch)

    result = api.load_character_reference_preview(
        project_id, "hero_01", reference["asset_id"]
    )

    assert result["asset_id"] == reference["asset_id"]
    assert result["mime_type"] == "image/png"
    assert result["width"] == 1
    assert result["height"] == 1
    assert result["size_bytes"] == len(payload)
    assert result["sha256"] == hashlib.sha256(payload).hexdigest()
    assert base64.b64decode(result["data_url"].split(",", 1)[1]) == payload
    assert "path" not in result
    assert "workspace_root" not in result


def test_preview_rejects_unknown_reference_and_other_project(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    api = DesktopWorkspaceAPI(tmp_path / "workspace")
    project_id, reference, _ = _import_reference(api, tmp_path, monkeypatch)
    other_project = api.create_project("Other project")["id"]
    api.save_character_profile(other_project, _profile(), expected_revision=0)

    with pytest.raises(DesktopAPIError, match="does not belong"):
        api.load_character_reference_preview(other_project, "hero_01", reference["asset_id"])
    with pytest.raises(DesktopAPIError, match="does not belong"):
        api.load_character_reference_preview(project_id, "hero_01", "f" * 32)


def test_preview_rejects_modified_asset_checksum(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    api = DesktopWorkspaceAPI(tmp_path / "workspace")
    project_id, reference, _ = _import_reference(api, tmp_path, monkeypatch)
    asset = _asset_path(api, project_id, reference)
    asset.write_bytes(_png() + b"tampered")

    with pytest.raises(DesktopAPIError, match="checksum"):
        api.load_character_reference_preview(project_id, "hero_01", reference["asset_id"])


def test_preview_rejects_symlinked_asset_without_reading_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    api = DesktopWorkspaceAPI(tmp_path / "workspace")
    project_id, reference, payload = _import_reference(api, tmp_path, monkeypatch)
    asset = _asset_path(api, project_id, reference)
    outside = tmp_path / "outside.png"
    outside.write_bytes(payload)
    asset.unlink()
    try:
        asset.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation unavailable on this platform")

    with pytest.raises(DesktopAPIError, match="unsafe"):
        api.load_character_reference_preview(project_id, "hero_01", reference["asset_id"])
