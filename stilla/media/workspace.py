"""Safe local project workspace with atomic JSON persistence.

Only validated project IDs and document names are accepted. All writes stay beneath
the configured workspace root and use same-directory temporary files plus replace.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_NAME = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
_MAX_JSON_BYTES = 2_000_000


class WorkspaceError(ValueError):
    """Workspace data or operation is invalid."""


def _identifier(value: str, field: str, pattern: re.Pattern[str] = _ID) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise WorkspaceError(f"{field} must be a safe identifier")
    return value


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_bytes(value: Any) -> bytes:
    try:
        encoded = json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2).encode("utf-8")
    except (TypeError, ValueError, RecursionError):
        raise WorkspaceError("value must be JSON-serializable data") from None
    if len(encoded) > _MAX_JSON_BYTES:
        raise WorkspaceError("JSON document exceeds the 2 MB limit")
    return encoded


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise WorkspaceError("refusing to write through a symbolic link")
    fd, temp_name = tempfile.mkstemp(prefix=".stilla-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


class ProjectWorkspace:
    """Persist project metadata and named JSON documents beneath one local directory."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _project_dir(self, project_id: str) -> Path:
        _identifier(project_id, "project_id")
        path = self.root / "projects" / project_id
        if path.is_symlink():
            raise WorkspaceError("project directory must not be a symbolic link")
        if not path.resolve().is_relative_to((self.root / "projects").resolve()):
            raise WorkspaceError("project path escapes workspace")
        return path

    def create_project(self, project_id: str, title: str, *, language: str = "en") -> dict[str, Any]:
        project_dir = self._project_dir(project_id)
        if not isinstance(title, str) or not title.strip() or len(title) > 500:
            raise WorkspaceError("title must be non-empty text of at most 500 characters")
        if not isinstance(language, str) or not language.strip() or len(language) > 35:
            raise WorkspaceError("language must be non-empty text of at most 35 characters")
        project_dir.mkdir(parents=True, exist_ok=False)
        metadata = {
            "schema_version": 1,
            "id": project_id,
            "title": title.strip(),
            "language": language.strip(),
            "created_at": _now(),
            "updated_at": _now(),
        }
        try:
            _atomic_write(project_dir / "project.json", _json_bytes(metadata))
            (project_dir / "documents").mkdir()
        except Exception:
            # Remove only the directory created by this call; never overwrite existing work.
            import shutil
            shutil.rmtree(project_dir, ignore_errors=True)
            raise
        return metadata

    def list_projects(self) -> list[dict[str, Any]]:
        parent = self.root / "projects"
        if not parent.exists():
            return []
        projects = []
        for entry in parent.iterdir():
            if entry.is_symlink() or not entry.is_dir() or not _ID.fullmatch(entry.name):
                continue
            try:
                projects.append(self.load_project(entry.name))
            except WorkspaceError:
                continue
        return sorted(projects, key=lambda item: item["updated_at"], reverse=True)

    def load_project(self, project_id: str) -> dict[str, Any]:
        path = self._project_dir(project_id) / "project.json"
        value = self._read_json(path)
        if not isinstance(value, dict) or value.get("schema_version") != 1 or value.get("id") != project_id:
            raise WorkspaceError("project metadata is invalid")
        return value

    def save_document(self, project_id: str, name: str, value: Any) -> None:
        _identifier(project_id, "project_id")
        _identifier(name, "document name", _NAME)
        project = self._project_dir(project_id)
        if not project.is_dir():
            raise WorkspaceError("project does not exist")
        path = project / "documents" / f"{name}.json"
        _atomic_write(path, _json_bytes(value))
        metadata = self.load_project(project_id)
        metadata["updated_at"] = _now()
        _atomic_write(project / "project.json", _json_bytes(metadata))

    def load_document(self, project_id: str, name: str) -> Any:
        _identifier(name, "document name", _NAME)
        project = self._project_dir(project_id)
        if not project.is_dir():
            raise WorkspaceError("project does not exist")
        return self._read_json(project / "documents" / f"{name}.json")

    @staticmethod
    def _read_json(path: Path) -> Any:
        if path.is_symlink() or not path.is_file():
            raise WorkspaceError("workspace file does not exist or is unsafe")
        try:
            with path.open("rb") as stream:
                raw = stream.read(_MAX_JSON_BYTES + 1)
            if len(raw) > _MAX_JSON_BYTES:
                raise WorkspaceError("workspace file exceeds the 2 MB limit")
            return json.loads(raw.decode("utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, RecursionError):
            raise WorkspaceError("workspace file could not be read as valid JSON") from None
