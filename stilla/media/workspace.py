"""Safe local project workspace with atomic, version-aware JSON persistence."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
import threading
import time
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator

_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_NAME = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_MAX_JSON_BYTES = 2_000_000
_LOCK_TIMEOUT_SECONDS = 15.0
_PROCESS_LOCKS: dict[str, threading.Lock] = {}
_PROCESS_LOCKS_GUARD = threading.Lock()


class WorkspaceError(ValueError):
    """Workspace data or operation is invalid."""


class WorkspaceConflictError(WorkspaceError):
    """A versioned write was based on a stale document revision."""


def _identifier(value: str, field: str, pattern: re.Pattern[str] = _ID) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise WorkspaceError(f"{field} must be a safe identifier")
    return value


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _json_bytes(value: Any) -> bytes:
    try:
        encoded = json.dumps(
            value, ensure_ascii=False, allow_nan=False, indent=2
        ).encode("utf-8")
    except (TypeError, ValueError, RecursionError):
        raise WorkspaceError("value must be JSON-serializable data") from None
    if len(encoded) > _MAX_JSON_BYTES:
        raise WorkspaceError("JSON document exceeds the 2 MB limit")
    return encoded


def _fsync_directory(path: Path) -> None:
    if os.name == "nt":
        return
    try:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError:
        # Some filesystems do not support directory fsync; the file itself is already synced.
        return


def atomic_write_bytes(path: str | Path, data: bytes) -> None:
    """Atomically replace one file and sync its parent directory where supported."""
    target = Path(path)
    if not isinstance(data, bytes):
        raise WorkspaceError("atomic write data must be bytes")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink():
        raise WorkspaceError("refusing to write through a symbolic link")
    descriptor, temp_name = tempfile.mkstemp(
        prefix=".stilla-", suffix=".tmp", dir=target.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, target)
        _fsync_directory(target.parent)
    except OSError:
        raise WorkspaceError("atomic workspace write failed") from None
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        except OSError:
            pass


def _atomic_write(path: Path, data: bytes) -> None:
    atomic_write_bytes(path, data)


class ProjectWorkspace:
    """Persist project metadata and named JSON documents beneath one local directory."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def project_lock(
        self, project_id: str, timeout: float = _LOCK_TIMEOUT_SECONDS
    ) -> Iterator[None]:
        """Serialize project operations across threads and independent processes."""
        project = self._project_dir(project_id)
        if not project.is_dir():
            raise WorkspaceError("project does not exist")
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or timeout <= 0:
            raise WorkspaceError("project lock timeout must be a positive number")
        lock_path = project / ".stilla.lock"
        if lock_path.is_symlink():
            raise WorkspaceError("project lock path is unsafe")
        key = str(lock_path.resolve())
        with _PROCESS_LOCKS_GUARD:
            thread_lock = _PROCESS_LOCKS.setdefault(key, threading.Lock())
        if not thread_lock.acquire(timeout=float(timeout)):
            raise WorkspaceError("timed out waiting for project lock")

        descriptor: int | None = None
        locked = False
        deadline = time.monotonic() + float(timeout)
        try:
            try:
                flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
                descriptor = os.open(lock_path, flags, 0o600)
                if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                    raise WorkspaceError("project lock path is not a regular file")
                if os.name == "nt":
                    import msvcrt

                    if os.fstat(descriptor).st_size == 0:
                        os.write(descriptor, b"\\0")
                        os.fsync(descriptor)
                    while True:
                        os.lseek(descriptor, 0, os.SEEK_SET)
                        try:
                            msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
                            locked = True
                            break
                        except OSError:
                            if time.monotonic() >= deadline:
                                raise WorkspaceError("timed out waiting for project lock") from None
                            time.sleep(0.025)
                else:
                    import fcntl

                    while True:
                        try:
                            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                            locked = True
                            break
                        except BlockingIOError:
                            if time.monotonic() >= deadline:
                                raise WorkspaceError("timed out waiting for project lock") from None
                            time.sleep(0.025)
            except WorkspaceError:
                raise
            except OSError:
                raise WorkspaceError("could not acquire project lock") from None
            yield
        finally:
            try:
                if descriptor is not None:
                    if locked:
                        try:
                            if os.name == "nt":
                                import msvcrt

                                os.lseek(descriptor, 0, os.SEEK_SET)
                                msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
                            else:
                                import fcntl

                                fcntl.flock(descriptor, fcntl.LOCK_UN)
                        except OSError:
                            pass
                    os.close(descriptor)
            finally:
                thread_lock.release()

    def _projects_dir(self) -> Path:
        path = self.root / "projects"
        if path.is_symlink():
            raise WorkspaceError("projects directory must not be a symbolic link")
        return path

    def _project_dir(self, project_id: str) -> Path:
        _identifier(project_id, "project_id")
        projects = self._projects_dir()
        path = projects / project_id
        if path.is_symlink():
            raise WorkspaceError("project directory must not be a symbolic link")
        if not path.resolve().is_relative_to(projects.resolve()):
            raise WorkspaceError("project path escapes workspace")
        return path

    @staticmethod
    def _documents_dir(project: Path) -> Path:
        path = project / "documents"
        if path.is_symlink() or not path.is_dir():
            raise WorkspaceError("project documents directory is missing or unsafe")
        if not path.resolve().is_relative_to(project.resolve()):
            raise WorkspaceError("documents path escapes project")
        return path

    def create_project(
        self, project_id: str, title: str, *, language: str = "en"
    ) -> dict[str, Any]:
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
        except (OSError, WorkspaceError):
            shutil.rmtree(project_dir, ignore_errors=True)
            raise
        return metadata

    def list_projects(self) -> list[dict[str, Any]]:
        parent = self._projects_dir()
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
        if (
            not isinstance(value, dict)
            or value.get("schema_version") != 1
            or value.get("id") != project_id
        ):
            raise WorkspaceError("project metadata is invalid")
        return value

    def _document_path(self, project_id: str, name: str) -> Path:
        _identifier(name, "document name", _NAME)
        project = self._project_dir(project_id)
        if not project.is_dir():
            raise WorkspaceError("project does not exist")
        return self._documents_dir(project) / f"{name}.json"

    def _update_project_timestamp(self, project_id: str) -> None:
        project = self._project_dir(project_id)
        metadata = self.load_project(project_id)
        metadata["updated_at"] = _now()
        _atomic_write(project / "project.json", _json_bytes(metadata))

    @staticmethod
    def _read_bytes(path: Path) -> bytes | None:
        if path.is_symlink():
            raise WorkspaceError("workspace file path is unsafe")
        if not path.exists():
            return None
        if not path.is_file():
            raise WorkspaceError("workspace path is not a regular file")
        try:
            with path.open("rb") as stream:
                raw = stream.read(_MAX_JSON_BYTES + 1)
        except OSError:
            raise WorkspaceError("workspace file could not be read") from None
        if len(raw) > _MAX_JSON_BYTES:
            raise WorkspaceError("workspace file exceeds the 2 MB limit")
        return raw

    @staticmethod
    def _parse_bytes(raw: bytes) -> Any:
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError, RecursionError):
            raise WorkspaceError("workspace file could not be read as valid JSON") from None

    def save_document(self, project_id: str, name: str, value: Any) -> None:
        path = self._document_path(project_id, name)
        encoded = _json_bytes(value)
        with self.project_lock(project_id):
            # Updating metadata first makes an interrupted write a harmless timestamp-only change.
            self._update_project_timestamp(project_id)
            _atomic_write(path, encoded)

    def load_document(self, project_id: str, name: str) -> Any:
        path = self._document_path(project_id, name)
        with self.project_lock(project_id):
            raw = self._read_bytes(path)
            if raw is None:
                raise WorkspaceError("workspace file does not exist")
            return self._parse_bytes(raw)

    def load_document_versioned(self, project_id: str, name: str) -> dict[str, Any]:
        """Return a document and its content hash for optimistic concurrency."""
        path = self._document_path(project_id, name)
        with self.project_lock(project_id):
            raw = self._read_bytes(path)
            if raw is None:
                return {"value": None, "revision": None}
            return {
                "value": self._parse_bytes(raw),
                "revision": hashlib.sha256(raw).hexdigest(),
            }

    def save_document_versioned(
        self, project_id: str, name: str, value: Any, expected_revision: str | None
    ) -> str:
        """Save only when the caller's content-hash revision is still current."""
        if expected_revision is not None and (
            not isinstance(expected_revision, str) or not _SHA256.fullmatch(expected_revision)
        ):
            raise WorkspaceError("expected document revision is invalid")
        path = self._document_path(project_id, name)
        encoded = _json_bytes(value)
        with self.project_lock(project_id):
            current = self._read_bytes(path)
            current_revision = hashlib.sha256(current).hexdigest() if current is not None else None
            if current_revision != expected_revision:
                raise WorkspaceConflictError("document changed since it was loaded")
            self._update_project_timestamp(project_id)
            _atomic_write(path, encoded)
            return hashlib.sha256(encoded).hexdigest()

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
