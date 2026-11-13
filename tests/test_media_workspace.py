from __future__ import annotations

import multiprocessing
import threading
import time
from pathlib import Path

import pytest

from stilla.media.workspace import (
    ProjectWorkspace,
    WorkspaceConflictError,
    WorkspaceError,
)


def _hold_project_lock(root: str, project_id: str, entered: object) -> None:
    with ProjectWorkspace(root).project_lock(project_id):
        entered.set()
        time.sleep(0.35)


def _wait_for_project_lock(root: str, project_id: str, results: object) -> None:
    started = time.monotonic()
    with ProjectWorkspace(root).project_lock(project_id, timeout=5):
        results.put(time.monotonic() - started)


def test_versioned_document_write_rejects_stale_revision(tmp_path: Path) -> None:
    workspace = ProjectWorkspace(tmp_path / "workspace")
    workspace.create_project("project_01", "Test")
    initial = workspace.load_document_versioned("project_01", "storyboard")
    assert initial == {"value": None, "revision": None}

    first_revision = workspace.save_document_versioned(
        "project_01", "storyboard", {"title": "First"}, expected_revision=None
    )
    second = workspace.load_document_versioned("project_01", "storyboard")
    assert second["revision"] == first_revision

    next_revision = workspace.save_document_versioned(
        "project_01", "storyboard", {"title": "Second"},
        expected_revision=first_revision,
    )
    assert next_revision != first_revision
    with pytest.raises(WorkspaceConflictError):
        workspace.save_document_versioned(
            "project_01", "storyboard", {"title": "Stale"},
            expected_revision=first_revision,
        )
    assert workspace.load_document("project_01", "storyboard") == {"title": "Second"}


def test_versioned_writes_allow_only_one_concurrent_winner(tmp_path: Path) -> None:
    root = tmp_path / "workspace"
    first = ProjectWorkspace(root)
    second = ProjectWorkspace(root)
    first.create_project("project_01", "Test")
    revision = first.save_document_versioned(
        "project_01", "brief", {"value": 0}, expected_revision=None
    )
    barrier = threading.Barrier(3)
    results: list[str] = []

    def write(workspace: ProjectWorkspace, value: int) -> None:
        barrier.wait()
        try:
            workspace.save_document_versioned(
                "project_01", "brief", {"value": value}, expected_revision=revision
            )
            results.append("saved")
        except WorkspaceConflictError:
            results.append("conflict")

    workers = [
        threading.Thread(target=write, args=(first, 1)),
        threading.Thread(target=write, args=(second, 2)),
    ]
    for worker in workers:
        worker.start()
    barrier.wait()
    for worker in workers:
        worker.join(timeout=5)
        assert not worker.is_alive()

    assert sorted(results) == ["conflict", "saved"]


def test_project_lock_serializes_independent_processes(tmp_path: Path) -> None:
    root = tmp_path / "workspace"
    ProjectWorkspace(root).create_project("project_01", "Process lock")
    context = multiprocessing.get_context("spawn")
    entered = context.Event()
    results = context.Queue()
    holder = context.Process(target=_hold_project_lock, args=(str(root), "project_01", entered))
    waiter = context.Process(target=_wait_for_project_lock, args=(str(root), "project_01", results))

    holder.start()
    assert entered.wait(timeout=5)
    waiter.start()
    elapsed = results.get(timeout=8)
    holder.join(timeout=8)
    waiter.join(timeout=8)

    assert holder.exitcode == 0
    assert waiter.exitcode == 0
    assert elapsed >= 0.20


def test_project_lock_rejects_symbolic_link_lock_file(tmp_path: Path) -> None:
    root = tmp_path / "workspace"
    workspace = ProjectWorkspace(root)
    workspace.create_project("project_01", "Symlink lock")
    outside = tmp_path / "outside.lock"
    outside.write_bytes(b"")
    lock_path = root / "projects" / "project_01" / ".stilla.lock"
    try:
        lock_path.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation unavailable on this platform")

    with pytest.raises(WorkspaceError, match="unsafe"):
        with workspace.project_lock("project_01"):
            pass


def test_legacy_document_save_remains_compatible(tmp_path: Path) -> None:
    workspace = ProjectWorkspace(tmp_path / "workspace")
    workspace.create_project("project_01", "Compatibility")
    workspace.save_document("project_01", "brief", {"idea": "local"})
    assert workspace.load_document("project_01", "brief") == {"idea": "local"}
