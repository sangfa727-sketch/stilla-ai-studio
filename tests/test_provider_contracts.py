import pytest

from stilla.ai.providers import (
    ProviderConfig,
    ProviderConfigurationError,
    ProviderKind,
    select_provider,
)


def test_default_provider_is_local_loopback() -> None:
    config = ProviderConfig()
    assert config.kind is ProviderKind.LOCAL_OPENAI_COMPATIBLE
    assert config.base_url == "http://127.0.0.1:1234/v1"
    assert select_provider(config) is config


@pytest.mark.parametrize("url", ["https://example.com/v1", "http://192.168.1.20:1234/v1", "http://example.com/v1", "http://user:password@127.0.0.1:1234/v1"])
def test_local_provider_rejects_remote_or_credential_urls(url: str) -> None:
    with pytest.raises(ProviderConfigurationError):
        ProviderConfig(base_url=url)


def test_remote_provider_requires_explicit_opt_in_and_https() -> None:
    with pytest.raises(ProviderConfigurationError, match="allow_remote"):
        ProviderConfig(kind=ProviderKind.REMOTE_API, base_url="https://api.example.com/v1", api_key_env="STILLA_API_KEY")
    with pytest.raises(ProviderConfigurationError, match="HTTPS"):
        ProviderConfig(kind=ProviderKind.REMOTE_API, base_url="http://api.example.com/v1", allow_remote=True, api_key_env="STILLA_API_KEY")


def test_remote_provider_references_env_var_not_secret() -> None:
    config = ProviderConfig(kind=ProviderKind.REMOTE_API, base_url="https://api.example.com/v1", allow_remote=True, api_key_env="STILLA_API_KEY")
    assert config.is_ready_to_attempt
    assert not hasattr(config, "api_key")


def test_disabled_provider_is_never_selected() -> None:
    config = ProviderConfig(enabled=False)
    assert not config.is_ready_to_attempt
    with pytest.raises(ProviderConfigurationError, match="disabled"):
        select_provider(config)


def test_remote_provider_can_be_configured_disabled_without_opt_in() -> None:
    config = ProviderConfig(kind=ProviderKind.REMOTE_API, base_url="https://api.example.com/v1", enabled=False)
    assert not config.is_ready_to_attempt
    with pytest.raises(ProviderConfigurationError):
        select_provider(config)


def test_provider_rejects_embedded_credentials() -> None:
    with pytest.raises(ProviderConfigurationError, match="Credentials"):
        ProviderConfig(base_url="http://token@localhost:1234/v1")
