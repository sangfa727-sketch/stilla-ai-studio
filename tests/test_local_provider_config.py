import pytest

from stilla.ai.local_openai_compatible import (
    LocalProviderConfig,
    ProviderConfigurationError,
)


def test_defaults_target_existing_bionic_local_api() -> None:
    config = LocalProviderConfig()
    assert config.base_url == "http://127.0.0.1:1234/v1"
    assert config.models_url == "http://127.0.0.1:1234/v1/models"
    assert config.chat_completions_url == (
        "http://127.0.0.1:1234/v1/chat/completions"
    )


def test_trailing_slashes_are_normalized() -> None:
    assert LocalProviderConfig("http://localhost:1234/v1/").base_url == (
        "http://localhost:1234/v1"
    )


@pytest.mark.parametrize(
    "url",
    [
        "",
        "localhost:1234/v1",
        "file:///tmp/api",
        "http://user:secret@127.0.0.1:1234/v1",
        "http://example.com/v1",
        "http://127.0.0.1/v1?token=secret",
        "http://127.0.0.1/v1#fragment",
    ],
)
def test_rejects_unsafe_or_malformed_urls(url: str) -> None:
    with pytest.raises(ProviderConfigurationError):
        LocalProviderConfig(url)


def test_rejects_non_positive_timeout() -> None:
    with pytest.raises(ProviderConfigurationError):
        LocalProviderConfig(timeout_seconds=0)


def test_remote_https_endpoint_is_allowed() -> None:
    assert LocalProviderConfig("https://api.example.com/v1").models_url == (
        "https://api.example.com/v1/models"
    )
