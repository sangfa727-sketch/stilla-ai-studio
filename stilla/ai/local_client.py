"""Bounded HTTP adapter for an explicitly selected local OpenAI-compatible provider."""

import json
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from stilla.ai.providers import ProviderConfig, ProviderConfigurationError, ProviderKind, select_provider

_MAX_RESPONSE_BYTES = 1_000_000


class ProviderRequestError(RuntimeError):
    """A sanitized provider request failure."""


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class LocalOpenAICompatibleClient:
    """Small synchronous local adapter; no cloud fallback and no prompt logging."""

    def __init__(self, config: ProviderConfig):
        selected = select_provider(config)
        if selected.kind is not ProviderKind.LOCAL_OPENAI_COMPATIBLE:
            raise ProviderConfigurationError("This client only supports the local provider")
        self._config = selected
        self._opener = build_opener(_NoRedirectHandler())

    def list_models(self) -> list[str]:
        payload = self._request("GET", "/models")
        data = payload.get("data")
        if not isinstance(data, list):
            raise ProviderRequestError("Provider returned an invalid model list")
        return [
            item["id"] for item in data
            if isinstance(item, dict) and isinstance(item.get("id"), str)
            and item["id"].strip() and len(item["id"]) <= 200
        ]

    def chat(self, messages: list[dict[str, str]], *, model: str | None = None) -> str:
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

        chosen_model = model if model is not None else self._config.model
        if chosen_model is None:
            available = self.list_models()
            if not available:
                raise ProviderRequestError("Local provider has no available models")
            chosen_model = available[0]
        if not isinstance(chosen_model, str) or not chosen_model.strip() or len(chosen_model) > 200:
            raise ValueError("model must be a non-empty string of at most 200 characters")

        payload = self._request("POST", "/chat/completions", {
            "model": chosen_model, "messages": checked_messages, "stream": False,
        })
        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            raise ProviderRequestError("Provider returned an invalid completion")
        message = choices[0].get("message")
        if not isinstance(message, dict) or not isinstance(message.get("content"), str):
            raise ProviderRequestError("Provider returned an invalid completion")
        return message["content"]

    def _request(self, method: str, path: str, body: dict | None = None) -> dict:
        url = self._config.base_url.rstrip("/") + path
        data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
        request = Request(url, data=data, method=method, headers={"Accept": "application/json"})
        if data is not None:
            request.add_header("Content-Type", "application/json")
        try:
            with self._opener.open(request, timeout=self._config.timeout_seconds) as response:
                raw = response.read(_MAX_RESPONSE_BYTES + 1)
        except HTTPError as exc:
            if exc.code in {301, 302, 303, 307, 308}:
                raise ProviderRequestError("Provider redirects are not permitted") from None
            raise ProviderRequestError(f"Provider returned HTTP status {exc.code}") from None
        except (URLError, TimeoutError, OSError):
            raise ProviderRequestError("Could not reach the local AI provider or request timed out") from None
        if len(raw) > _MAX_RESPONSE_BYTES:
            raise ProviderRequestError("Provider response exceeded the size limit")
        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ProviderRequestError("Provider returned invalid JSON") from None
        if not isinstance(payload, dict):
            raise ProviderRequestError("Provider returned an invalid response")
        return payload
