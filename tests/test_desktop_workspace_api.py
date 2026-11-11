from __future__ import annotations

from pathlib import Path

import pytest

from stilla.characters.schema import CharacterProfile, VisualIdentity
from stilla.desktop.workspace_api import DesktopAPIError, DesktopWorkspaceAPI


@pytest.fixture
def api(tmp_path: Path) -> DesktopWorkspaceAPI:
    return DesktopWorkspaceAPI(tmp_path / "workspace")


def _project(api: DesktopWorkspaceAPI) -> str:
    return api.create_project("Fixture project")["id"]


def _profile() -> dict:
    return CharacterProfile(
        id="hero_01",
        name="Pip",
        species_or_type="original small forest creature",
        visual=VisualIdentity(
            silhouette="round pear shape",
            body_proportions="large head, short body",
            face_shape="soft oval",
            eyes="large amber eyes",
        ),
    ).to_dict()


def test_runtime_info_exposes_only_declared_runtime_metadata(api: DesktopWorkspaceAPI) -> None:
    info = api.get_runtime_info()
    assert info["runtime"] == "pywebview"
    assert info["bridge_version"] == 1
    assert info["ready"] is True
    assert not hasattr(api, "open_path")
    assert not hasattr(api, "run_command")


def test_create_project_uses_generated_safe_identifier(api: DesktopWorkspaceAPI) -> None:
    project = api.create_project("A local story", "my")
    assert project["title"] == "A local story"
    assert len(project["id"]) == 32
    assert api.list_projects()[0]["id"] == project["id"]


def test_project_document_round_trip_is_project_scoped(api: DesktopWorkspaceAPI) -> None:
    first = api.create_project("First")
    second = api.create_project("Second")
    api.save_document(first["id"], "brief", {"idea": "first project"})
    api.save_document(second["id"], "brief", {"idea": "second project"})
    assert api.load_document(first["id"], "brief") == {"idea": "first project"}
    assert api.load_document(second["id"], "brief") == {"idea": "second project"}


@pytest.mark.parametrize("project_id", ["../outside", "C:\\private", "", None])
def test_rejects_unsafe_or_missing_project_ids(api: DesktopWorkspaceAPI, project_id: str) -> None:
    with pytest.raises(DesktopAPIError):
        api.load_document(project_id, "brief")


def test_rejects_unapproved_document_names(api: DesktopWorkspaceAPI) -> None:
    with pytest.raises(DesktopAPIError):
        api.save_document(_project(api), "../secret", {"x": 1})


def test_character_profile_round_trip_is_inside_project(api: DesktopWorkspaceAPI) -> None:
    project_id = _project(api)
    saved = api.save_character_profile(project_id, _profile())
    assert saved["saved"] is True
    loaded = api.load_character_profile(project_id, "hero_01")
    assert loaded["name"] == "Pip"
    assert (api._workspace.root / "projects" / project_id / "characters" /
            "hero_01.character.json").is_file()


def test_rejects_invalid_character_profile(api: DesktopWorkspaceAPI) -> None:
    with pytest.raises(DesktopAPIError):
        api.save_character_profile(_project(api), {"id": "../bad"})


def test_rejects_symlink_project_directory(api: DesktopWorkspaceAPI, tmp_path: Path) -> None:
    project_id = _project(api)
    outside = tmp_path / "outside"
    outside.mkdir()
    project_path = api._workspace.root / "projects" / project_id
    real_project = tmp_path / "real-project"
    project_path.rename(real_project)
    project_path.symlink_to(outside, target_is_directory=True)
    with pytest.raises(DesktopAPIError):
        api.load_document(project_id, "brief")


def test_reference_import_requires_native_window(api: DesktopWorkspaceAPI) -> None:
    with pytest.raises(DesktopAPIError, match="window is not ready"):
        api.import_character_reference(_project(api), "hero_01")


def test_document_size_limit(api: DesktopWorkspaceAPI) -> None:
    with pytest.raises(DesktopAPIError, match="2 MB"):
        api.save_document(_project(api), "brief", {"text": "x" * 2_000_001})
