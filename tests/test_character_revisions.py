from __future__ import annotations

import json
from pathlib import Path

import pytest

from stilla.characters.revisions import load_character_revision_ledger
from stilla.characters.schema import CharacterProfile, VisualIdentity
from stilla.characters.storage import save_character
from stilla.desktop.workspace_api import DesktopAPIError, DesktopWorkspaceAPI


@pytest.fixture
def api(tmp_path: Path) -> DesktopWorkspaceAPI:
    return DesktopWorkspaceAPI(tmp_path / "workspace")


def _profile(name: str = "Pip") -> dict:
    return CharacterProfile(
        id="hero_01",
        name=name,
        species_or_type="original small forest creature",
        visual=VisualIdentity(
            silhouette="round pear shape",
            body_proportions="large head, short body",
            face_shape="soft oval",
            eyes="large amber eyes",
        ),
    ).to_dict()


def _project(api: DesktopWorkspaceAPI) -> str:
    return api.create_project("Revision test project")["id"]


def _character_dir(api: DesktopWorkspaceAPI, project_id: str) -> Path:
    return api._workspace.root / "projects" / project_id / "characters"


def test_character_revisions_are_durable_and_immutable(api: DesktopWorkspaceAPI) -> None:
    project_id = _project(api)
    first = _profile()
    saved_first = api.save_character_profile(project_id, first, expected_revision=0)
    assert saved_first["revision"] == 1

    second = _profile("Pip the Explorer")
    saved_second = api.save_character_profile(project_id, second, expected_revision=1)
    assert saved_second["revision"] == 2

    ledger = load_character_revision_ledger(_character_dir(api, project_id), "hero_01")
    assert ledger is not None
    assert [entry["revision"] for entry in ledger["revisions"]] == [1, 2]
    assert ledger["revisions"][0]["profile"]["name"] == "Pip"
    assert ledger["revisions"][1]["profile"]["name"] == "Pip the Explorer"
    records = api.list_character_profile_records(project_id)
    assert records[0]["revision"] == 2
    assert records[0]["profile"]["name"] == "Pip the Explorer"


def test_stale_character_revision_is_rejected_without_overwriting_latest(
    api: DesktopWorkspaceAPI,
) -> None:
    project_id = _project(api)
    api.save_character_profile(project_id, _profile(), expected_revision=0)
    api.save_character_profile(
        project_id, _profile("Pip Updated"), expected_revision=1
    )

    with pytest.raises(DesktopAPIError, match="changed in another window"):
        api.save_character_profile(
            project_id, _profile("Stale edit"), expected_revision=1
        )

    assert api.load_character_profile(project_id, "hero_01")["name"] == "Pip Updated"


def test_legacy_character_file_migrates_to_revision_one(api: DesktopWorkspaceAPI) -> None:
    project_id = _project(api)
    directory = _character_dir(api, project_id)
    directory.mkdir()
    save_character(directory, CharacterProfile.from_dict(_profile()))

    records = api.list_character_profile_records(project_id)

    assert len(records) == 1
    assert records[0]["revision"] == 1
    assert (directory / "revisions" / "hero_01.revisions.json").is_file()


def test_ledger_recovers_profile_mirror_after_interrupted_write(
    api: DesktopWorkspaceAPI,
) -> None:
    project_id = _project(api)
    directory = _character_dir(api, project_id)
    first = _profile()
    api.save_character_profile(project_id, first, expected_revision=0)
    latest = _profile("Pip after recovery")
    api.save_character_profile(project_id, latest, expected_revision=1)

    # Simulate a crash after the immutable ledger commit but before its current-file mirror.
    save_character(directory, CharacterProfile.from_dict(first))

    loaded = api.load_character_profile(project_id, "hero_01")
    assert loaded["name"] == "Pip after recovery"
    assert json.loads(
        (directory / "hero_01.character.json").read_text(encoding="utf-8")
    )["name"] == "Pip after recovery"


def test_corrupt_revision_ledger_fails_closed_and_is_preserved(
    api: DesktopWorkspaceAPI,
) -> None:
    project_id = _project(api)
    api.save_character_profile(project_id, _profile(), expected_revision=0)
    ledger_path = _character_dir(api, project_id) / "revisions" / "hero_01.revisions.json"
    corrupt = "{not valid ledger JSON"
    ledger_path.write_text(corrupt, encoding="utf-8")

    with pytest.raises(DesktopAPIError, match="existing data was preserved"):
        api.list_character_profile_records(project_id)

    assert ledger_path.read_text(encoding="utf-8") == corrupt


def test_character_delete_preserves_revision_history_as_tombstone(
    api: DesktopWorkspaceAPI,
) -> None:
    project_id = _project(api)
    api.save_character_profile(project_id, _profile(), expected_revision=0)

    result = api.delete_character_profile(project_id, "hero_01")
    ledger = load_character_revision_ledger(_character_dir(api, project_id), "hero_01")

    assert result["history_preserved"] is True
    assert ledger is not None
    assert ledger["deleted_at"]
    assert len(ledger["revisions"]) == 1
    assert api.list_character_profile_records(project_id) == []


def test_revision_ledgers_are_isolated_between_projects(api: DesktopWorkspaceAPI) -> None:
    first_project = _project(api)
    second_project = _project(api)
    api.save_character_profile(first_project, _profile("First"), expected_revision=0)
    api.save_character_profile(second_project, _profile("Second"), expected_revision=0)

    assert api.load_character_profile(first_project, "hero_01")["name"] == "First"
    assert api.load_character_profile(second_project, "hero_01")["name"] == "Second"
    assert api.list_character_profile_records(first_project)[0]["revision"] == 1
    assert api.list_character_profile_records(second_project)[0]["revision"] == 1


def test_external_profile_divergence_is_not_silently_overwritten(
    api: DesktopWorkspaceAPI,
) -> None:
    project_id = _project(api)
    directory = _character_dir(api, project_id)
    api.save_character_profile(project_id, _profile(), expected_revision=0)
    save_character(directory, CharacterProfile.from_dict(_profile("Untracked external edit")))

    with pytest.raises(DesktopAPIError, match="existing data was preserved"):
        api.list_character_profile_records(project_id)

    assert api.load_character_profile.__name__ == "load_character_profile"
    assert json.loads(
        (directory / "hero_01.character.json").read_text(encoding="utf-8")
    )["name"] == "Untracked external edit"
