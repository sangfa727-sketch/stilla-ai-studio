from __future__ import annotations

from pathlib import Path

import pytest

from stilla.desktop.workspace_api import DesktopAPIError, DesktopWorkspaceAPI


def test_runtime_settings_default_and_persist_across_api_instances(tmp_path: Path) -> None:
    root = tmp_path / "workspace"
    api = DesktopWorkspaceAPI(root)
    assert api.get_local_runtime_settings() == {
        "schema_version": 1,
        "qwen_base_url": "http://127.0.0.1:1234/v1",
        "qwen_model": "qwen2.5-7b-instruct-uncensored",
        "comfyui_base_url": "http://127.0.0.1:8188",
    }

    saved = api.save_local_runtime_settings(
        "http://127.0.0.1:1234/v1",
        "qwen2.5-local",
        "http://127.0.0.1:8189",
    )
    reopened = DesktopWorkspaceAPI(root)
    assert reopened.get_local_runtime_settings() == saved
    assert saved["qwen_model"] == "qwen2.5-local"


def test_runtime_settings_reject_remote_endpoint_without_overwriting_existing(
    tmp_path: Path,
) -> None:
    api = DesktopWorkspaceAPI(tmp_path / "workspace")
    original = api.get_local_runtime_settings()
    with pytest.raises(DesktopAPIError, match="safely save"):
        api.save_local_runtime_settings(
            "https://example.com/v1",
            "qwen",
            "http://127.0.0.1:8188",
        )
    assert api.get_local_runtime_settings() == original


def test_runtime_settings_reject_invalid_model_id(tmp_path: Path) -> None:
    api = DesktopWorkspaceAPI(tmp_path / "workspace")
    with pytest.raises(DesktopAPIError, match="safely save"):
        api.save_local_runtime_settings(
            "http://127.0.0.1:1234/v1",
            "   ",
            "http://127.0.0.1:8188",
        )


def test_runtime_settings_refuse_symlink_target(tmp_path: Path) -> None:
    api = DesktopWorkspaceAPI(tmp_path / "workspace")
    target = tmp_path / "outside.json"
    target.write_text('{"untouched": true}', encoding="utf-8")
    settings_path = tmp_path / "workspace" / ".stilla-runtime-settings.json"
    try:
        settings_path.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks are unavailable on this platform")

    with pytest.raises(DesktopAPIError, match="unsafe"):
        api.get_local_runtime_settings()
    with pytest.raises(DesktopAPIError, match="unsafe"):
        api.save_local_runtime_settings(
            "http://127.0.0.1:1234/v1",
            "qwen",
            "http://127.0.0.1:8188",
        )
    assert target.read_text(encoding="utf-8") == '{"untouched": true}'
