import pytest

from stilla.ai.diagnostics import diagnose_local_provider
from stilla.ai.local_client import ProviderConnectionError
from stilla.ai.providers import ProviderConfig, ProviderKind


class FakeClient:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = 0

    def list_models(self):
        self.calls += 1
        if self.error:
            raise self.error
        return self.result


def test_diagnostics_discovers_local_models_without_calling_chat():
    client = FakeClient(["qwen2.5-7b-instruct", "", 123, "x" * 201])
    result = diagnose_local_provider(ProviderConfig(), client)
    assert result.configured and result.reachable
    assert result.models == ("qwen2.5-7b-instruct",)
    assert result.message == "Local AI server is ready"
    assert client.calls == 1


def test_diagnostics_handles_openai_style_model_payload():
    client = FakeClient({"data": [{"id": "qwen-local"}, {"id": 3}, {}]})
    result = diagnose_local_provider(ProviderConfig(), client)
    assert result.models == ("qwen-local",)


def test_diagnostics_returns_safe_message_when_server_is_unavailable():
    client = FakeClient(error=ProviderConnectionError("secret response content"))
    result = diagnose_local_provider(ProviderConfig(), client)
    assert result.configured and not result.reachable
    assert "secret" not in result.message
    assert result.models == ()


def test_diagnostics_reports_empty_model_list():
    result = diagnose_local_provider(ProviderConfig(), FakeClient([]))
    assert result.reachable
    assert not result.models
    assert "no models" in result.message


def test_disabled_local_provider_returns_status_without_network_call():
    client = FakeClient(["should-not-be-requested"])
    result = diagnose_local_provider(ProviderConfig(enabled=False), client)
    assert not result.configured and not result.reachable
    assert result.message == "Local provider is disabled"
    assert client.calls == 0


def test_diagnostics_refuses_remote_provider():
    config = ProviderConfig(
        kind=ProviderKind.REMOTE_API,
        base_url="https://api.example.com/v1",
        allow_remote=True,
        api_key_env="STILLA_API_KEY",
    )
    with pytest.raises(ValueError, match="only the local provider"):
        diagnose_local_provider(config, FakeClient([]))
