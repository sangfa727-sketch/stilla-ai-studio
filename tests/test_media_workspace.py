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


def _hold_project_lock(
    root: str, project_id: str, entered: object, attempting: object, released: object
) -> None:
    with ProjectWorkspace(root).project_lock(project_id):
        entered.set()
        if not attempting.wait(timeout=5):
            raise RuntimeError("second process did not attempt the project lock")
        time.sleep(1)
    released.set()


def _wait_for_project_lock(
    root: str, project_id: str, attempting: object, released: object, acquired: object
) -> None:
    attempting.set()
    with ProjectWorkspace(root).project_lock(project_id, timeout=5):
        if not released.is_set():
            raise AssertionError("second process entered before the first released the lock")
        acquired.set()


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
    attempting = context.Event()
    released = context.Event()
    acquired = context.Event()
    holder = context.Process(
        target=_hold_project_lock,
        args=(str(root), "project_01", entered, attempting, released),
    )
    waiter = context.Process(
        target=_wait_for_project_lock,
        args=(str(root), "project_01", attempting, released, acquired),
    )

    holder.start()
    assert entered.wait(timeout=5)
    waiter.start()
    assert acquired.wait(timeout=8)
    holder.join(timeout=8)
    waiter.join(timeout=8)

    assert released.is_set()
    assert holder.exitcode == 0
    assert waiter.exitcode == 0


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

    with pytest.raises(WorkspaceError, match="unsafe"), workspace.project_lock("project_01"):
        pass


def test_legacy_document_save_remains_compatible(tmp_path: Path) -> None:
    workspace = ProjectWorkspace(tmp_path / "workspace")
    workspace.create_project("project_01", "Compatibility")
    workspace.save_document("project_01", "brief", {"idea": "local"})
    assert workspace.load_document("project_01", "brief") == {"idea": "local"}



def test_project_lock_does_not_mask_operation_errors(tmp_path: Path) -> None:
    workspace = ProjectWorkspace(tmp_path / "workspace")
    workspace.create_project("project_01", "Error propagation")

    with pytest.raises(OSError, match="operation failed"), workspace.project_lock("project_01"):
        raise OSError("operation failed")
