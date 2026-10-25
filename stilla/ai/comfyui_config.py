"""Configuration for an explicitly local ComfyUI image-generation server.

This module validates endpoint settings only; it never starts ComfyUI, downloads
models, or makes network requests.
"""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit


class ComfyUIConfigurationError(ValueError):
    """Raised when ComfyUI endpoint settings are invalid or unsafe."""


@dataclass(frozen=True, slots=True)
class ComfyUIConfig:
    """Loopback-only configuration for a local ComfyUI instance."""

    base_url: str = "http://127.0.0.1:8188"
    timeout_seconds: float = 10.0
    max_response_bytes: int = 1_048_576

    def __post_init__(self) -> None:
        if not isinstance(self.base_url, str) or len(self.base_url) > 2048:
            raise ComfyUIConfigurationError("base_url must be a URL string of at most 2048 characters")
        parsed = urlsplit(self.base_url.strip())
        if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise ComfyUIConfigurationError("ComfyUI must use plain HTTP on a loopback host")
        if parsed.username is not None or parsed.password is not None:
            raise ComfyUIConfigurationError("Credentials must not be embedded in base_url")
        if parsed.query or parsed.fragment:
            raise ComfyUIConfigurationError("base_url must not contain a query or fragment")
        if parsed.path not in {"", "/"}:
            raise ComfyUIConfigurationError("base_url must identify the ComfyUI server root")
        if (
            isinstance(self.timeout_seconds, bool)
            or not isinstance(self.timeout_seconds, (int, float))
            or not 0 < self.timeout_seconds <= 120
        ):
            raise ComfyUIConfigurationError("timeout_seconds must be greater than 0 and at most 120")
        if (
            isinstance(self.max_response_bytes, bool)
            or not isinstance(self.max_response_bytes, int)
            or not 1 <= self.max_response_bytes <= 10_485_760
        ):
            raise ComfyUIConfigurationError("max_response_bytes must be between 1 and 10485760")
        object.__setattr__(self, "base_url", urlunsplit(("http", parsed.netloc, "", "", "")))

    @property
    def system_stats_url(self) -> str:
        """Return the local server's system statistics endpoint."""
        return f"{self.base_url}/system_stats"

    @property
    def object_info_url(self) -> str:
        """Return the endpoint used to inspect installed ComfyUI node types."""
        return f"{self.base_url}/object_info"

    @property
    def prompt_url(self) -> str:
        """Return the workflow submission endpoint."""
        return f"{self.base_url}/prompt"

    @property
    def history_url(self) -> str:
        """Return the generation history endpoint."""
        return f"{self.base_url}/history"
