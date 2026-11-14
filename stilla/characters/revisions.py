"""Append-only, project-local character revision history."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from stilla.characters.schema import CharacterProfile, CharacterProfileError
from stilla.media.workspace import WorkspaceError, atomic_write_bytes

_CHARACTER_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_MAX_LEDGER_BYTES = 20 * 1024 * 1024
_MAX_REVISIONS = 100


class CharacterRevisionError(RuntimeError):
    """A character revision ledger is invalid or cannot be safely updated."""


def _now() -> str:
    return datetime.now(UTC).isoformat()


def profile_digest(profile: CharacterProfile) -> str:
    encoded = json.dumps(
        profile.to_dict(), ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _ledger_path(directory: str | Path, character_id: str, *, create: bool) -> Path | None:
    if not isinstance(character_id, str) or not _CHARACTER_ID.fullmatch(character_id):
        raise CharacterRevisionError("Invalid character identifier")
    root = Path(directory).expanduser()
    if root.is_symlink() or not root.is_dir():
        raise CharacterRevisionError("Character directory is missing or unsafe")
    revision_dir = root / "revisions"
    if revision_dir.is_symlink():
        raise CharacterRevisionError("Character revision directory is unsafe")
    if not revision_dir.exists():
        if not create:
            return None
        try:
            revision_dir.mkdir()
        except FileExistsError:
            pass
    if not revision_dir.is_dir() or not revision_dir.resolve().is_relative_to(root.resolve()):
        raise CharacterRevisionError("Character revision directory is unsafe")
    target = revision_dir / f"{character_id}.revisions.json"
    if target.is_symlink():
        raise CharacterRevisionError("Character revision ledger path is unsafe")
    return target


def _validate_ledger(value: object, character_id: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {
        "schema_version", "character_id", "current_revision",
        "updated_at", "deleted_at", "revisions",
    }:
        raise CharacterRevisionError("Character revision ledger has an invalid structure")
    if (
        value["schema_version"] != 1
        or isinstance(value["schema_version"], bool)
        or value["character_id"] != character_id
        or not isinstance(value["current_revision"], int)
        or isinstance(value["current_revision"], bool)
        or not isinstance(value["updated_at"], str)
        or not value["updated_at"]
        or len(value["updated_at"]) > 64
        or (value["deleted_at"] is not None and (
            not isinstance(value["deleted_at"], str) or not value["deleted_at"]
            or len(value["deleted_at"]) > 64
        ))
        or not isinstance(value["revisions"], list)
        or not 1 <= len(value["revisions"]) <= _MAX_REVISIONS
        or value["current_revision"] != len(value["revisions"])
    ):
        raise CharacterRevisionError("Character revision ledger failed validation")

    for expected_revision, entry in enumerate(value["revisions"], start=1):
        if not isinstance(entry, dict) or set(entry) != {
            "revision", "created_at", "identity_fingerprint", "profile_sha256", "profile",
        }:
            raise CharacterRevisionError("Character revision entry has an invalid structure")
        if (
            entry["revision"] != expected_revision
            or isinstance(entry["revision"], bool)
            or not isinstance(entry["created_at"], str)
            or not entry["created_at"]
            or len(entry["created_at"]) > 64
            or not isinstance(entry["identity_fingerprint"], str)
            or not _SHA256.fullmatch(entry["identity_fingerprint"])
            or not isinstance(entry["profile_sha256"], str)
            or not _SHA256.fullmatch(entry["profile_sha256"])
        ):
            raise CharacterRevisionError("Character revision entry failed validation")
        try:
            profile = CharacterProfile.from_dict(entry["profile"])
        except (CharacterProfileError, TypeError):
            raise CharacterRevisionError("Character revision profile failed validation") from None
        if (
            profile.id != character_id
            or profile.identity_fingerprint != entry["identity_fingerprint"]
            or profile_digest(profile) != entry["profile_sha256"]
        ):
            raise CharacterRevisionError("Character revision checksum does not match its snapshot")
    return value


def load_character_revision_ledger(
    directory: str | Path, character_id: str
) -> dict[str, Any] | None:
    target = _ledger_path(directory, character_id, create=False)
    if target is None or not target.exists():
        return None
    if not target.is_file():
        raise CharacterRevisionError("Character revision ledger is not a regular file")
    try:
        with target.open("rb") as stream:
            raw = stream.read(_MAX_LEDGER_BYTES + 1)
    except OSError:
        raise CharacterRevisionError("Could not read character revision ledger") from None
    if len(raw) > _MAX_LEDGER_BYTES:
        raise CharacterRevisionError("Character revision ledger exceeds the 20 MiB limit")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError):
        raise CharacterRevisionError("Character revision ledger is not valid UTF-8 JSON") from None
    return _validate_ledger(value, character_id)


def save_character_revision_ledger(directory: str | Path, ledger: dict[str, Any]) -> None:
    character_id = ledger.get("character_id") if isinstance(ledger, dict) else None
    if not isinstance(character_id, str):
        raise CharacterRevisionError("Character revision ledger has no valid identifier")
    value = _validate_ledger(ledger, character_id)
    try:
        encoded = json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, RecursionError):
        raise CharacterRevisionError("Character revision ledger cannot be serialized") from None
    if len(encoded) > _MAX_LEDGER_BYTES:
        raise CharacterRevisionError("Character revision ledger exceeds the 20 MiB limit")
    target = _ledger_path(directory, character_id, create=True)
    if target is None:
        raise CharacterRevisionError("Character revision ledger path is unavailable")
    try:
        atomic_write_bytes(target, encoded)
    except WorkspaceError:
        raise CharacterRevisionError("Could not persist character revision ledger") from None


def create_character_revision_ledger(
    profile: CharacterProfile, timestamp: str | None = None
) -> dict[str, Any]:
    created_at = timestamp or _now()
    return {
        "schema_version": 1,
        "character_id": profile.id,
        "current_revision": 1,
        "updated_at": created_at,
        "deleted_at": None,
        "revisions": [{
            "revision": 1,
            "created_at": created_at,
            "identity_fingerprint": profile.identity_fingerprint,
            "profile_sha256": profile_digest(profile),
            "profile": profile.to_dict(),
        }],
    }


def append_character_revision(
    ledger: dict[str, Any], profile: CharacterProfile, timestamp: str | None = None
) -> dict[str, Any]:
    value = _validate_ledger(ledger, profile.id)
    if value["deleted_at"] is not None:
        raise CharacterRevisionError("Deleted character IDs cannot be reused")
    if len(value["revisions"]) >= _MAX_REVISIONS:
        raise CharacterRevisionError("Character revision history reached its 100 revision limit")
    created_at = timestamp or _now()
    revisions = list(value["revisions"])
    revision = value["current_revision"] + 1
    revisions.append({
        "revision": revision,
        "created_at": created_at,
        "identity_fingerprint": profile.identity_fingerprint,
        "profile_sha256": profile_digest(profile),
        "profile": profile.to_dict(),
    })
    return {
        **value,
        "current_revision": revision,
        "updated_at": created_at,
        "revisions": revisions,
    }


def mark_character_deleted(
    ledger: dict[str, Any], timestamp: str | None = None
) -> dict[str, Any]:
    value = _validate_ledger(ledger, ledger.get("character_id", ""))
    if value["deleted_at"] is not None:
        raise CharacterRevisionError("Character is already deleted")
    deleted_at = timestamp or _now()
    return {**value, "updated_at": deleted_at, "deleted_at": deleted_at}
