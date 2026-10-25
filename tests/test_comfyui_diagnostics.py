import json
from urllib.error import URLError

import pytest

from stilla.ai.comfyui_config import ComfyUIConfig
from stilla.ai import comfyui_diagnostics as diagnostics


class FakeResponse:
    def __init__(self, value: object):
        self.value = value
        self.headers = {"Content-Length": str(len(json.dumps(value).encode()))}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def getcode(self):
        return 200

    def read(self, limit: int):
        return json.dumps(self.value).encode()[:limit]


def test_diagnostics_discovers_nodes_without_submitting_workflows(monkeypatch) -> None:
    calls = []

    def fake_get_json(config, path):
        calls.append(path)
        if path == "system_stats":
            return {"system": {}}
        return {"KSampler": {}, "CheckpointLoaderSimple": {}}

    monkeypatch.setattr(diagnostics, "_get_json", fake_get_json)
    result = diagnostics.diagnose_comfyui(ComfyUIConfig())
    assert result.reachable
    assert result.system_stats_available
    assert result.object_info_available
    assert result.node_count == 2
    assert calls == ["system_stats", "object_info"]
    assert "prompt" not in calls


def test_diagnostics_reports_server_unavailable(monkeypatch) -> None:
    def fail(config, path):
        raise URLError("private endpoint detail")

    monkeypatch.setattr(diagnostics, "_get_json", fail)
    result = diagnostics.diagnose_comfyui(ComfyUIConfig())
    assert not result.reachable
    assert result.node_count == 0
    assert "private endpoint detail" not in result.message


def test_diagnostics_reports_invalid_node_catalog(monkeypatch) -> None:
    monkeypatch.setattr(
        diagnostics, "_get_json",
        lambda config, path: {"ok": True} if path == "system_stats" else ["not", "a", "mapping"],
    )
    result = diagnostics.diagnose_comfyui(ComfyUIConfig())
    assert result.reachable
    assert not result.object_info_available
    assert result.node_count == 0


def test_get_json_rejects_oversized_response(monkeypatch) -> None:
    class Oversized(FakeResponse):
        def __init__(self):
            self.headers = {"Content-Length": "9999"}

    monkeypatch.setattr(diagnostics, "build_opener", lambda handler: type(
        "Opener", (), {"open": lambda self, request, timeout: Oversized()}
    )())
    with pytest.raises(ValueError, match="size limit"):
        diagnostics._get_json(ComfyUIConfig(max_response_bytes=20), "system_stats")
