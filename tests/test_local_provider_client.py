import json
from urllib.error import URLError

import pytest

from stilla.ai.local_client import LocalOpenAICompatibleClient, ProviderRequestError
from stilla.ai.providers import ProviderConfig, ProviderConfigurationError, ProviderKind


class FakeResponse:
    def __init__(self, payload):
        self.raw = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, size=-1):
        return self.raw[:size]


class FakeOpener:
    def __init__(self, payloads):
        self.payloads = list(payloads)
        self.requests = []

    def open(self, request, timeout):
        self.requests.append((request, timeout))
        result = self.payloads.pop(0)
        if isinstance(result, Exception):
            raise result
        return FakeResponse(result)


def test_list_models_reads_model_ids_from_local_server():
    client = LocalOpenAICompatibleClient(ProviderConfig())
    opener = FakeOpener([{"data": [{"id": "qwen-local"}, {"id": "other"}, {"name": "invalid"}]}])
    client._opener = opener

    assert client.list_models() == ["qwen-local", "other"]
    assert opener.requests[0][0].full_url == "http://127.0.0.1:1234/v1/models"
    assert opener.requests[0][1] == 30.0


def test_chat_discovers_model_and_posts_completion():
    client = LocalOpenAICompatibleClient(ProviderConfig())
    opener = FakeOpener([
        {"data": [{"id": "qwen-local"}]},
        {"choices": [{"message": {"content": "Hello"}}]},
    ])
    client._opener = opener

    assert client.chat([{"role": "user", "content": "Hi"}]) == "Hello"
    request = opener.requests[1][0]
    payload = json.loads(request.data)
    assert payload["model"] == "qwen-local"
    assert payload["stream"] is False


def test_configured_model_skips_discovery():
    client = LocalOpenAICompatibleClient(ProviderConfig(model="selected-model"))
    opener = FakeOpener([{"choices": [{"message": {"content": "ok"}}]}])
    client._opener = opener

    assert client.chat([{"role": "user", "content": "Hi"}]) == "ok"
    assert len(opener.requests) == 1


def test_invalid_messages_fail_before_request():
    client = LocalOpenAICompatibleClient(ProviderConfig())
    opener = FakeOpener([])
    client._opener = opener

    with pytest.raises(ValueError):
        client.chat([{"role": "user", "content": "x", "extra": "not allowed"}])
    assert opener.requests == []


def test_invalid_provider_response_is_sanitized():
    client = LocalOpenAICompatibleClient(ProviderConfig())
    client._opener = FakeOpener([{"data": "not-a-list"}])

    with pytest.raises(ProviderRequestError, match="unexpected JSON shape"):
        client.list_models()


def test_response_size_is_bounded():
    client = LocalOpenAICompatibleClient(ProviderConfig())

    class HugeResponse(FakeResponse):
        def read(self, size=-1):
            return b"x" * size

    class HugeOpener:
        def open(self, request, timeout):
            return HugeResponse({})

    client._opener = HugeOpener()
    with pytest.raises(ProviderRequestError, match="exceeded 1 MB"):
        client.list_models()


def test_network_errors_are_sanitized():
    client = LocalOpenAICompatibleClient(ProviderConfig())
    client._opener = FakeOpener([URLError("private detail")])
    with pytest.raises(ProviderRequestError, match="Could not connect"):
        client.list_models()


def test_local_client_rejects_remote_provider():
    config = ProviderConfig(
        kind=ProviderKind.REMOTE_API,
        base_url="https://api.example.com/v1",
        allow_remote=True,
        api_key_env="STILLA_API_KEY",
    )
    with pytest.raises(ProviderConfigurationError, match="only supports the local"):
        LocalOpenAICompatibleClient(config)


def test_empty_explicit_model_is_rejected_not_silently_replaced():
    client = LocalOpenAICompatibleClient(ProviderConfig(model="configured"))
    client._opener = FakeOpener([])
    with pytest.raises(ValueError, match="model must be"):
        client.chat([{"role": "user", "content": "Hi"}], model="")
    assert client._opener.requests == []


def test_unhashable_message_role_fails_as_validation_error_before_request():
    client = LocalOpenAICompatibleClient(ProviderConfig())
    opener = FakeOpener([])
    client._opener = opener

    with pytest.raises(ValueError, match="message role or content is invalid"):
        client.chat([{"role": [], "content": "Hi"}])
    assert opener.requests == []


def test_non_object_model_response_is_rejected_cleanly():
    client = LocalOpenAICompatibleClient(ProviderConfig())
    client._opener = FakeOpener([["unexpected", "array"]])

    with pytest.raises(ProviderRequestError, match="invalid model list"):
        client.list_models()
