"""Bounded, atomic project document persistence."""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
from typing import Any

from stilla.projects.schema import ProjectDocument, ProjectValidationError


MAX_PROJECT_BYTES = 10 * 1024 * 1024
PROJECT_SUFFIX = ".stilla.json"


class ProjectStorageError(RuntimeError):
    """Safe project persistence error without leaking document contents."""


def _validate_path(path: Path) -> Path:
    target = Path(path).expanduser()
    if target.suffixes[-2:] != [".stilla", ".json"]:
        raise ProjectStorageError(f"Project path must end with {PROJECT_SUFFIX}")
    if target.exists() and target.is_symlink():
        raise ProjectStorageError("Refusing to read or overwrite a symbolic-link project file")
    if not target.parent.exists() or not target.parent.is_dir():
        raise ProjectStorageError("Project directory does not exist")
    return target


def save_project(path: str | Path, project: ProjectDocument) -> Path:
    """Write to a same-directory temporary file, fsync, then atomically replace target."""
    target = _validate_path(Path(path))
    if not isinstance(project, ProjectDocument):
        raise ProjectStorageError("project must be a validated ProjectDocument")
    try:
        encoded = json.dumps(
            project.to_dict(), ensure_ascii=False, allow_nan=False, separators=(",", ":")
        ).encode("utf-8")
    except (TypeError, ValueError):
        raise ProjectStorageError("Project contains data that cannot be safely serialized") from None
    if len(encoded) > MAX_PROJECT_BYTES:
        raise ProjectStorageError("Project document exceeds the 10 MiB limit")

    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=target.parent, prefix=".stilla-tmp-", suffix=".tmp", delete=False
        ) as stream:
            temp_name = stream.name
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, target)
        temp_name = None
        # Best-effort directory fsync improves rename durability on POSIX; unsupported on Windows.
        try:
            directory_fd = os.open(target.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        except OSError:
            pass
    except OSError:
        raise ProjectStorageError("Could not save project; the previous file was preserved") from None
    finally:
        if temp_name is not None:
            try:
                os.unlink(temp_name)
            except OSError:
                pass
    return target


def load_project(path: str | Path) -> ProjectDocument:
    """Load a bounded JSON project and validate it before returning any data."""
    target = _validate_path(Path(path))
    try:
        with target.open("rb") as stream:
            raw = stream.read(MAX_PROJECT_BYTES + 1)
    except OSError:
        raise ProjectStorageError("Could not read project file") from None
    if len(raw) > MAX_PROJECT_BYTES:
        raise ProjectStorageError("Project document exceeds the 10 MiB limit")
    try:
        data: Any = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ProjectStorageError("Project file is not valid UTF-8 JSON") from None
    try:
        return ProjectDocument.from_dict(data)
    except (ProjectValidationError, TypeError):
        raise ProjectStorageError("Project document failed schema validation") from None
