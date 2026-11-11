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


def test_character_profiles_are_listed_only_within_the_selected_project(api: DesktopWorkspaceAPI) -> None:
    first = _project(api)
    second = _project(api)
    api.save_character_profile(first, _profile())
    other = _profile()
    other["id"] = "hero_02"
    other["name"] = "Other"
    api.save_character_profile(second, other)

    assert [item["id"] for item in api.list_character_profiles(first)] == ["hero_01"]
    assert [item["id"] for item in api.list_character_profiles(second)] == ["hero_02"]


def test_character_profile_delete_is_project_scoped(api: DesktopWorkspaceAPI) -> None:
    first = _project(api)
    second = _project(api)
    api.save_character_profile(first, _profile())
    other = _profile()
    other["id"] = "hero_01"
    api.save_character_profile(second, other)

    assert api.delete_character_profile(first, "hero_01") == {
        "deleted": True, "character_id": "hero_01"
    }
    assert api.list_character_profiles(first) == []
    assert api.load_character_profile(second, "hero_01")["name"] == "Pip"


def test_character_profile_delete_rejects_symlink(api: DesktopWorkspaceAPI, tmp_path: Path) -> None:
    project_id = _project(api)
    outside = tmp_path / "outside.character.json"
    outside.write_text("{}", encoding="utf-8")
    directory = api._workspace.root / "projects" / project_id / "characters"
    directory.mkdir()
    (directory / "hero_01.character.json").symlink_to(outside)
    with pytest.raises(DesktopAPIError, match="unsafe"):
        api.delete_character_profile(project_id, "hero_01")
    assert outside.read_text(encoding="utf-8") == "{}"


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


def test_reference_import_uses_native_picker_and_stores_hash(
    api: DesktopWorkspaceAPI, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import hashlib
    import sys
    from types import SimpleNamespace

    image = tmp_path / "reference.png"
    payload = b"\x89PNG\r\n\x1a\n" + b"test-image-payload"
    image.write_bytes(payload)

    class FakeWindow:
        def create_file_dialog(self, *_args, **_kwargs):
            return [str(image)]

    monkeypatch.setitem(
        sys.modules,
        "webview",
        SimpleNamespace(OPEN_DIALOG=1, FOLDER_DIALOG=2),
    )
    api._attach_window(FakeWindow())
    project_id = _project(api)
    result = api.import_character_reference(project_id, "hero_01")

    assert result["mime_type"] == "image/png"
    assert result["size_bytes"] == len(payload)
    assert result["sha256"] == hashlib.sha256(payload).hexdigest()
    stored = api._workspace.root / "projects" / project_id / result["relative_path"]
    assert stored.read_bytes() == payload


def test_reference_import_rejects_fake_image_extension(
    api: DesktopWorkspaceAPI, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import sys
    from types import SimpleNamespace

    fake = tmp_path / "fake.png"
    fake.write_bytes(b"not a real png")

    class FakeWindow:
        def create_file_dialog(self, *_args, **_kwargs):
            return [str(fake)]

    monkeypatch.setitem(
        sys.modules,
        "webview",
        SimpleNamespace(OPEN_DIALOG=1, FOLDER_DIALOG=2),
    )
    api._attach_window(FakeWindow())
    with pytest.raises(DesktopAPIError, match="signatures"):
        api.import_character_reference(_project(api), "hero_01")


def _empty_storyboard() -> dict:
    return {
        "schema_version": 1,
        "shot_plan": {"id": "story_plan", "title": "Project storyboard", "shots": []},
        "character_revisions": [],
        "bindings": [],
    }


def test_storyboard_document_round_trip_is_project_scoped(api: DesktopWorkspaceAPI) -> None:
    first = _project(api)
    second = _project(api)
    first_doc = _empty_storyboard()
    first_doc["shot_plan"]["title"] = "First project storyboard"
    second_doc = _empty_storyboard()
    second_doc["shot_plan"]["title"] = "Second project storyboard"

    api.save_document(first, "storyboard", first_doc)
    api.save_document(second, "storyboard", second_doc)

    assert api.load_document(first, "storyboard")["shot_plan"]["title"] == "First project storyboard"
    assert api.load_document(second, "storyboard")["shot_plan"]["title"] == "Second project storyboard"


def test_missing_storyboard_load_returns_valid_empty_document(api: DesktopWorkspaceAPI) -> None:
    project_id = _project(api)
    assert api.load_document(project_id, "storyboard") == _empty_storyboard()


def test_storyboard_document_rejects_invalid_binding_payload(api: DesktopWorkspaceAPI) -> None:
    with pytest.raises(DesktopAPIError, match="failed validation"):
        api.save_document(_project(api), "storyboard", {
            "schema_version": 1,
            "shot_plan": {"id": "../unsafe", "title": "Bad", "shots": []},
            "character_revisions": [],
            "bindings": [],
        })


def test_storyboard_load_rejects_symlink_document_directory(
    api: DesktopWorkspaceAPI, tmp_path: Path
) -> None:
    project_id = _project(api)
    project = api._workspace.root / "projects" / project_id
    outside = tmp_path / "outside-documents"
    outside.mkdir()
    (project / "documents").symlink_to(outside, target_is_directory=True)
    with pytest.raises(DesktopAPIError, match="unsafe"):
        api.load_document(project_id, "storyboard")
