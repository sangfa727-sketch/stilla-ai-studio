import json
from urllib.error import URLError

import pytest

from stilla.ai.comfyui_client import ComfyUIClient, ComfyUIClientError
from stilla.ai.comfyui_config import ComfyUIConfig


class FakeResponse:
    def __init__(self, value):
        self.payload = json.dumps(value).encode()
        self.headers = {"Content-Length": str(len(self.payload))}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def getcode(self):
        return 200

    def read(self, limit):
        return self.payload[:limit]


def test_submit_workflow_posts_to_local_prompt_endpoint(monkeypatch):
    seen = {}

    class Opener:
        def open(self, request, timeout):
            seen.update(url=request.full_url, method=request.get_method(), body=json.loads(request.data))
            return FakeResponse({"prompt_id": "12345678-abcd"})

    monkeypatch.setattr("stilla.ai.comfyui_client.build_opener", lambda handler: Opener())
    client = ComfyUIClient(ComfyUIConfig())
    assert client.submit_workflow({"1": {"class_type": "KSampler", "inputs": {}}}) == "12345678-abcd"
    assert seen["url"] == "http://127.0.0.1:8188/prompt"
    assert seen["method"] == "POST"
    assert seen["body"]["client_id"] == "stilla-ai-studio"


def test_rejects_oversized_workflow_before_network(monkeypatch):
    monkeypatch.setattr("stilla.ai.comfyui_client.build_opener", lambda handler: pytest.fail("network called"))
    with pytest.raises(ValueError, match="2 MiB"):
        ComfyUIClient(ComfyUIConfig()).submit_workflow({"prompt": "x" * (2 * 1024 * 1024)})


def test_rejects_invalid_prompt_id():
    with pytest.raises(ValueError, match="prompt_id"):
        ComfyUIClient(ComfyUIConfig()).get_history("../etc/passwd")


def test_history_returns_none_when_not_ready(monkeypatch):
    class Opener:
        def open(self, request, timeout):
            return FakeResponse({})

    monkeypatch.setattr("stilla.ai.comfyui_client.build_opener", lambda handler: Opener())
    assert ComfyUIClient(ComfyUIConfig()).get_history("12345678-abcd") is None


def test_sanitizes_connection_errors(monkeypatch):
    class Opener:
        def open(self, request, timeout):
            raise URLError("secret")

    monkeypatch.setattr("stilla.ai.comfyui_client.build_opener", lambda handler: Opener())
    with pytest.raises(ComfyUIClientError, match="Could not communicate") as error:
        ComfyUIClient(ComfyUIConfig()).submit_workflow({"1": {"class_type": "KSampler"}})
    assert "secret" not in str(error.value)
