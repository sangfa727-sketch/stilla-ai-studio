"""Versioned character snapshots and fail-closed storyboard shot bindings.

This is a domain contract only. It does not write files, call a provider, or mutate
the existing desktop browser prototype.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from stilla.characters.consistency import CharacterGenerationPlan, build_generation_plan
from stilla.characters.schema import CharacterProfile, CharacterProfileError
from stilla.planning.schema import ShotPlan, PlanningValidationError

_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_MAX_REVISIONS = 500
_MAX_BINDINGS = 10_000


class StoryboardBindingError(ValueError):
    """Raised when a storyboard character binding is incomplete or inconsistent."""


@dataclass(frozen=True, slots=True)
class CharacterRevisionSnapshot:
    """Immutable profile snapshot embedded in a storyboard document."""

    revision: int
    profile: CharacterProfile

    def __post_init__(self) -> None:
        if isinstance(self.revision, bool) or not isinstance(self.revision, int) or self.revision < 1:
            raise StoryboardBindingError("character revision must be a positive integer")
        if not isinstance(self.profile, CharacterProfile):
            raise StoryboardBindingError("revision snapshot requires a validated character profile")

    @property
    def identity_fingerprint(self) -> str:
        return self.profile.identity_fingerprint

    def to_dict(self) -> dict[str, Any]:
        return {"revision": self.revision, "profile": self.profile.to_dict()}

    @classmethod
    def from_dict(cls, data: object) -> CharacterRevisionSnapshot:
        if not isinstance(data, dict) or set(data) != {"revision", "profile"}:
            raise StoryboardBindingError("invalid character revision snapshot")
        try:
            return cls(revision=data["revision"], profile=CharacterProfile.from_dict(data["profile"]))
        except (CharacterProfileError, TypeError, KeyError) as exc:
            raise StoryboardBindingError("character revision snapshot failed validation") from exc


@dataclass(frozen=True, slots=True)
class ShotCharacterBinding:
    """Pins one shot to one exact character profile revision and identity fingerprint."""

    shot_id: str
    character_id: str
    profile_revision: int
    identity_fingerprint: str

    def __post_init__(self) -> None:
        for value, field in ((self.shot_id, "shot_id"), (self.character_id, "character_id")):
            if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value):
                raise StoryboardBindingError(f"{field} must be a safe 1-64 character identifier")
        if (isinstance(self.profile_revision, bool) or not isinstance(self.profile_revision, int)
                or self.profile_revision < 1):
            raise StoryboardBindingError("profile_revision must be a positive integer")
        if not isinstance(self.identity_fingerprint, str) or not _SHA256.fullmatch(self.identity_fingerprint):
            raise StoryboardBindingError("identity_fingerprint must be a lowercase SHA-256 digest")

    def to_dict(self) -> dict[str, Any]:
        return {
            "shot_id": self.shot_id,
            "character_id": self.character_id,
            "profile_revision": self.profile_revision,
            "identity_fingerprint": self.identity_fingerprint,
        }

    @classmethod
    def from_dict(cls, data: object) -> ShotCharacterBinding:
        if not isinstance(data, dict) or set(data) != {
            "shot_id", "character_id", "profile_revision", "identity_fingerprint"
        }:
            raise StoryboardBindingError("invalid shot character binding")
        try:
            return cls(**data)
        except TypeError as exc:
            raise StoryboardBindingError("shot character binding failed validation") from exc


@dataclass(frozen=True, slots=True)
class CharacterBoundShotPlan:
    """A shot plan plus immutable character snapshots and explicit per-shot bindings."""

    shot_plan: ShotPlan
    character_revisions: tuple[CharacterRevisionSnapshot, ...] = ()
    bindings: tuple[ShotCharacterBinding, ...] = ()
    schema_version: int = 1

    def __post_init__(self) -> None:
        if isinstance(self.schema_version, bool) or not isinstance(self.schema_version, int) or self.schema_version != 1:
            raise StoryboardBindingError("unsupported storyboard binding schema version")
        if not isinstance(self.shot_plan, ShotPlan):
            raise StoryboardBindingError("shot_plan must be a validated ShotPlan")
        revisions = tuple(self.character_revisions)
        bindings = tuple(self.bindings)
        if len(revisions) > _MAX_REVISIONS or any(
            not isinstance(item, CharacterRevisionSnapshot) for item in revisions
        ):
            raise StoryboardBindingError("character revision snapshots exceed the supported limit")
        if len(bindings) > _MAX_BINDINGS or any(
            not isinstance(item, ShotCharacterBinding) for item in bindings
        ):
            raise StoryboardBindingError("shot bindings exceed the supported limit")
        revision_keys = [(item.profile.id, item.revision) for item in revisions]
        if len(revision_keys) != len(set(revision_keys)):
            raise StoryboardBindingError("character revision snapshots must be unique")
        shot_ids = {shot.id for shot in self.shot_plan.shots}
        binding_keys = [(item.shot_id, item.character_id) for item in bindings]
        if len(binding_keys) != len(set(binding_keys)):
            raise StoryboardBindingError("a character may only be bound once per shot")
        revisions_by_key = {(item.profile.id, item.revision): item for item in revisions}
        for binding in bindings:
            if binding.shot_id not in shot_ids:
                raise StoryboardBindingError("binding references a shot that does not exist")
            snapshot = revisions_by_key.get((binding.character_id, binding.profile_revision))
            if snapshot is None:
                raise StoryboardBindingError("binding references a missing character revision snapshot")
            if snapshot.identity_fingerprint != binding.identity_fingerprint:
                raise StoryboardBindingError("binding fingerprint does not match its revision snapshot")
        object.__setattr__(self, "character_revisions", revisions)
        object.__setattr__(self, "bindings", bindings)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "shot_plan": self.shot_plan.to_dict(),
            "character_revisions": [item.to_dict() for item in self.character_revisions],
            "bindings": [item.to_dict() for item in self.bindings],
        }

    @classmethod
    def from_dict(cls, data: object) -> CharacterBoundShotPlan:
        if not isinstance(data, dict) or set(data) != {
            "schema_version", "shot_plan", "character_revisions", "bindings"
        }:
            raise StoryboardBindingError("invalid character-bound shot plan document")
        revisions_raw = data["character_revisions"]
        bindings_raw = data["bindings"]
        if not isinstance(revisions_raw, list) or not isinstance(bindings_raw, list):
            raise StoryboardBindingError("character revisions and bindings must be arrays")
        if len(revisions_raw) > _MAX_REVISIONS or len(bindings_raw) > _MAX_BINDINGS:
            raise StoryboardBindingError("storyboard binding document exceeds the item limit")
        try:
            return cls(
                shot_plan=ShotPlan.from_dict(data["shot_plan"]),
                character_revisions=tuple(CharacterRevisionSnapshot.from_dict(item) for item in revisions_raw),
                bindings=tuple(ShotCharacterBinding.from_dict(item) for item in bindings_raw),
                schema_version=data["schema_version"],
            )
        except (PlanningValidationError, TypeError, KeyError) as exc:
            raise StoryboardBindingError("storyboard binding document failed validation") from exc

    def compile_shot(self, shot_id: str) -> tuple[CharacterGenerationPlan, ...]:
        """Compile only profiles pinned to this shot; missing/stale snapshots fail closed."""
        shot = next((item for item in self.shot_plan.shots if item.id == shot_id), None)
        if shot is None:
            raise StoryboardBindingError("requested shot does not exist")
        revisions = {
            (item.profile.id, item.revision): item for item in self.character_revisions
        }
        plans = []
        for binding in self.bindings:
            if binding.shot_id != shot_id:
                continue
            snapshot = revisions.get((binding.character_id, binding.profile_revision))
            if snapshot is None or snapshot.identity_fingerprint != binding.identity_fingerprint:
                raise StoryboardBindingError("character revision is missing or has changed")
            try:
                plans.append(build_generation_plan(snapshot.profile, shot.description))
            except CharacterProfileError as exc:
                raise StoryboardBindingError("character generation plan could not be compiled") from exc
        return tuple(plans)


def bind_character_to_shots(
    document: CharacterBoundShotPlan,
    character: CharacterProfile,
    *,
    revision: int,
    shot_ids: tuple[str, ...] | list[str] | None = None,
) -> CharacterBoundShotPlan:
    """Return a new document with an exact profile snapshot bound to selected shots.

    If shot_ids is omitted, the character is bound to every shot. Existing bindings
    for the same character on selected shots are replaced; other characters remain.
    """
    if not isinstance(document, CharacterBoundShotPlan):
        raise TypeError("document must be a CharacterBoundShotPlan")
    snapshot = CharacterRevisionSnapshot(revision=revision, profile=character)
    available = {shot.id for shot in document.shot_plan.shots}
    selected = tuple(shot.id for shot in document.shot_plan.shots) if shot_ids is None else tuple(shot_ids)
    if (
        not selected
        or any(not isinstance(item, str) for item in selected)
        or len(selected) != len(set(selected))
        or any(item not in available for item in selected)
    ):
        raise StoryboardBindingError("selected shot IDs must be unique existing shots")
    revisions = {
        (item.profile.id, item.revision): item for item in document.character_revisions
    }
    key = (character.id, revision)
    existing_snapshot = revisions.get(key)
    if existing_snapshot is not None and existing_snapshot.identity_fingerprint != snapshot.identity_fingerprint:
        raise StoryboardBindingError("a character revision cannot be overwritten with different identity data")
    revisions[key] = snapshot
    selected_set = set(selected)
    bindings = [
        item for item in document.bindings
        if not (item.character_id == character.id and item.shot_id in selected_set)
    ]
    bindings.extend(
        ShotCharacterBinding(
            shot_id=shot_id,
            character_id=character.id,
            profile_revision=revision,
            identity_fingerprint=snapshot.identity_fingerprint,
        )
        for shot_id in selected
    )
    return CharacterBoundShotPlan(
        shot_plan=document.shot_plan,
        character_revisions=tuple(revisions.values()),
        bindings=tuple(bindings),
    )
