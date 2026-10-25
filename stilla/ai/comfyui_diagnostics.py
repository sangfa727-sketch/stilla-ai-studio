"""Safe, read-only diagnostics for an explicitly local ComfyUI instance."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from stilla.ai.comfyui_config import ComfyUIConfig


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req: Request, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


@dataclass(frozen=True, slots=True)
class ComfyUIDiagnostics:
    configured: bool
    reachable: bool
    system_stats_available: bool
    object_info_available: bool
    node_count: int
    message: str

    def to_dict(self) -> dict[str, object]:
        return {
            "configured": self.configured,
            "reachable": self.reachable,
            "system_stats_available": self.system_stats_available,
            "object_info_available": self.object_info_available,
            "node_count": self.node_count,
            "message": self.message,
        }


def _get_json(config: ComfyUIConfig, path: str) -> object:
    """Fetch a bounded JSON response without following redirects."""
    opener = build_opener(_NoRedirect)
    request = Request(
        f"{config.base_url}/{path}",
        headers={"Accept": "application/json", "User-Agent": "STILLA-AI-Studio-local-diagnostics"},
        method="GET",
    )
    with opener.open(request, timeout=config.timeout_seconds) as response:
        status = response.getcode()
        if status != 200:
            raise ValueError("Local ComfyUI returned a non-success status")
        content_length = response.headers.get("Content-Length")
        if content_length:
            try:
                if int(content_length) > config.max_response_bytes:
                    raise ValueError("Local ComfyUI response exceeds configured size limit")
            except ValueError as exc:
                if "size limit" in str(exc):
                    raise
        payload = response.read(config.max_response_bytes + 1)
        if len(payload) > config.max_response_bytes:
            raise ValueError("Local ComfyUI response exceeds configured size limit")
    try:
        return json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Local ComfyUI returned invalid JSON") from exc


def diagnose_comfyui(config: ComfyUIConfig) -> ComfyUIDiagnostics:
    """Check local ComfyUI and discover node types without submitting workflows."""
    if not isinstance(config, ComfyUIConfig):
        raise TypeError("A validated ComfyUIConfig is required")
    try:
        _get_json(config, "system_stats")
    except (HTTPError, URLError, TimeoutError, OSError, ValueError):
        return ComfyUIDiagnostics(
            configured=True,
            reachable=False,
            system_stats_available=False,
            object_info_available=False,
            node_count=0,
            message="Cannot verify local ComfyUI; confirm it is running on the configured port",
        )
    try:
        nodes = _get_json(config, "object_info")
    except (HTTPError, URLError, TimeoutError, OSError, ValueError):
        return ComfyUIDiagnostics(
            configured=True,
            reachable=True,
            system_stats_available=True,
            object_info_available=False,
            node_count=0,
            message="ComfyUI responds, but its node catalog could not be read",
        )
    if not isinstance(nodes, dict):
        return ComfyUIDiagnostics(
            configured=True,
            reachable=True,
            system_stats_available=True,
            object_info_available=False,
            node_count=0,
            message="ComfyUI returned an unsupported node catalog format",
        )
    return ComfyUIDiagnostics(
        configured=True,
        reachable=True,
        system_stats_available=True,
        object_info_available=True,
        node_count=len(nodes),
        message="Local ComfyUI is reachable; node catalog discovered",
    )
