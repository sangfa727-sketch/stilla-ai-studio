"""Fail-closed provider configuration for local-first AI features.

This module defines configuration only; it makes no network requests and never
silently selects a fallback provider.
"""

from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlsplit


class ProviderConfigurationError(ValueError):
    """Raised when provider settings violate local-first safety rules."""


class ProviderKind(str, Enum):
    LOCAL_OPENAI_COMPATIBLE = "local_openai_compatible"
    REMOTE_API = "remote_api"


@dataclass(frozen=True, slots=True)
class ProviderConfig:
    """Explicit provider settings; never stores an API secret directly."""

    kind: ProviderKind = ProviderKind.LOCAL_OPENAI_COMPATIBLE
    base_url: str = "http://127.0.0.1:1234/v1"
    enabled: bool = True
    allow_remote: bool = False
    api_key_env: str | None = None
    model: str | None = None
    timeout_seconds: float = 30.0

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ProviderKind):
            raise ProviderConfigurationError("kind must be an explicit ProviderKind")
        if not isinstance(self.enabled, bool) or not isinstance(self.allow_remote, bool):
            raise ProviderConfigurationError("enabled and allow_remote must be booleans")
        if not isinstance(self.base_url, str) or len(self.base_url) > 2048:
            raise ProviderConfigurationError("base_url must be a valid URL string")
        parsed = urlsplit(self.base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ProviderConfigurationError("base_url must use HTTP(S) and include a host")
        if parsed.username is not None or parsed.password is not None:
            raise ProviderConfigurationError("Credentials must not be embedded in base_url")
        if not isinstance(self.timeout_seconds, (int, float)) or isinstance(self.timeout_seconds, bool) or not 0 < self.timeout_seconds <= 300:
            raise ProviderConfigurationError("timeout_seconds must be greater than 0 and at most 300")
        if self.model is not None and (not isinstance(self.model, str) or not self.model.strip() or len(self.model) > 200):
            raise ProviderConfigurationError("model must be a non-empty string of at most 200 characters")
        if self.kind is ProviderKind.LOCAL_OPENAI_COMPATIBLE:
            if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "::1", "localhost"}:
                raise ProviderConfigurationError("Local provider must use plain HTTP on a loopback host")
            if self.allow_remote or self.api_key_env is not None:
                raise ProviderConfigurationError("Remote opt-in and API keys are not valid for local provider")
        elif self.enabled:
            if not self.allow_remote:
                raise ProviderConfigurationError("Remote provider requires explicit allow_remote=True opt-in")
            if parsed.scheme != "https":
                raise ProviderConfigurationError("Remote provider must use HTTPS")
            if not isinstance(self.api_key_env, str) or not self.api_key_env.isidentifier():
                raise ProviderConfigurationError("Remote provider requires an environment-variable name for its API key")

    @property
    def is_ready_to_attempt(self) -> bool:
        """Whether configuration permits an attempt, not whether the provider is reachable."""
        if not self.enabled:
            return False
        return self.kind is ProviderKind.LOCAL_OPENAI_COMPATIBLE or (self.allow_remote and self.api_key_env is not None)


def select_provider(config: ProviderConfig) -> ProviderConfig:
    """Return only the explicit provider selection; never silently fall back."""
    if not isinstance(config, ProviderConfig):
        raise ProviderConfigurationError("A validated ProviderConfig is required")
    if not config.is_ready_to_attempt:
        raise ProviderConfigurationError("Selected provider is disabled or not explicitly enabled")
    return config
