from pathlib import Path

import pytest

from stilla.desktop.workspace_api import DesktopAPIError, DesktopWorkspaceAPI


def node(*required: str) -> dict[str, object]:
    return {"input": {"required": {name: ["STRING"] for name in required}}}


def test_desktop_api_returns_read_only_conditioning_capability_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []

    def fake_get_json(config, path: str):
        assert config.base_url == "http://127.0.0.1:8188"
        calls.append(path)
        if path == "system_stats":
            return {"system": {"comfyui_version": "0.3.26"}}
        return {
            "IPAdapterModelLoader": node("ipadapter_file"),
            "IPAdapterApply": node("ipadapter", "clip_vision", "image", "model", "weight"),
        }

    monkeypatch.setattr("stilla.ai.comfyui_capabilities._get_json", fake_get_json)
    report = DesktopWorkspaceAPI(tmp_path / "workspace").inspect_comfyui_capabilities(
        "http://127.0.0.1:8188"
    )

    ipadapter = next(item for item in report["capabilities"] if item["capability"] == "ipadapter")
    instantid = next(item for item in report["capabilities"] if item["capability"] == "instantid")
    assert calls == ["system_stats", "object_info"]
    assert report["comfyui_version"] == "0.3.26"
    assert report["node_count"] == 2
    assert ipadapter["status"] == "available"
    assert instantid["status"] == "unsupported"
    assert report["generation_ready"] is False


def test_desktop_api_rejects_remote_comfyui_capability_endpoint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def unexpected_request(*args, **kwargs):
        pytest.fail("Remote endpoint must be rejected before any request")

    monkeypatch.setattr("stilla.ai.comfyui_capabilities._get_json", unexpected_request)
    api = DesktopWorkspaceAPI(tmp_path / "workspace")

    with pytest.raises(DesktopAPIError, match="safely inspect"):
        api.inspect_comfyui_capabilities("http://example.com")


def test_desktop_api_sanitizes_comfyui_capability_inspection_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(config, path):
        raise OSError("private endpoint or local path")

    monkeypatch.setattr("stilla.ai.comfyui_capabilities._get_json", fail)
    api = DesktopWorkspaceAPI(tmp_path / "workspace")

    with pytest.raises(DesktopAPIError) as error:
        api.inspect_comfyui_capabilities("http://127.0.0.1:8188")

    assert "private endpoint" not in str(error.value)
    assert "local path" not in str(error.value)
