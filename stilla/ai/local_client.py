"""Bounded, redirect-free transport for a local OpenAI-compatible API."""

from __future__ import annotations

import ipaddress
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from stilla.ai.local_openai_compatible import LocalProviderConfig
from stilla.ai.providers import (
    ProviderConfig,
    ProviderConfigurationError,
    ProviderKind,
    select_provider,
)

_MAX_RESPONSE_BYTES = 1_048_576
_MAX_REQUEST_BYTES = 256_000


class ProviderConnectionError(RuntimeError):
    """Safe-to-display provider error; never includes response bodies or credentials."""


ProviderRequestError = ProviderConnectionError


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req: Request, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


def _is_loopback(hostname: str) -> bool:
    if hostname.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(hostname).is_loopback
    except ValueError:
        return False


class LocalOpenAICompatibleClient:
    """Local-only HTTP client supporting the legacy transport and a typed chat helper."""

    def __init__(self, config: LocalProviderConfig | ProviderConfig | None = None) -> None:
        self._provider_config: ProviderConfig | None = None
        if config is None or isinstance(config, LocalProviderConfig):
            self.config = config or LocalProviderConfig()
            parsed = urlsplit(self.config.base_url)
            if not _is_loopback(parsed.hostname or ""):
                raise ValueError("Local provider client only permits loopback hosts")
            self._base_url = self.config.base_url
            self._timeout_seconds = self.config.timeout_seconds
        elif isinstance(config, ProviderConfig):
            selected = select_provider(config)
            if selected.kind is not ProviderKind.LOCAL_OPENAI_COMPATIBLE:
                raise ProviderConfigurationError("This client only supports the local provider")
            self._provider_config = selected
            self._base_url = selected.base_url.rstrip("/")
            self._timeout_seconds = selected.timeout_seconds
            self.config = LocalProviderConfig(self._base_url, self._timeout_seconds)
        else:
            raise TypeError("config must be LocalProviderConfig or ProviderConfig")
        self._opener = build_opener(_NoRedirect())

    def list_models(self) -> dict[str, Any] | list[str]:
        payload = self._request(self._base_url.rstrip("/") + "/models")
        if self._provider_config is None:
            return payload
        data = payload.get("data")
        if not isinstance(data, list):
            raise ProviderConnectionError("Provider returned an invalid model list")
        return [
            item["id"] for item in data
            if isinstance(item, dict) and isinstance(item.get("id"), str)
            and item["id"].strip() and len(item["id"]) <= 200
        ]

    def chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Legacy low-level completion call with a strict bounded JSON payload."""
        if not isinstance(payload, dict) or not payload:
            raise ValueError("payload must be a non-empty object")
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        if len(body) > _MAX_REQUEST_BYTES:
            raise ValueError("request payload exceeds the 256 KB limit")
        return self._request(self._base_url.rstrip("/") + "/chat/completions", body)

    def chat(self, messages: list[dict[str, str]], *, model: str | None = None) -> str:
        """Validate chat messages and return a non-streaming completion string."""
        if self._provider_config is None:
            raise ProviderConfigurationError("chat() requires the validated ProviderConfig contract")
        if not isinstance(messages, list) or not messages or len(messages) > 100:
            raise ValueError("messages must contain between 1 and 100 items")
        checked_messages = []
        for message in messages:
            if not isinstance(message, dict) or set(message) != {"role", "content"}:
                raise ValueError("each message must contain only role and content")
            role, content = message["role"], message["content"]
            if role not in {"system", "user", "assistant"} or not isinstance(content, str):
                raise ValueError("message role or content is invalid")
            if len(content) > 100_000:
                raise ValueError("message content exceeds the size limit")
            checked_messages.append({"role": role, "content": content})
        chosen_model = model if model is not None else self._provider_config.model
        if chosen_model is None:
            models = self.list_models()
            if not models:
                raise ProviderConnectionError("Local provider has no available models")
            chosen_model = models[0]
        if not isinstance(chosen_model, str) or not chosen_model.strip() or len(chosen_model) > 200:
            raise ValueError("model must be a non-empty string of at most 200 characters")
        payload = self.chat_completions({
            "model": chosen_model, "messages": checked_messages, "stream": False,
        })
        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            raise ProviderConnectionError("Provider returned an invalid completion")
        message = choices[0].get("message")
        if not isinstance(message, dict) or not isinstance(message.get("content"), str):
            raise ProviderConnectionError("Provider returned an invalid completion")
        return message["content"]

    def _request(self, url: str, body: bytes | None = None) -> dict[str, Any]:
        headers = {"Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        request = Request(url, data=body, headers=headers, method="POST" if body is not None else "GET")
        try:
            with self._opener.open(request, timeout=self._timeout_seconds) as response:
                data = response.read(_MAX_RESPONSE_BYTES + 1)
                if len(data) > _MAX_RESPONSE_BYTES:
                    raise ProviderConnectionError("Local provider response exceeded 1 MB")
        except HTTPError as exc:
            if 300 <= exc.code < 400:
                raise ProviderConnectionError("Local provider redirects are not allowed") from None
            raise ProviderConnectionError(f"Local provider returned HTTP {exc.code}") from None
        except (URLError, TimeoutError, OSError):
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
