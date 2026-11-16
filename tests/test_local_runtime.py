from __future__ import annotations

import json
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Iterator

import pytest

from stilla.ai.local_runtime import (
    DEFAULT_COMFYUI_BASE_URL,
    DEFAULT_QWEN_BASE_URL,
    DEFAULT_QWEN_MODEL,
    LocalRuntimeError,
    test_comfyui_connection as check_comfyui_connection,
    test_qwen_connection as check_qwen_connection,
    validate_runtime_settings,
)


@contextmanager
def local_server(routes: dict[str, tuple[int, object]]) -> Iterator[str]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            status, payload = routes.get(self.path, (404, {"error": "not found"}))
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            if isinstance(payload, bytes):
                self.wfile.write(payload)
            else:
                self.wfile.write(json.dumps(payload).encode("utf-8"))

        def log_message(self, format: str, *args: object) -> None:
            return

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()


def test_default_runtime_settings_are_local_and_valid() -> None:
    settings = validate_runtime_settings()
    assert settings == {
        "schema_version": 1,
        "qwen_base_url": DEFAULT_QWEN_BASE_URL,
        "qwen_model": DEFAULT_QWEN_MODEL,
        "comfyui_base_url": DEFAULT_COMFYUI_BASE_URL,
    }


@pytest.mark.parametrize(
    "url",
    [
        "https://127.0.0.1/v1",
        "http://example.com/v1",
        "http://127.0.0.1.evil.test/v1",
        "http://user:pass@127.0.0.1/v1",
        "http://127.0.0.1/v1?token=x",
        "http://127.0.0.1/v2",
    ],
)
def test_qwen_rejects_non_loopback_or_unsupported_urls(url: str) -> None:
    with pytest.raises(LocalRuntimeError):
        validate_runtime_settings(qwen_base_url=url)


@pytest.mark.parametrize("url", ["http://example.com", "https://127.0.0.1", "http://127.0.0.1/ui"])
def test_comfyui_rejects_non_loopback_or_unsupported_urls(url: str) -> None:
    with pytest.raises(LocalRuntimeError):
        validate_runtime_settings(comfyui_base_url=url)


def test_qwen_discovers_model_ids_and_reports_selected_model() -> None:
    with local_server({"/v1/models": (200, {"data": [{"id": "qwen-local"}, {"id": "other"}, {"id": "qwen-local"}]})}) as root:
        result = check_qwen_connection(root + "/v1", "qwen-local")
    assert result == {
        "connected": True,
        "models": ["qwen-local", "other"],
        "selected_model": "qwen-local",
        "selected_model_available": True,
    }


def test_qwen_connection_distinguishes_unavailable_selected_model() -> None:
    with local_server({"/v1/models": (200, {"data": [{"id": "qwen-local"}]})}) as root:
        result = check_qwen_connection(root + "/v1", "missing-model")
    assert result["connected"] is True
    assert result["selected_model_available"] is False


def test_qwen_rejects_invalid_models_payload() -> None:
    with local_server({"/v1/models": (200, {"models": [{"name": "qwen"}]})}) as root:
        with pytest.raises(LocalRuntimeError, match="data list"):
            check_qwen_connection(root + "/v1", "qwen")


def test_comfyui_checks_system_stats_without_submitting_workflow() -> None:
    with local_server({
        "/system_stats": (200, {"system": {"comfyui_version": "0.3.26"}, "devices": [{"name": "GPU"}]})
    }) as root:
        result = check_comfyui_connection(root)
    assert result == {"connected": True, "version": "0.3.26", "device_count": 1}


def test_comfyui_rejects_unexpected_status_payload() -> None:
    with local_server({"/system_stats": (200, {"status": "ok"})}) as root:
        with pytest.raises(LocalRuntimeError, match="unsupported structure"):
            check_comfyui_connection(root)


def test_local_runtime_does_not_follow_redirects() -> None:
    with local_server({"/v1/models": (302, {"location": "https://example.com"})}) as root:
        with pytest.raises(LocalRuntimeError, match="HTTP 302"):
            check_qwen_connection(root + "/v1", "qwen")


def test_local_runtime_bounds_response_size() -> None:
    with local_server({"/v1/models": (200, b"x" * (256 * 1024 + 1))}) as root:
        with pytest.raises(LocalRuntimeError, match="256 KB"):
            check_qwen_connection(root + "/v1", "qwen")
