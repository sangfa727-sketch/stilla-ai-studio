import pytest

from stilla.ai.comfyui_config import ComfyUIConfig, ComfyUIConfigurationError


def test_defaults_point_to_local_comfyui() -> None:
    config = ComfyUIConfig()
    assert config.base_url == "http://127.0.0.1:8188"
    assert config.prompt_url == "http://127.0.0.1:8188/prompt"


@pytest.mark.parametrize("url", [
    "https://127.0.0.1:8188",
    "http://example.com:8188",
    "http://192.168.1.10:8188",
    "http://user:pass@127.0.0.1:8188",
    "http://127.0.0.1:8188/?token=secret",
    "http://127.0.0.1:8188/api",
])
def test_rejects_nonlocal_or_ambiguous_endpoint(url: str) -> None:
    with pytest.raises(ComfyUIConfigurationError):
        ComfyUIConfig(base_url=url)


@pytest.mark.parametrize("timeout", [0, -1, 121, True, "10"])
def test_rejects_invalid_timeout(timeout: object) -> None:
    with pytest.raises(ComfyUIConfigurationError):
        ComfyUIConfig(timeout_seconds=timeout)  # type: ignore[arg-type]


@pytest.mark.parametrize("size", [0, -1, 10_485_761, True, 1.5])
def test_rejects_invalid_response_limit(size: object) -> None:
    with pytest.raises(ComfyUIConfigurationError):
        ComfyUIConfig(max_response_bytes=size)  # type: ignore[arg-type]


def test_normalizes_trailing_slash() -> None:
    assert ComfyUIConfig(base_url="http://localhost:8188/").base_url == "http://localhost:8188"
