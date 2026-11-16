"""Bounded, loopback-only health checks for local AI runtimes.

This module performs metadata GET requests only. It never downloads models,
sends prompts, follows redirects, or contacts non-loopback hosts.
"""
from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import (
    HTTPRedirectHandler,
    ProxyHandler,
    Request,
    build_opener,
)

DEFAULT_QWEN_BASE_URL = "http://127.0.0.1:1234/v1"
DEFAULT_QWEN_MODEL = "qwen2.5-7b-instruct-uncensored"
DEFAULT_COMFYUI_BASE_URL = "http://127.0.0.1:8188"
_MAX_RESPONSE_BYTES = 256 * 1024
_MAX_MODELS = 100
_ALLOWED_HOSTS = {"127.0.0.1", "::1"}


class LocalRuntimeError(ValueError):
    """A sanitized local-runtime configuration or health-check failure."""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, file_pointer, code, message, headers, new_url):
        return None


def _normalize_loopback_url(value: str, *, service: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 2048:
        raise LocalRuntimeError(f"{service} endpoint must be a valid URL")
    try:
        parsed = urlsplit(value.strip())
        port = parsed.port
    except ValueError:
        raise LocalRuntimeError(f"{service} endpoint is invalid") from None
    if (
        parsed.scheme != "http"
        or parsed.hostname not in _ALLOWED_HOSTS
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise LocalRuntimeError(f"{service} endpoint must use HTTP on this computer only")
    if port is not None and not 1 <= port <= 65535:
        raise LocalRuntimeError(f"{service} endpoint port is invalid")
    path = parsed.path.rstrip("/")
    allowed_paths = {"/v1"} if service == "Qwen" else {""}
    if path not in allowed_paths:
        raise LocalRuntimeError(f"{service} endpoint path is not supported")
    authority = parsed.netloc
    return f"http://{authority}{path}"


def validate_runtime_settings(
    qwen_base_url: str = DEFAULT_QWEN_BASE_URL,
    qwen_model: str = DEFAULT_QWEN_MODEL,
    comfyui_base_url: str = DEFAULT_COMFYUI_BASE_URL,
) -> dict[str, object]:
    """Validate and normalize non-secret local endpoint/model preferences."""
    if (
        not isinstance(qwen_model, str)
        or not qwen_model.strip()
        or len(qwen_model) > 200
    ):
        raise LocalRuntimeError("Qwen model ID must contain 1 to 200 characters")
    return {
        "schema_version": 1,
        "qwen_base_url": _normalize_loopback_url(qwen_base_url, service="Qwen"),
        "qwen_model": qwen_model.strip(),
        "comfyui_base_url": _normalize_loopback_url(comfyui_base_url, service="ComfyUI"),
    }


def _get_json(url: str, *, service: str, timeout_seconds: float = 3.0) -> dict:
    request = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "STILLA-AI-Studio"},
        method="GET",
    )
    opener = build_opener(ProxyHandler({}), _NoRedirect)
    try:
        with opener.open(request, timeout=timeout_seconds) as response:
            if response.status != 200:
                raise LocalRuntimeError(f"{service} returned HTTP {response.status}")
            raw = response.read(_MAX_RESPONSE_BYTES + 1)
    except HTTPError as exc:
        raise LocalRuntimeError(f"{service} returned HTTP {exc.code}") from None
    except (URLError, TimeoutError, OSError):
        raise LocalRuntimeError(
            f"{service} is unavailable. Check that its local server is running."
        ) from None
    if len(raw) > _MAX_RESPONSE_BYTES:
        raise LocalRuntimeError(f"{service} response exceeded the 256 KB safety limit")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError):
        raise LocalRuntimeError(f"{service} returned invalid JSON") from None
    if not isinstance(payload, dict):
        raise LocalRuntimeError(f"{service} returned an unsupported response")
    return payload


def discover_qwen_models(base_url: str, selected_model: str) -> dict[str, object]:
    """Discover OpenAI-compatible model IDs; does not send prompts or run inference."""
    settings = validate_runtime_settings(
        qwen_base_url=base_url,
        qwen_model=selected_model,
        comfyui_base_url=DEFAULT_COMFYUI_BASE_URL,
    )
    endpoint = str(settings["qwen_base_url"]) + "/models"
    payload = _get_json(endpoint, service="Qwen")
    entries = payload.get("data")
    if not isinstance(entries, list):
        raise LocalRuntimeError("Qwen /models response is missing its data list")
    models: list[str] = []
    for entry in entries[:_MAX_MODELS]:
        if isinstance(entry, dict) and isinstance(entry.get("id"), str):
            model_id = entry["id"].strip()
            if model_id and len(model_id) <= 200 and model_id not in models:
                models.append(model_id)
    if not models:
        raise LocalRuntimeError("Qwen returned no usable model IDs")
    return {
        "connected": True,
        "models": models,
        "selected_model": settings["qwen_model"],
        "selected_model_available": settings["qwen_model"] in models,
    }


def check_comfyui_status(base_url: str) -> dict[str, object]:
    """Check ComfyUI's local system_stats endpoint without submitting a workflow."""
    endpoint = _normalize_loopback_url(base_url, service="ComfyUI") + "/system_stats"
    payload = _get_json(endpoint, service="ComfyUI")
    system = payload.get("system")
    devices = payload.get("devices")
    if not isinstance(system, dict) or not isinstance(devices, list):
        raise LocalRuntimeError("ComfyUI system status response has an unsupported structure")
    version = system.get("comfyui_version")
    return {
        "connected": True,
        "version": version if isinstance(version, str) and len(version) <= 80 else None,
        "device_count": len(devices),
    }
