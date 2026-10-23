import io
import json
from urllib.error import HTTPError, URLError
from unittest.mock import Mock

import pytest

from stilla.ai.local_client import LocalOpenAICompatibleClient, ProviderConnectionError
from stilla.ai.local_openai_compatible import LocalProviderConfig


class FakeResponse:
    def __init__(self, payload: bytes):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, size=-1):
        return self.payload[:size]


def client():
    instance = LocalOpenAICompatibleClient(LocalProviderConfig())
    instance._opener = Mock()
    return instance


def test_list_models_uses_get_and_parses_json():
    instance = client()
    instance._opener.open.return_value = FakeResponse(b'{"data": []}')
    assert instance.list_models() == {"data": []}
    request = instance._opener.open.call_args.args[0]
    assert request.method == "GET"
    assert request.full_url == "http://127.0.0.1:1234/v1/models"


def test_chat_completions_posts_json():
    instance = client()
    instance._opener.open.return_value = FakeResponse(b'{"choices": []}')
    assert instance.chat_completions({"model": "test", "messages": []}) == {"choices": []}
    request = instance._opener.open.call_args.args[0]
    assert request.method == "POST"
    assert json.loads(request.data) == {"model": "test", "messages": []}


def test_remote_host_is_rejected_by_local_client():
    with pytest.raises(ValueError, match="loopback"):
        LocalOpenAICompatibleClient(LocalProviderConfig("https://api.example.com/v1"))


def test_rejects_empty_or_oversized_request():
    instance = client()
    with pytest.raises(ValueError):
        instance.chat_completions({})
    with pytest.raises(ValueError, match="256 KB"):
        instance.chat_completions({"content": "x" * 270_000})


def test_response_size_is_bounded():
    instance = client()
    instance._opener.open.return_value = FakeResponse(b" " * (1_048_577))
    with pytest.raises(ProviderConnectionError, match="exceeded 1 MB"):
        instance.list_models()


def test_invalid_json_is_reported_without_body():
    instance = client()
    instance._opener.open.return_value = FakeResponse(b"not-json secret-token")
    with pytest.raises(ProviderConnectionError, match="invalid JSON") as exc:
        instance.list_models()
    assert "secret-token" not in str(exc.value)


def test_redirect_is_not_followed():
    instance = client()
    instance._opener.open.side_effect = HTTPError(
        "http://127.0.0.1:1234/v1/models", 302, "Found", {}, io.BytesIO()
    )
    with pytest.raises(ProviderConnectionError, match="redirects are not allowed"):
        instance.list_models()


def test_connection_error_does_not_disclose_url():
    instance = client()
    instance._opener.open.side_effect = URLError("failed at http://secret.example/token")
    with pytest.raises(ProviderConnectionError) as exc:
        instance.list_models()
    assert "secret.example" not in str(exc.value)
    assert "token" not in str(exc.value)
