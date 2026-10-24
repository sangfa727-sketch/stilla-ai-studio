import json

import pytest

from stilla.jobs.lifecycle import JobError, JobStore
from stilla.media.workspace import ProjectWorkspace, WorkspaceError


def test_project_workspace_round_trip_and_list(tmp_path):
    workspace = ProjectWorkspace(tmp_path / "studio")
    project = workspace.create_project("launch_1", "Launch Video", language="en")
    workspace.save_document("launch_1", "brief", {"title": "Launch", "constraints": ["local only"]})
    assert project["id"] == "launch_1"
    assert workspace.load_project("launch_1")["title"] == "Launch Video"
    assert workspace.load_document("launch_1", "brief") == {
        "title": "Launch", "constraints": ["local only"]
    }
    assert [p["id"] for p in workspace.list_projects()] == ["launch_1"]


def test_workspace_never_overwrites_existing_project(tmp_path):
    workspace = ProjectWorkspace(tmp_path)
    workspace.create_project("one", "Original")
    with pytest.raises(FileExistsError):
        workspace.create_project("one", "Replacement")
    assert workspace.load_project("one")["title"] == "Original"


@pytest.mark.parametrize("project_id", ["../outside", "with spaces", "", "x" * 65])
def test_workspace_rejects_unsafe_project_ids(tmp_path, project_id):
    with pytest.raises(WorkspaceError):
        ProjectWorkspace(tmp_path).create_project(project_id, "Title")


def test_workspace_rejects_unsafe_document_names_and_oversized_data(tmp_path):
    workspace = ProjectWorkspace(tmp_path)
    workspace.create_project("p1", "Project")
    with pytest.raises(WorkspaceError):
        workspace.save_document("p1", "../brief", {})
    with pytest.raises(WorkspaceError, match="2 MB"):
        workspace.save_document("p1", "script", {"text": "x" * 2_000_001})


def test_workspace_rejects_non_json_values(tmp_path):
    workspace = ProjectWorkspace(tmp_path)
    workspace.create_project("p1", "Project")
    with pytest.raises(WorkspaceError):
        workspace.save_document("p1", "brief", {"not_json": object()})
    with pytest.raises(WorkspaceError):
        workspace.save_document("p1", "brief", {"not_finite": float("nan")})


def test_workspace_refuses_symlink_project_file(tmp_path):
    workspace = ProjectWorkspace(tmp_path / "studio")
    workspace.create_project("p1", "Project")
    outside = tmp_path / "outside.json"
    outside.write_text(json.dumps({"secret": True}), encoding="utf-8")
    target = tmp_path / "studio" / "projects" / "p1" / "documents" / "brief.json"
    target.symlink_to(outside)
    with pytest.raises(WorkspaceError):
        workspace.load_document("p1", "brief")
    with pytest.raises(WorkspaceError):
        workspace.save_document("p1", "brief", {"secret": False})
    assert json.loads(outside.read_text(encoding="utf-8")) == {"secret": True}


def test_job_state_transitions_persist_and_complete(tmp_path):
    jobs = JobStore(tmp_path / "jobs")
    created = jobs.create("job1", "script", project_id="project1", input_data={"brief": "hello"})
    assert created["state"] == "queued"
    jobs.transition("job1", "running")
    jobs.update_progress("job1", 42)
    completed = jobs.transition("job1", "completed", result={"script_id": "s1"})
    assert completed["progress"] == 100
    assert completed["result"] == {"script_id": "s1"}
    assert jobs.get("job1")["state"] == "completed"


def test_job_failure_and_cancel_are_terminal(tmp_path):
    jobs = JobStore(tmp_path)
    jobs.create("fail1", "render", project_id="p1", input_data={})
    jobs.transition("fail1", "running")
    failed = jobs.transition("fail1", "failed", error="Renderer unavailable")
    assert failed["error"] == "Renderer unavailable"
    with pytest.raises(JobError):
        jobs.transition("fail1", "running")

    jobs.create("cancel1", "image", project_id="p1", input_data={})
    cancelled = jobs.transition("cancel1", "cancelled")
    assert cancelled["state"] == "cancelled"
    with pytest.raises(JobError):
        jobs.transition("cancel1", "running")


def test_job_rejects_invalid_transitions_progress_and_duplicate_ids(tmp_path):
    jobs = JobStore(tmp_path)
    jobs.create("job1", "script", project_id="p1", input_data={})
    with pytest.raises(JobError):
        jobs.transition("job1", "completed", result={})
    with pytest.raises(JobError):
        jobs.create("job1", "script", project_id="p1", input_data={})
    jobs.transition("job1", "running")
    with pytest.raises(JobError):
        jobs.update_progress("job1", 30)
    jobs.update_progress("job1", 50)
    with pytest.raises(JobError):
        jobs.update_progress("job1", 20)
    with pytest.raises(JobError):
        jobs.transition("job1", "completed", progress=99, result={})
    with pytest.raises(JobError):
        jobs.transition("job1", "failed")
