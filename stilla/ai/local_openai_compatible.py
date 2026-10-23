"""Configuration and URL validation for a local OpenAI-compatible API.

No model is downloaded or started by this module. Network requests are intentionally
implemented in a later milestone after the provider contract and error handling are tested.
"""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit


class ProviderConfigurationError(ValueError):
    """Raised when a local provider endpoint is unsafe or malformed."""


@dataclass(frozen=True, slots=True)
class LocalProviderConfig:
    """Validated configuration for a local OpenAI-compatible server."""

    base_url: str = "http://127.0.0.1:1234/v1"
    timeout_seconds: float = 30.0

    def __post_init__(self) -> None:
        parsed = urlsplit(self.base_url.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ProviderConfigurationError("base_url must be an absolute HTTP(S) URL")
        if parsed.username or parsed.password:
            raise ProviderConfigurationError("Credentials must not be embedded in base_url")
        if parsed.query or parsed.fragment:
            raise ProviderConfigurationError("base_url must not contain a query or fragment")
        if self.timeout_seconds <= 0:
            raise ProviderConfigurationError("timeout_seconds must be greater than zero")
        if parsed.scheme == "http" and parsed.hostname.lower() not in {
            "127.0.0.1", "localhost", "::1"
        }:
            raise ProviderConfigurationError(
                "Plain HTTP is allowed only for loopback hosts; use HTTPS for remote endpoints"
            )
        normalized_path = parsed.path.rstrip("/")
        object.__setattr__(
            self,
            "base_url",
            urlunsplit((parsed.scheme, parsed.netloc, normalized_path, "", "")),
        )

    @property
    def models_url(self) -> str:
        """Return the OpenAI-compatible model discovery endpoint."""
        return f"{self.base_url}/models"

    @property
    def chat_completions_url(self) -> str:
        """Return the OpenAI-compatible chat completion endpoint."""
        return f"{self.base_url}/chat/completions"
