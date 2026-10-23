"""Validated creative-planning data models for the offline-first Studio workflow.

These models are plain data only: they do not execute prompts, access providers, or touch files.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any

_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
MAX_TEXT = 100_000
MAX_ITEMS = 10_000


class PlanningValidationError(ValueError):
    """Raised when an untrusted planning document is invalid."""


def _text(value: object, field: str, *, limit: int = MAX_TEXT, allow_empty: bool = True) -> str:
    if not isinstance(value, str):
        raise PlanningValidationError(f"{field} must be text")
    if len(value) > limit:
        raise PlanningValidationError(f"{field} exceeds the {limit} character limit")
    if not allow_empty and not value.strip():
        raise PlanningValidationError(f"{field} must not be empty")
    return value


def _id(value: object, field: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise PlanningValidationError(f"{field} must be a 1-64 character safe identifier")
    return value


def _items(value: object, field: str, *, maximum: int = MAX_ITEMS) -> tuple:
    if not isinstance(value, (list, tuple)):
        raise PlanningValidationError(f"{field} must be an array")
    if len(value) > maximum:
        raise PlanningValidationError(f"{field} exceeds the item limit")
    return tuple(value)


def _strict_dict(value: object, field: str, allowed: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) - allowed:
        raise PlanningValidationError(f"{field} contains unsupported fields")
    return value


@dataclass(frozen=True, slots=True)
class CreativeBrief:
    """Human-approved creative intent and constraints for a planned video."""

    title: str
    audience: str
    objective: str
    language: str = "en"
    tone: str = ""
    target_duration_seconds: int = 60
    aspect_ratio: str = "16:9"
    constraints: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _text(self.title, "brief.title", limit=500, allow_empty=False)
        _text(self.audience, "brief.audience", limit=2_000, allow_empty=False)
        _text(self.objective, "brief.objective", limit=5_000, allow_empty=False)
        _text(self.language, "brief.language", limit=35, allow_empty=False)
        _text(self.tone, "brief.tone", limit=2_000)
        if isinstance(self.target_duration_seconds, bool) or not isinstance(self.target_duration_seconds, int):
            raise PlanningValidationError("brief.target_duration_seconds must be an integer")
        if not 1 <= self.target_duration_seconds <= 86_400:
            raise PlanningValidationError("brief.target_duration_seconds must be between 1 and 86400")
        if not isinstance(self.aspect_ratio, str) or self.aspect_ratio not in {"16:9", "9:16", "1:1", "4:3", "3:2", "custom"}:
            raise PlanningValidationError("brief.aspect_ratio is unsupported")
        constraints = _items(self.constraints, "brief.constraints", maximum=100)
        for item in constraints:
            _text(item, "brief constraint", limit=2_000, allow_empty=False)
        object.__setattr__(self, "constraints", constraints)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title, "audience": self.audience, "objective": self.objective,
            "language": self.language, "tone": self.tone,
            "target_duration_seconds": self.target_duration_seconds,
            "aspect_ratio": self.aspect_ratio, "constraints": list(self.constraints),
        }

    @classmethod
    def from_dict(cls, data: object) -> "CreativeBrief":
        obj = _strict_dict(data, "brief", {
            "title", "audience", "objective", "language", "tone",
            "target_duration_seconds", "aspect_ratio", "constraints",
        })
        return cls(**obj)


@dataclass(frozen=True, slots=True)
class ScriptSegment:
    id: str
    text: str
    narration: str = ""
    estimated_duration_seconds: float = 5.0

    def __post_init__(self) -> None:
        _id(self.id, "script_segment.id")
        _text(self.text, "script_segment.text", allow_empty=False)
        _text(self.narration, "script_segment.narration")
        duration = self.estimated_duration_seconds
        if isinstance(duration, bool) or not isinstance(duration, (int, float)):
            raise PlanningValidationError("script segment duration must be a number")
        if not math.isfinite(duration) or not 0 < duration <= 86_400:
            raise PlanningValidationError("script segment duration must be between 0 and 86400")

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "text": self.text, "narration": self.narration,
                "estimated_duration_seconds": self.estimated_duration_seconds}


@dataclass(frozen=True, slots=True)
class ScriptDocument:
    id: str
    title: str
    language: str
    segments: tuple[ScriptSegment, ...] = ()

    def __post_init__(self) -> None:
        _id(self.id, "script.id")
        _text(self.title, "script.title", limit=500, allow_empty=False)
        _text(self.language, "script.language", limit=35, allow_empty=False)
        segments = _items(self.segments, "script.segments")
        if any(not isinstance(item, ScriptSegment) for item in segments):
            raise PlanningValidationError("script.segments must contain ScriptSegment objects")
        ids = [item.id for item in segments]
        if len(ids) != len(set(ids)):
            raise PlanningValidationError("script segment IDs must be unique")
        object.__setattr__(self, "segments", segments)

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "title": self.title, "language": self.language,
                "segments": [segment.to_dict() for segment in self.segments]}

    @classmethod
    def from_dict(cls, data: object) -> "ScriptDocument":
        obj = _strict_dict(data, "script", {"id", "title", "language", "segments"})
        raw = _items(obj.get("segments", []), "script.segments")
        parsed = []
        for item in raw:
            parsed.append(ScriptSegment(**_strict_dict(
                item, "script segment",
                {"id", "text", "narration", "estimated_duration_seconds"},
            )))
        return cls(id=obj.get("id"), title=obj.get("title"), language=obj.get("language"),
                   segments=tuple(parsed))


@dataclass(frozen=True, slots=True)
class StoryboardFrame:
    id: str
    script_segment_id: str
    visual_description: str
    on_screen_text: str = ""
    asset_prompt: str = ""

    def __post_init__(self) -> None:
        _id(self.id, "storyboard_frame.id")
        _id(self.script_segment_id, "storyboard_frame.script_segment_id")
        _text(self.visual_description, "storyboard_frame.visual_description", allow_empty=False)
        _text(self.on_screen_text, "storyboard_frame.on_screen_text", limit=10_000)
        _text(self.asset_prompt, "storyboard_frame.asset_prompt", limit=10_000)

    def to_dict(self) -> dict[str, str]:
        return {"id": self.id, "script_segment_id": self.script_segment_id,
                "visual_description": self.visual_description,
                "on_screen_text": self.on_screen_text, "asset_prompt": self.asset_prompt}


@dataclass(frozen=True, slots=True)
class StoryboardDocument:
    id: str
    title: str
    frames: tuple[StoryboardFrame, ...] = ()

    def __post_init__(self) -> None:
        _id(self.id, "storyboard.id")
        _text(self.title, "storyboard.title", limit=500, allow_empty=False)
        frames = _items(self.frames, "storyboard.frames")
        if any(not isinstance(item, StoryboardFrame) for item in frames):
            raise PlanningValidationError("storyboard.frames must contain StoryboardFrame objects")
        ids = [item.id for item in frames]
        if len(ids) != len(set(ids)):
            raise PlanningValidationError("storyboard frame IDs must be unique")
        object.__setattr__(self, "frames", frames)

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "title": self.title, "frames": [frame.to_dict() for frame in self.frames]}

    @classmethod
    def from_dict(cls, data: object) -> "StoryboardDocument":
        obj = _strict_dict(data, "storyboard", {"id", "title", "frames"})
        raw = _items(obj.get("frames", []), "storyboard.frames")
        frames = []
        for item in raw:
            frames.append(StoryboardFrame(**_strict_dict(
                item, "storyboard frame",
                {"id", "script_segment_id", "visual_description", "on_screen_text", "asset_prompt"},
            )))
        return cls(id=obj.get("id"), title=obj.get("title"), frames=tuple(frames))


@dataclass(frozen=True, slots=True)
class Shot:
    id: str
    storyboard_frame_id: str
    description: str
    duration_seconds: float = 5.0
    camera: str = ""
    generation_prompt: str = ""

    def __post_init__(self) -> None:
        _id(self.id, "shot.id")
        _id(self.storyboard_frame_id, "shot.storyboard_frame_id")
        _text(self.description, "shot.description", limit=10_000, allow_empty=False)
        _text(self.camera, "shot.camera", limit=1_000)
        _text(self.generation_prompt, "shot.generation_prompt", limit=10_000)
        duration = self.duration_seconds
        if isinstance(duration, bool) or not isinstance(duration, (int, float)):
            raise PlanningValidationError("shot.duration_seconds must be a number")
        if not 0 < duration <= 86_400:
            raise PlanningValidationError("shot.duration_seconds must be between 0 and 86400")

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "storyboard_frame_id": self.storyboard_frame_id,
                "description": self.description, "duration_seconds": self.duration_seconds,
                "camera": self.camera, "generation_prompt": self.generation_prompt}


@dataclass(frozen=True, slots=True)
class ShotPlan:
    id: str
    title: str
    shots: tuple[Shot, ...] = ()

    def __post_init__(self) -> None:
        _id(self.id, "shot_plan.id")
        _text(self.title, "shot_plan.title", limit=500, allow_empty=False)
        shots = _items(self.shots, "shot_plan.shots")
        if any(not isinstance(item, Shot) for item in shots):
            raise PlanningValidationError("shot_plan.shots must contain Shot objects")
        ids = [item.id for item in shots]
        if len(ids) != len(set(ids)):
            raise PlanningValidationError("shot IDs must be unique")
        object.__setattr__(self, "shots", shots)

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "title": self.title, "shots": [shot.to_dict() for shot in self.shots]}

    @classmethod
    def from_dict(cls, data: object) -> "ShotPlan":
        obj = _strict_dict(data, "shot_plan", {"id", "title", "shots"})
        raw = _items(obj.get("shots", []), "shot_plan.shots")
        shots = []
        for item in raw:
            shots.append(Shot(**_strict_dict(
                item, "shot",
                {"id", "storyboard_frame_id", "description", "duration_seconds", "camera", "generation_prompt"},
            )))
        return cls(id=obj.get("id"), title=obj.get("title"), shots=tuple(shots))
