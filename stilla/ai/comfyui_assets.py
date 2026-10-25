"""Retrieve generated images from local ComfyUI and safely persist them in a project."""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener
from typing import Any

from stilla.ai.comfyui_config import ComfyUIConfig
from stilla.media.workspace import ProjectWorkspace, WorkspaceError

_ASSET_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_FILENAME = re.compile(r"^[^/\\\\\x00]{1,255}$")
_SUBFOLDER = re.compile(r"^[A-Za-z0-9_. -]{1,128}(?:/[A-Za-z0-9_. -]{1,128})*$")
_ALLOWED_TYPES = {
    "image/png": (".png", b"\x89PNG\r\n\x1a\n"),
    "image/jpeg": (".jpg", b"\xff\xd8\xff"),
    "image/webp": (".webp", b"RIFF"),
}


class ComfyUIAssetError(RuntimeError):
    """A safe error while retrieving or saving a generated local image."""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req: Request, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


class ComfyUIAssetStore:
    """Download one ComfyUI output image into a validated project's assets directory."""

    def __init__(
        self,
        config: ComfyUIConfig,
        workspace: ProjectWorkspace,
        *,
        max_asset_bytes: int | None = None,
    ) -> None:
        if not isinstance(config, ComfyUIConfig):
            raise TypeError("A validated ComfyUIConfig is required")
        if not isinstance(workspace, ProjectWorkspace):
            raise TypeError("A ProjectWorkspace is required")
        if max_asset_bytes is None:
            max_asset_bytes = min(10_485_760, config.max_response_bytes)
        if (
            isinstance(max_asset_bytes, bool)
            or not isinstance(max_asset_bytes, int)
            or not 1 <= max_asset_bytes <= config.max_response_bytes
        ):
            raise ValueError("max_asset_bytes must be within the configured response limit")
        self._config = config
        self._workspace = workspace
        self._max_asset_bytes = max_asset_bytes

    @staticmethod
    def _validate_reference(image: object) -> dict[str, str]:
        if not isinstance(image, dict):
            raise TypeError("image reference must be an object")
        filename = image.get("filename")
        subfolder = image.get("subfolder", "")
        image_type = image.get("type", "output")
        if not isinstance(filename, str) or not _FILENAME.fullmatch(filename) or filename in {".", ".."}:
            raise ValueError("image filename is invalid")
        if not isinstance(subfolder, str) or (subfolder and not _SUBFOLDER.fullmatch(subfolder)):
            raise ValueError("image subfolder is invalid")
        if subfolder and any(part in {"", ".", ".."} for part in subfolder.split("/")):
            raise ValueError("image subfolder contains an unsafe path segment")
        if image_type not in {"output", "temp", "input"}:
            raise ValueError("image type is invalid")
        return {"filename": filename, "subfolder": subfolder, "type": image_type}

    def save_image(self, project_id: str, asset_id: str, image: object) -> Path:
        """Fetch a history image reference and save verified image bytes without overwriting."""
        if not isinstance(asset_id, str) or not _ASSET_ID.fullmatch(asset_id):
            raise ValueError("asset_id must be a safe identifier")
        reference = self._validate_reference(image)
        project = self._workspace.root / "projects" / project_id
        try:
            metadata = self._workspace.load_project(project_id)
            del metadata
        except WorkspaceError as exc:
            raise ComfyUIAssetError("Project does not exist or is unsafe") from exc
        if project.is_symlink() or not project.is_dir() or not project.resolve().is_relative_to(self._workspace.root.resolve() / "projects"):
            raise ComfyUIAssetError("Project path is unsafe")
        query = urlencode(reference)
        request = Request(
            f"{self._config.base_url}/view?{query}",
            headers={"Accept": "image/png, image/jpeg, image/webp", "User-Agent": "STILLA-AI-Studio-local-client"},
            method="GET",
        )
        try:
            with build_opener(_NoRedirect).open(request, timeout=self._config.timeout_seconds) as response:
                if response.getcode() != 200:
                    raise ComfyUIAssetError("Local ComfyUI returned a non-success image response")
                length = response.headers.get("Content-Length")
                if length is not None:
                    try:
                        parsed_length = int(length)
                    except (TypeError, ValueError) as exc:
                        raise ComfyUIAssetError("Local ComfyUI returned invalid image metadata") from exc
                    if not 0 <= parsed_length <= self._max_asset_bytes:
                        raise ComfyUIAssetError("Generated image exceeds the configured size limit")
                payload = response.read(self._max_asset_bytes + 1)
                content_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        except ComfyUIAssetError:
            raise
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise ComfyUIAssetError("Could not retrieve image from local ComfyUI") from exc
        if len(payload) > self._max_asset_bytes:
            raise ComfyUIAssetError("Generated image exceeds the configured size limit")
        image_spec = _ALLOWED_TYPES.get(content_type)
        if image_spec is None or not payload.startswith(image_spec[1]):
            raise ComfyUIAssetError("Local ComfyUI returned an unsupported or invalid image")
        if content_type == "image/webp" and (len(payload) < 12 or payload[8:12] != b"WEBP"):
            raise ComfyUIAssetError("Local ComfyUI returned an invalid WebP image")

        assets = project / "assets"
        if assets.is_symlink():
            raise ComfyUIAssetError("Project assets directory is unsafe")
        assets.mkdir(exist_ok=True)
        if not assets.is_dir() or not assets.resolve().is_relative_to(project.resolve()):
            raise ComfyUIAssetError("Project assets directory is unsafe")
        destination = assets / f"{asset_id}{image_spec[0]}"
        if destination.exists() or destination.is_symlink():
            raise ComfyUIAssetError("Asset already exists; refusing to overwrite")
        fd, temp_name = tempfile.mkstemp(prefix=".stilla-image-", suffix=".tmp", dir=assets)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            if destination.exists() or destination.is_symlink():
                raise ComfyUIAssetError("Asset already exists; refusing to overwrite")
            os.replace(temp_name, destination)
        finally:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass
        return destination
