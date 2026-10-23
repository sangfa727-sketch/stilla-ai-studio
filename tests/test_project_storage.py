import json
from pathlib import Path

import pytest

from stilla.projects.schema import (
    AssetReference,
    ProjectDocument,
    ProjectValidationError,
    Scene,
)
from stilla.projects.storage import (
    MAX_PROJECT_BYTES,
    ProjectStorageError,
    load_project,
    save_project,
)


def project() -> ProjectDocument:
    return ProjectDocument(
        id="project_01",
        name="Morning Film",
        scenes=(Scene("scene_01", "First light", "A bakery opens", 8),),
        assets=(AssetReference("asset_01", "media/morning.mp4", "video/mp4"),),
        metadata={"frame_rate": 30},
    )


def test_project_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "morning.stilla.json"
    original = project()
    save_project(path, original)
    loaded = load_project(path)
    assert loaded == original
    assert loaded.scenes[0].title == "First light"
    assert loaded.assets[0].relative_path == "media/morning.mp4"


@pytest.mark.parametrize("asset_path", ["../secret.txt", "/etc/passwd", "C:\\private\\file.mp4"])
def test_asset_path_rejects_absolute_and_traversal(asset_path: str) -> None:
    with pytest.raises(ProjectValidationError):
        AssetReference("asset_01", asset_path, "video/mp4")


def test_rejects_duplicate_scene_and_asset_ids() -> None:
    with pytest.raises(ProjectValidationError, match="scene IDs"):
        ProjectDocument(
            id="project_01",
            name="Film",
            scenes=(Scene("same", "One"), Scene("same", "Two")),
        )
    with pytest.raises(ProjectValidationError, match="asset IDs"):
        ProjectDocument(
            id="project_01",
            name="Film",
            assets=(
                AssetReference("same", "one.png", "image/png"),
                AssetReference("same", "two.png", "image/png"),
            ),
        )


def test_rejects_unsupported_schema_and_unknown_top_level_fields() -> None:
    with pytest.raises(ProjectValidationError, match="schema version"):
        ProjectDocument.from_dict({"schema_version": 999, "id": "p", "name": "Film"})
    with pytest.raises(ProjectValidationError, match="unsupported top-level"):
        ProjectDocument.from_dict(
            {"schema_version": 1, "id": "p", "name": "Film", "execute": "arbitrary code"}
        )


def test_rejects_invalid_scene_duration() -> None:
    with pytest.raises(ProjectValidationError):
        Scene("scene_01", "Scene", duration_seconds=0)
    with pytest.raises(ProjectValidationError):
        Scene("scene_01", "Scene", duration_seconds=float("inf"))


def test_load_rejects_invalid_json_without_leaking_contents(tmp_path: Path) -> None:
    path = tmp_path / "bad.stilla.json"
    path.write_text('{"secret":"do not disclose"', encoding="utf-8")
    with pytest.raises(ProjectStorageError, match="valid UTF-8 JSON") as exc:
        load_project(path)
    assert "do not disclose" not in str(exc.value)


def test_load_rejects_oversized_document(tmp_path: Path) -> None:
    path = tmp_path / "large.stilla.json"
    path.write_bytes(b" " * (MAX_PROJECT_BYTES + 1))
    with pytest.raises(ProjectStorageError, match="10 MiB"):
        load_project(path)


def test_save_rejects_wrong_extension_and_missing_directory(tmp_path: Path) -> None:
    with pytest.raises(ProjectStorageError, match="must end"):
        save_project(tmp_path / "project.json", project())
    with pytest.raises(ProjectStorageError, match="directory does not exist"):
        save_project(tmp_path / "missing" / "project.stilla.json", project())


def test_save_rejects_symlink_target(tmp_path: Path) -> None:
    real = tmp_path / "real.stilla.json"
    real.write_text(json.dumps(project().to_dict()), encoding="utf-8")
    link = tmp_path / "linked.stilla.json"
    try:
        link.symlink_to(real)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation unavailable on this platform")
    with pytest.raises(ProjectStorageError, match="symbolic-link"):
        save_project(link, project())


def test_bad_document_shape_is_reported_as_schema_failure(tmp_path: Path) -> None:
    path = tmp_path / "wrong-shape.stilla.json"
    path.write_text('[]', encoding="utf-8")
    with pytest.raises(ProjectStorageError, match="schema validation"):
        load_project(path)
