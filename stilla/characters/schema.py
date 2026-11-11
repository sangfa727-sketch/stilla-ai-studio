"""Validated, provider-neutral character identity records.

A profile stores creative identity and generation references. It does not claim that
diffusion models can guarantee pixel-identical characters across arbitrary scenes.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any

_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
MAX_TEXT = 8_000
MAX_ITEMS = 40


class CharacterProfileError(ValueError):
    """Raised when a character profile contains invalid or unsafe data."""


def _text(value: object, field: str, limit: int = MAX_TEXT, *, required: bool = False) -> str:
    if not isinstance(value, str) or len(value) > limit or (required and not value.strip()):
        raise CharacterProfileError(f"{field} must be text within the supported limit")
    return value


def _id(value: object, field: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise CharacterProfileError(f"{field} must be a safe 1-64 character identifier")
    return value


def _strings(value: object, field: str, *, maximum: int = MAX_ITEMS) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)) or len(value) > maximum:
        raise CharacterProfileError(f"{field} must be an array within the item limit")
    result = tuple(_text(item, field, 500, required=True) for item in value)
    if len(result) != len(set(result)):
        raise CharacterProfileError(f"{field} must not contain duplicates")
    return result


def _strict(data: object, field: str, allowed: set[str]) -> dict[str, Any]:
    if not isinstance(data, dict) or set(data) - allowed:
        raise CharacterProfileError(f"{field} contains unsupported fields")
    return data


@dataclass(frozen=True, slots=True)
class VisualIdentity:
    """Stable visual anchors. Scene pose and expression are intentionally separate."""

    silhouette: str
    body_proportions: str
    face_shape: str
    eyes: str
    nose: str = ""
    mouth: str = ""
    primary_colors: tuple[str, ...] = ()
    surface_or_skin_detail: str = ""
    hairstyle_or_head_shape: str = ""
    outfit: str = ""
    accessories: tuple[str, ...] = ()
    distinguishing_marks: tuple[str, ...] = ()
    art_style: str = "original stylized 3D cartoon"
    fixed_features: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field in ("silhouette", "body_proportions", "face_shape", "eyes"):
            _text(getattr(self, field), f"visual.{field}", required=True)
        for field in ("nose", "mouth", "surface_or_skin_detail", "hairstyle_or_head_shape",
                      "outfit", "art_style"):
            _text(getattr(self, field), f"visual.{field}", required=(field == "art_style"))
        for field in ("primary_colors", "accessories", "distinguishing_marks", "fixed_features"):
            object.__setattr__(self, field, _strings(getattr(self, field), f"visual.{field}"))

    def to_dict(self) -> dict[str, Any]:
        return {field: (list(value) if isinstance(value, tuple) else value)
                for field, value in ((name, getattr(self, name)) for name in self.__dataclass_fields__)}

    @classmethod
    def from_dict(cls, data: object) -> "VisualIdentity":
        allowed = set(cls.__dataclass_fields__)
        obj = _strict(data, "visual_identity", allowed)
        return cls(**obj)


@dataclass(frozen=True, slots=True)
class ComedyPersonality:
    """Original behavior design; it must not imitate a named copyrighted character."""

    archetype: str = "lovable mischief-maker"
    core_traits: tuple[str, ...] = ()
    strength: str = ""
    comic_flaw: str = ""
    humor_mechanics: tuple[str, ...] = ()
    speech_pattern: str = ""
    catchphrase: str = ""
    reaction_style: str = ""
    relationship_dynamic: str = ""
    running_gag: str = ""
    avoid: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field in ("archetype", "strength", "comic_flaw", "speech_pattern",
                      "catchphrase", "reaction_style", "relationship_dynamic", "running_gag"):
            _text(getattr(self, field), f"personality.{field}")
        for field in ("core_traits", "humor_mechanics", "avoid"):
            object.__setattr__(self, field, _strings(getattr(self, field), f"personality.{field}"))

    def to_dict(self) -> dict[str, Any]:
        return {name: (list(getattr(self, name)) if isinstance(getattr(self, name), tuple)
                       else getattr(self, name)) for name in self.__dataclass_fields__}

    @classmethod
    def from_dict(cls, data: object) -> "ComedyPersonality":
        return cls(**_strict(data, "comedy_personality", set(cls.__dataclass_fields__)))


@dataclass(frozen=True, slots=True)
class CharacterReference:
    """Project-relative reference image with optional content checksum."""

    asset_id: str
    relative_path: str
    role: str = "master"
    sha256: str = ""

    def __post_init__(self) -> None:
        _id(self.asset_id, "reference.asset_id")
        path = _text(self.relative_path, "reference.relative_path", 2048, required=True)
        normalized = path.replace("\\", "/")
        if normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized):
            raise CharacterProfileError("reference path must be project-relative")
        if any(part in {"", ".", ".."} for part in normalized.split("/")):
            raise CharacterProfileError("reference path contains an unsafe segment")
        _text(self.role, "reference.role", 100, required=True)
        if self.sha256 and not _SHA256.fullmatch(self.sha256):
            raise CharacterProfileError("reference.sha256 must be a lowercase SHA-256 digest")

    def to_dict(self) -> dict[str, str]:
        return {"asset_id": self.asset_id, "relative_path": self.relative_path,
                "role": self.role, "sha256": self.sha256}

    @classmethod
    def from_dict(cls, data: object) -> "CharacterReference":
        return cls(**_strict(data, "character_reference",
                             {"asset_id", "relative_path", "role", "sha256"}))


@dataclass(frozen=True, slots=True)
class CharacterProfile:
    """A versioned original character that can be reused across stories and projects."""

    id: str
    name: str
    species_or_type: str
    visual: VisualIdentity
    personality: ComedyPersonality = ComedyPersonality()
    references: tuple[CharacterReference, ...] = ()
    voice_description: str = ""
    language: str = "en"
    schema_version: int = 1

    def __post_init__(self) -> None:
        _id(self.id, "character.id")
        _text(self.name, "character.name", 200, required=True)
        _text(self.species_or_type, "character.species_or_type", 300, required=True)
        _text(self.voice_description, "character.voice_description", 2_000)
        _text(self.language, "character.language", 35, required=True)
        if self.schema_version != 1 or isinstance(self.schema_version, bool):
            raise CharacterProfileError("unsupported character schema version")
        if not isinstance(self.visual, VisualIdentity) or not isinstance(self.personality, ComedyPersonality):
            raise CharacterProfileError("visual and personality must be validated profile objects")
        refs = tuple(self.references)
        if len(refs) > 20 or any(not isinstance(ref, CharacterReference) for ref in refs):
            raise CharacterProfileError("references must contain at most 20 validated records")
        ids = [ref.asset_id for ref in refs]
        if len(ids) != len(set(ids)):
            raise CharacterProfileError("character reference asset IDs must be unique")
        object.__setattr__(self, "references", refs)

    def identity_payload(self) -> dict[str, Any]:
        """Only immutable visual identity participates in the consistency fingerprint."""
        return {
            "name": self.name,
            "species_or_type": self.species_or_type,
            "visual": self.visual.to_dict(),
            "references": [ref.to_dict() for ref in self.references],
        }

    @property
    def identity_fingerprint(self) -> str:
        encoded = json.dumps(self.identity_payload(), ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version, "id": self.id, "name": self.name,
            "species_or_type": self.species_or_type, "visual": self.visual.to_dict(),
            "personality": self.personality.to_dict(),
            "references": [ref.to_dict() for ref in self.references],
            "voice_description": self.voice_description, "language": self.language,
        }

    @classmethod
    def from_dict(cls, data: object) -> "CharacterProfile":
        allowed = {"schema_version", "id", "name", "species_or_type", "visual",
                   "personality", "references", "voice_description", "language"}
        obj = _strict(data, "character_profile", allowed)
        raw_refs = obj.get("references", [])
        if not isinstance(raw_refs, list) or len(raw_refs) > 20:
            raise CharacterProfileError("character references must be a bounded array")
        refs = tuple(CharacterReference.from_dict(item) for item in raw_refs)
        return cls(
            id=obj.get("id"), name=obj.get("name"), species_or_type=obj.get("species_or_type"),
            visual=VisualIdentity.from_dict(obj.get("visual")),
            personality=ComedyPersonality.from_dict(obj.get("personality", {})),
            references=refs, voice_description=obj.get("voice_description", ""),
            language=obj.get("language", "en"), schema_version=obj.get("schema_version", 1),
        )
