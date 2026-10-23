"""Versioned, JSON-safe project document schema for STILLA."""

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any



CURRENT_SCHEMA_VERSION = 1
_MAX_SCENES = 10_000
_MAX_ASSETS = 50_000
_MAX_TEXT = 100_000
_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")


class ProjectValidationError(ValueError):
    """Raised when a project document violates the supported schema."""


def _require_id(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not _ID_PATTERN.fullmatch(value):
        raise ProjectValidationError(f"{field_name} must be a 1-64 character safe identifier")
    return value


def _require_text(value: object, field_name: str, *, max_length: int = _MAX_TEXT) -> str:
    if not isinstance(value, str):
        raise ProjectValidationError(f"{field_name} must be text")
    if len(value) > max_length:
        raise ProjectValidationError(f"{field_name} exceeds the {max_length} character limit")
    return value


@dataclass(frozen=True, slots=True)
class Scene:
    id: str
    title: str
    description: str = ""
    duration_seconds: float = 5.0

    def __post_init__(self) -> None:
        _require_id(self.id, "scene.id")
        _require_text(self.title, "scene.title", max_length=500)
        _require_text(self.description, "scene.description")
        if isinstance(self.duration_seconds, bool) or not isinstance(
            self.duration_seconds, (int, float)
        ):
            raise ProjectValidationError("scene.duration_seconds must be a number")
        if not 0 < self.duration_seconds <= 86_400:
            raise ProjectValidationError("scene.duration_seconds must be between 0 and 86400")


@dataclass(frozen=True, slots=True)
class AssetReference:
    id: str
    relative_path: str
    media_type: str

    def __post_init__(self) -> None:
        _require_id(self.id, "asset.id")
        _require_text(self.relative_path, "asset.relative_path", max_length=2_048)
        _require_text(self.media_type, "asset.media_type", max_length=100)
        # Paths are references only. Reject traversal and absolute paths at the schema boundary.
        normalized = self.relative_path.replace("\\", "/")
        if normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized):
            raise ProjectValidationError("asset.relative_path must be project-relative")
        if any(part == ".." for part in normalized.split("/")):
            raise ProjectValidationError("asset.relative_path must not traverse parent directories")


@dataclass(frozen=True, slots=True)
class ProjectDocument:
    id: str
    name: str
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    schema_version: int = CURRENT_SCHEMA_VERSION
    scenes: tuple[Scene, ...] = ()
    assets: tuple[AssetReference, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_id(self.id, "project.id")
        _require_text(self.name, "project.name", max_length=500)
        if isinstance(self.schema_version, bool) or not isinstance(self.schema_version, int):
            raise ProjectValidationError("schema_version must be an integer")
        if self.schema_version != CURRENT_SCHEMA_VERSION:
            raise ProjectValidationError("unsupported project schema version")
        if len(self.scenes) > _MAX_SCENES:
            raise ProjectValidationError("project exceeds the scene limit")
        if len(self.assets) > _MAX_ASSETS:
            raise ProjectValidationError("project exceeds the asset limit")
        scene_ids = [scene.id for scene in self.scenes]
        asset_ids = [asset.id for asset in self.assets]
        if len(scene_ids) != len(set(scene_ids)):
            raise ProjectValidationError("scene IDs must be unique")
        if len(asset_ids) != len(set(asset_ids)):
            raise ProjectValidationError("asset IDs must be unique")
        for value, field_name in ((self.created_at, "created_at"), (self.updated_at, "updated_at")):
            if not isinstance(value, str) or len(value) > 100:
                raise ProjectValidationError(f"{field_name} must be an ISO timestamp string")
            try:
                datetime.fromisoformat(value)
            except ValueError as exc:
                raise ProjectValidationError(f"{field_name} must be an ISO timestamp string") from exc
        if not isinstance(self.metadata, dict):
            raise ProjectValidationError("project.metadata must be an object")
        if len(self.metadata) > 100:
            raise ProjectValidationError("project.metadata has too many top-level entries")

    def to_dict(self) -> dict[str, Any]:
        """Return a plain JSON-compatible document; never executes embedded content."""
        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "scenes": [
                {
                    "id": scene.id,
                    "title": scene.title,
                    "description": scene.description,
                    "duration_seconds": scene.duration_seconds,
                }
                for scene in self.scenes
            ],
            "assets": [
                {
                    "id": asset.id,
                    "relative_path": asset.relative_path,
                    "media_type": asset.media_type,
                }
                for asset in self.assets
            ],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: object) -> "ProjectDocument":  # noqa: UP037
        """Validate an untrusted JSON-like object and reject unknown top-level keys."""
        if not isinstance(data, dict):
            raise ProjectValidationError("project document must be an object")
        allowed = {
            "schema_version", "id", "name", "created_at", "updated_at",
            "scenes", "assets", "metadata",
        }
        if set(data) - allowed:
            raise ProjectValidationError("project document contains unsupported top-level fields")
        if isinstance(data.get("schema_version"), bool) or not isinstance(data.get("schema_version"), int):
            raise ProjectValidationError("schema_version must be an integer")
        if data.get("schema_version") != CURRENT_SCHEMA_VERSION:
            raise ProjectValidationError("unsupported project schema version")
        scenes_raw = data.get("scenes", [])
        assets_raw = data.get("assets", [])
        if not isinstance(scenes_raw, list) or not isinstance(assets_raw, list):
            raise ProjectValidationError("scenes and assets must be arrays")
        if len(scenes_raw) > _MAX_SCENES or len(assets_raw) > _MAX_ASSETS:
            raise ProjectValidationError("project exceeds the supported item limit")
        scenes = []
        for item in scenes_raw:
            if not isinstance(item, dict) or set(item) - {
                "id", "title", "description", "duration_seconds"
            }:
                raise ProjectValidationError("invalid scene object")
            scenes.append(Scene(**item))
        assets = []
        for item in assets_raw:
            if not isinstance(item, dict) or set(item) - {"id", "relative_path", "media_type"}:
                raise ProjectValidationError("invalid asset object")
            assets.append(AssetReference(**item))
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            schema_version=data.get("schema_version"),
            scenes=tuple(scenes),
            assets=tuple(assets),
            metadata=data.get("metadata", {}),
        )
