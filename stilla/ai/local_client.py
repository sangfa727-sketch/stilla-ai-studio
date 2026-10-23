"""Bounded, redirect-free transport for a local OpenAI-compatible API."""
from __future__ import annotations

import ipaddress
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from typing import Any
from urllib.request import HTTPRedirectHandler, Request, build_opener

from stilla.ai.local_openai_compatible import LocalProviderConfig


_MAX_RESPONSE_BYTES = 1_048_576


class ProviderConnectionError(RuntimeError):
    """Safe-to-display provider error; never includes response bodies or credentials."""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(
        self, req: Request, fp: Any, code: int, msg: str, headers: Any, newurl: str
    ) -> None:
        return None


def _is_loopback(hostname: str) -> bool:
    if hostname.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(hostname).is_loopback
    except ValueError:
        return False


class LocalOpenAICompatibleClient:
    """Minimal local-only HTTP client with bounded responses and no redirect following."""

    def __init__(self, config: LocalProviderConfig | None = None) -> None:
        self.config = config or LocalProviderConfig()
        parsed = urlsplit(self.config.base_url)
        if not _is_loopback(parsed.hostname or ""):
            raise ValueError("Local provider client only permits loopback hosts")
        self._opener = build_opener(_NoRedirect)

    def list_models(self) -> dict[str, Any]:
        return self._request(self.config.models_url)

    def chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict) or not payload:
            raise ValueError("payload must be a non-empty object")
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        if len(body) > 256_000:
            raise ValueError("request payload exceeds the 256 KB limit")
        return self._request(self.config.chat_completions_url, body)

    def _request(self, url: str, body: bytes | None = None) -> dict[str, Any]:
        headers = {"Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        request = Request(url, data=body, headers=headers, method="POST" if body else "GET")
        try:
            with self._opener.open(request, timeout=self.config.timeout_seconds) as response:
                data = response.read(_MAX_RESPONSE_BYTES + 1)
                if len(data) > _MAX_RESPONSE_BYTES:
                    raise ProviderConnectionError("Local provider response exceeded 1 MB")
        except HTTPError as exc:
            if 300 <= exc.code < 400:
                raise ProviderConnectionError("Local provider redirects are not allowed") from None
            raise ProviderConnectionError(
                f"Local provider returned HTTP {exc.code}"
            ) from None
        except (URLError, TimeoutError, OSError):
            # Do not expose exception strings: they may contain the configured URL.
            raise ProviderConnectionError(
                "Could not connect to the local provider; check that Bionic is running"
            ) from None
        try:
            result = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ProviderConnectionError("Local provider returned invalid JSON") from None
        if not isinstance(result, dict):
            raise ProviderConnectionError("Local provider returned an unexpected JSON shape")
        return result
