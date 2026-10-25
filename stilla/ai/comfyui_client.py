"""Bounded client for explicitly local ComfyUI workflow execution."""
from __future__ import annotations

import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from stilla.ai.comfyui_config import ComfyUIConfig


class ComfyUIClientError(RuntimeError):
    """A safe, user-facing error from local ComfyUI interaction."""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req: Request, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


_CLIENT_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
_PROMPT_ID = re.compile(r"^[A-Fa-f0-9-]{8,128}$")
_MAX_WORKFLOW_BYTES = 2 * 1024 * 1024


class ComfyUIClient:
    """Submit a caller-supplied workflow and inspect its local execution history."""

    def __init__(self, config: ComfyUIConfig, *, client_id: str = "stilla-ai-studio") -> None:
        if not isinstance(config, ComfyUIConfig):
            raise TypeError("A validated ComfyUIConfig is required")
        if not isinstance(client_id, str) or not _CLIENT_ID.fullmatch(client_id):
            raise ValueError("client_id must be 1-64 safe ASCII characters")
        self._config = config
        self._client_id = client_id

    def _request_json(self, method: str, path: str, body: bytes | None = None) -> object:
        request = Request(
            f"{self._config.base_url}/{path}", data=body,
            headers={"Accept": "application/json", "Content-Type": "application/json",
                     "User-Agent": "STILLA-AI-Studio-local-client"}, method=method,
        )
        try:
            with build_opener(_NoRedirect).open(request, timeout=self._config.timeout_seconds) as response:
                if response.getcode() != 200:
                    raise ComfyUIClientError("Local ComfyUI returned a non-success status")
                length = response.headers.get("Content-Length")
                if length:
                    try:
                        if not 0 <= int(length) <= self._config.max_response_bytes:
                            raise ComfyUIClientError("Local ComfyUI response exceeds configured size limit")
                    except ValueError as exc:
                        if isinstance(exc, ComfyUIClientError):
                            raise
                        raise ComfyUIClientError("Local ComfyUI returned invalid response metadata") from exc
                payload = response.read(self._config.max_response_bytes + 1)
        except ComfyUIClientError:
            raise
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise ComfyUIClientError("Could not communicate with local ComfyUI") from exc
        if len(payload) > self._config.max_response_bytes:
            raise ComfyUIClientError("Local ComfyUI response exceeds configured size limit")
        try:
            return json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ComfyUIClientError("Local ComfyUI returned invalid JSON") from exc

    def submit_workflow(self, workflow: dict[str, object]) -> str:
        """Submit a bounded JSON workflow and return its validated prompt ID."""
        if not isinstance(workflow, dict) or not workflow:
            raise ValueError("workflow must be a non-empty object")
        try:
            encoded = json.dumps(workflow, separators=(",", ":"), allow_nan=False).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise ValueError("workflow must contain JSON-compatible values") from exc
        if len(encoded) > _MAX_WORKFLOW_BYTES:
            raise ValueError("workflow exceeds the 2 MiB limit")
        payload = json.dumps({"prompt": workflow, "client_id": self._client_id},
                             separators=(",", ":"), allow_nan=False).encode("utf-8")
        result = self._request_json("POST", "prompt", payload)
        if not isinstance(result, dict):
            raise ComfyUIClientError("Local ComfyUI returned an unsupported workflow response")
        prompt_id = result.get("prompt_id")
        if not isinstance(prompt_id, str) or not _PROMPT_ID.fullmatch(prompt_id):
            raise ComfyUIClientError("Local ComfyUI did not return a valid workflow ID")
        return prompt_id

    def get_history(self, prompt_id: str) -> dict[str, object] | None:
        """Return one workflow's history, or None if it is not available yet."""
        if not isinstance(prompt_id, str) or not _PROMPT_ID.fullmatch(prompt_id):
            raise ValueError("prompt_id is invalid")
        result = self._request_json("GET", f"history/{prompt_id}")
        if not isinstance(result, dict):
            raise ComfyUIClientError("Local ComfyUI returned an unsupported history response")
        history = result.get(prompt_id)
        if history is None:
            return None
        if not isinstance(history, dict):
            raise ComfyUIClientError("Local ComfyUI returned invalid workflow history")
        return history
