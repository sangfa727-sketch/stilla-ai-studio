from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from stilla.characters.revisions import load_character_revision_ledger
from stilla.desktop.workspace_api import DesktopAPIError, DesktopWorkspaceAPI


def _profile(name: str = "Pip") -> dict:
    return {
        "schema_version": 1,
        "id": "hero_01",
        "name": name,
        "species_or_type": "original small forest creature",
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


def _project(api: DesktopWorkspaceAPI) -> str:
    return api.create_project("Reference transaction project")["id"]


def _attach_picker(
    api: DesktopWorkspaceAPI,
    image: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeWindow:
        def create_file_dialog(self, *_args, **_kwargs):
            return [str(image)]

    monkeypatch.setitem(
        sys.modules,
        "webview",
        SimpleNamespace(OPEN_DIALOG=1, FOLDER_DIALOG=2),
    )
    api._attach_window(FakeWindow())


def _image(tmp_path: Path, name: str = "reference.png") -> tuple[Path, bytes]:
    payload = b"\x89PNG\r\n\x1a\n" + b"stilla-reference-test-image"
    path = tmp_path / name
    path.write_bytes(payload)
    return path, payload


def _reference_path(api: DesktopWorkspaceAPI, project_id: str, reference: dict) -> Path:
    return (
        api._workspace.root
        / "projects"
        / project_id
        / reference["relative_path"]
    )


def test_reference_import_attaches_asset_and_revision_atomically(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    api = DesktopWorkspaceAPI(tmp_path / "workspace")
    project_id = _project(api)
    api.save_character_profile(project_id, _profile(), expected_revision=0)
    image, payload = _image(tmp_path)
    _attach_picker(api, image, monkeypatch)

    result = api.import_character_reference_and_save(project_id, "hero_01", 1)

    assert result["saved"] is True
    assert result["revision"] == 2
    assert result["profile"]["references"][0]["sha256"] == hashlib.sha256(payload).hexdigest()
    reference = result["reference"]
    assert reference["size_bytes"] == len(payload)
    assert reference["mime_type"] == "image/png"
    assert _reference_path(api, project_id, reference).read_bytes() == payload
    loaded = api.load_character_profile(project_id, "hero_01")
    assert loaded["references"][0]["asset_id"] == reference["asset_id"]
    ledger = load_character_revision_ledger(
        api._workspace.root / "projects" / project_id / "characters",
        "hero_01",
    )
    assert ledger is not None
    assert ledger["current_revision"] == 2
    assert ledger["revisions"][1]["profile"]["references"][0]["asset_id"] == reference["asset_id"]
    assert not list(
        (api._workspace.root / "projects" / project_id / ".stilla-reference-transactions").glob("*.json")
    )


def test_stale_reference_import_does_not_create_an_asset_or_journal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    api = DesktopWorkspaceAPI(tmp_path / "workspace")
    project_id = _project(api)
    api.save_character_profile(project_id, _profile(), expected_revision=0)
    api.save_character_profile(project_id, _profile("Pip updated"), expected_revision=1)
    image, _ = _image(tmp_path)
    _attach_picker(api, image, monkeypatch)

    with pytest.raises(DesktopAPIError, match="changed in another window"):
        api.import_character_reference_and_save(project_id, "hero_01", 1)

    project = api._workspace.root / "projects" / project_id
    assert not (project / "characters" / "references").exists()
    assert not (project / ".stilla-reference-transactions").exists()


def test_failed_revision_commit_rolls_back_imported_asset_and_journal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import stilla.desktop.workspace_api as workspace_api_module
    from stilla.characters.revisions import CharacterRevisionError

    api = DesktopWorkspaceAPI(tmp_path / "workspace")
    project_id = _project(api)
    api.save_character_profile(project_id, _profile(), expected_revision=0)
    image, _ = _image(tmp_path)
    _attach_picker(api, image, monkeypatch)

    def fail_commit(*_args, **_kwargs):
        raise CharacterRevisionError("simulated ledger write failure")

    monkeypatch.setattr(workspace_api_module, "save_character_revision_ledger", fail_commit)
    with pytest.raises(DesktopAPIError, match="attach the reference"):
        api.import_character_reference_and_save(project_id, "hero_01", 1)

    project = api._workspace.root / "projects" / project_id
    references = project / "characters" / "references"
    if references.exists():
        assert not list(references.rglob("*.png"))
    journal_dir = project / ".stilla-reference-transactions"
    if journal_dir.exists():
        assert not list(journal_dir.glob("*.json"))
    assert api.load_character_profile(project_id, "hero_01")["references"] == []


def test_startup_recovery_removes_uncommitted_reference_asset(
    tmp_path: Path,
) -> None:
    api = DesktopWorkspaceAPI(tmp_path / "workspace")
    project_id = _project(api)
    api.save_character_profile(project_id, _profile(), expected_revision=0)
    project = api._workspace.root / "projects" / project_id
    transaction_id = "a" * 32
    asset_id = "b" * 32
    payload = b"\x89PNG\r\n\x1a\n" + b"interrupted-asset"
    relative = f"characters/references/hero_01/{asset_id}.png"
    asset = project / relative
    asset.parent.mkdir(parents=True)
    asset.write_bytes(payload)
    journal_dir = project / ".stilla-reference-transactions"
    journal_dir.mkdir()
    journal = {
        "schema_version": 1,
        "transaction_id": transaction_id,
        "character_id": "hero_01",
        "asset_id": asset_id,
        "extension": ".png",
        "sha256": hashlib.sha256(payload).hexdigest(),
        "size_bytes": len(payload),
    }
    (journal_dir / f"{transaction_id}.json").write_text(
        json.dumps(journal), encoding="utf-8"
    )

    api.list_character_profile_records(project_id)

    assert not asset.exists()
    assert not (journal_dir / f"{transaction_id}.json").exists()
    assert not journal_dir.exists()


def test_startup_recovery_keeps_committed_asset_and_removes_stale_journal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    api = DesktopWorkspaceAPI(tmp_path / "workspace")
    project_id = _project(api)
    api.save_character_profile(project_id, _profile(), expected_revision=0)
    image, payload = _image(tmp_path)
    _attach_picker(api, image, monkeypatch)
    result = api.import_character_reference_and_save(project_id, "hero_01", 1)
    reference = result["reference"]
    project = api._workspace.root / "projects" / project_id
    transaction_id = "c" * 32
    journal_dir = project / ".stilla-reference-transactions"
    journal_dir.mkdir(exist_ok=True)
    journal = {
        "schema_version": 1,
        "transaction_id": transaction_id,
        "character_id": "hero_01",
        "asset_id": reference["asset_id"],
        "extension": ".png",
        "sha256": hashlib.sha256(payload).hexdigest(),
        "size_bytes": len(payload),
    }
    (journal_dir / f"{transaction_id}.json").write_text(
        json.dumps(journal), encoding="utf-8"
    )

    api.list_character_profile_records(project_id)

    assert _reference_path(api, project_id, reference).read_bytes() == payload
    assert not (journal_dir / f"{transaction_id}.json").exists()
    assert not journal_dir.exists()


def test_reference_cleanup_removes_only_unreferenced_assets_and_keeps_history(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    api = DesktopWorkspaceAPI(tmp_path / "workspace")
    project_id = _project(api)
    api.save_character_profile(project_id, _profile(), expected_revision=0)
    image, payload = _image(tmp_path)
    _attach_picker(api, image, monkeypatch)
    result = api.import_character_reference_and_save(project_id, "hero_01", 1)
    reference = result["reference"]
    profile_without_reference = result["profile"]
    profile_without_reference["references"] = []
    api.save_character_profile(
        project_id, profile_without_reference, expected_revision=result["revision"]
    )

    project = api._workspace.root / "projects" / project_id
    orphan = project / "characters" / "references" / "hero_01" / f"{'d' * 32}.png"
    orphan.write_bytes(b"\x89PNG\r\n\x1a\norphan")
    unrelated = orphan.parent / "notes.png"
    unrelated.write_bytes(b"user-created file")
    api.list_character_profile_records(project_id)

    assert _reference_path(api, project_id, reference).read_bytes() == payload
    assert not orphan.exists()
    assert unrelated.read_bytes() == b"user-created file"


def test_reference_cleanup_is_project_scoped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    api = DesktopWorkspaceAPI(tmp_path / "workspace")
    first_project = _project(api)
    second_project = _project(api)
    api.save_character_profile(first_project, _profile(), expected_revision=0)
    api.save_character_profile(second_project, _profile(), expected_revision=0)
    image, payload = _image(tmp_path)
    _attach_picker(api, image, monkeypatch)
    result = api.import_character_reference_and_save(first_project, "hero_01", 1)
    reference = result["reference"]

    api.list_character_profile_records(second_project)

    assert _reference_path(api, first_project, reference).read_bytes() == payload
    assert api.load_character_profile(second_project, "hero_01")["references"] == []


def test_malformed_reference_journal_fails_closed_and_preserves_asset(
    tmp_path: Path,
) -> None:
    api = DesktopWorkspaceAPI(tmp_path / "workspace")
    project_id = _project(api)
    api.save_character_profile(project_id, _profile(), expected_revision=0)
    project = api._workspace.root / "projects" / project_id
    journal_dir = project / ".stilla-reference-transactions"
    journal_dir.mkdir()
    journal_path = journal_dir / f"{'e' * 32}.json"
    journal_path.write_text("{malformed", encoding="utf-8")

    with pytest.raises(DesktopAPIError, match="existing data was preserved"):
        api.list_character_profile_records(project_id)

    assert journal_path.read_text(encoding="utf-8") == "{malformed"


def test_reference_import_rejects_invalid_image_signature_without_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    api = DesktopWorkspaceAPI(tmp_path / "workspace")
    project_id = _project(api)
    api.save_character_profile(project_id, _profile(), expected_revision=0)
    image = tmp_path / "not-an-image.png"
    image.write_bytes(b"not a png")
    _attach_picker(api, image, monkeypatch)

    with pytest.raises(DesktopAPIError, match="signatures"):
        api.import_character_reference_and_save(project_id, "hero_01", 1)

    project = api._workspace.root / "projects" / project_id
    assert not (project / "characters" / "references").exists()
    assert not (project / ".stilla-reference-transactions").exists()
