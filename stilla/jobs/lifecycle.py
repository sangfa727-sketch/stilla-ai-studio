"""Persistent, guarded job lifecycle for local generation and render tasks."""
from __future__ import annotations

import json
import re
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from stilla.media.workspace import WorkspaceError, _atomic_write, _json_bytes

_JOB_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_STATES = {"queued", "running", "completed", "failed", "cancelled"}
_TERMINAL = {"completed", "failed", "cancelled"}
_ALLOWED = {
    "queued": {"running", "cancelled"},
    "running": {"completed", "failed", "cancelled"},
    "completed": set(),
    "failed": set(),
    "cancelled": set(),
}


class JobError(ValueError):
    """A job is missing, invalid, or cannot perform the requested transition."""


def _now() -> str:
    return datetime.now(UTC).isoformat()


class JobStore:
    """Store each job independently as bounded JSON, with guarded state transitions.

    This store records lifecycle state only. Workers and UI must perform actual work
    separately; cancellation here is a durable request/state transition, not a claim
    that an arbitrary external process has already stopped.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    def _path(self, job_id: str) -> Path:
        if not isinstance(job_id, str) or not _JOB_ID.fullmatch(job_id):
            raise JobError("job_id must be a safe identifier")
        path = self.root / f"{job_id}.json"
        if path.is_symlink():
            raise JobError("job file must not be a symbolic link")
        return path

    def create(self, job_id: str, kind: str, *, project_id: str, input_data: Any) -> dict[str, Any]:
        path = self._path(job_id)
        if not isinstance(kind, str) or not kind.strip() or len(kind) > 80:
            raise JobError("kind must be non-empty text of at most 80 characters")
        if not isinstance(project_id, str) or not _JOB_ID.fullmatch(project_id):
            raise JobError("project_id must be a safe identifier")
        if not isinstance(input_data, dict):
            raise JobError("input_data must be an object")
        record = {
            "schema_version": 1, "id": job_id, "project_id": project_id,
            "kind": kind.strip(), "state": "queued", "progress": 0,
            "input": input_data, "result": None, "error": None,
            "created_at": _now(), "updated_at": _now(),
        }
        with self._lock:
            if path.exists():
                raise JobError("job already exists")
            try:
                _atomic_write(path, _json_bytes(record))
            except WorkspaceError as exc:
                raise JobError(str(exc)) from None
        return record

    def get(self, job_id: str) -> dict[str, Any]:
        path = self._path(job_id)
        if path.is_symlink() or not path.is_file():
            raise JobError("job does not exist or is unsafe")
        try:
            with path.open("rb") as stream:
                raw = stream.read(2_000_001)
            if len(raw) > 2_000_000:
                raise JobError("job record exceeds the 2 MB limit")
            record = json.loads(raw.decode("utf-8"))
        except JobError:
            raise
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, RecursionError):
            raise JobError("job record is invalid") from None
        if not isinstance(record, dict) or record.get("id") != job_id or record.get("state") not in _STATES:
            raise JobError("job record is invalid")
        return record

    def transition(
        self, job_id: str, state: str, *, progress: int | None = None,
        result: dict[str, Any] | None = None, error: str | None = None,
    ) -> dict[str, Any]:
        if not isinstance(state, str) or state not in _STATES:
            raise JobError("unsupported job state")
        if progress is not None and (isinstance(progress, bool) or not isinstance(progress, int) or not 0 <= progress <= 100):
            raise JobError("progress must be an integer from 0 to 100")
        if error is not None and (not isinstance(error, str) or len(error) > 2_000):
            raise JobError("error must be text of at most 2000 characters")
        if result is not None and not isinstance(result, dict):
            raise JobError("result must be an object")
        with self._lock:
            record = self.get(job_id)
            current = record["state"]
            if state not in _ALLOWED[current]:
                raise JobError(f"cannot transition job from {current} to {state}")
            if state == "completed":
                if progress not in (None, 100):
                    raise JobError("completed jobs must have 100 percent progress")
                record["progress"] = 100
                record["result"] = result or {}
                record["error"] = None
            elif state == "failed":
                if not error:
                    raise JobError("failed jobs require a safe error message")
                record["error"] = error
            elif state == "cancelled":
                record["error"] = None
            else:
                if state == "running":
                    record["progress"] = 0 if progress is None else progress
                elif progress is not None:
                    if progress < record["progress"]:
                        raise JobError("job progress cannot move backwards")
                    record["progress"] = progress
            record["state"] = state
            record["updated_at"] = _now()
            try:
                _atomic_write(self._path(job_id), _json_bytes(record))
            except WorkspaceError as exc:
                raise JobError(str(exc)) from None
            return record

    def update_progress(self, job_id: str, progress: int) -> dict[str, Any]:
        if isinstance(progress, bool) or not isinstance(progress, int) or not 0 <= progress <= 99:
            raise JobError("running progress must be an integer from 0 to 99")
        with self._lock:
            record = self.get(job_id)
            if record["state"] != "running":
                raise JobError("only running jobs can report progress")
            if progress < record["progress"]:
                raise JobError("job progress cannot move backwards")
            record["progress"] = progress
            record["updated_at"] = _now()
            try:
                _atomic_write(self._path(job_id), _json_bytes(record))
            except WorkspaceError as exc:
                raise JobError(str(exc)) from None
            return record
