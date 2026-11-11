"""Safe per-character JSON persistence inside a project character directory."""
from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

from stilla.characters.schema import CharacterProfile, CharacterProfileError

MAX_CHARACTER_BYTES = 2 * 1024 * 1024
_CHARACTER_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")


class CharacterStorageError(RuntimeError):
    """Safe character persistence failure without exposing profile contents."""


def _target(directory: str | Path, character_id: str) -> Path:
    if not isinstance(character_id, str) or not _CHARACTER_ID.fullmatch(character_id):
        raise CharacterStorageError("Invalid character identifier")
    root = Path(directory).expanduser()
    if root.exists() and root.is_symlink():
        raise CharacterStorageError("Refusing to use a symbolic-link character directory")
    if not root.exists() or not root.is_dir():
        raise CharacterStorageError("Character directory does not exist")
    target = root / f"{character_id}.character.json"
    if target.exists() and target.is_symlink():
        raise CharacterStorageError("Refusing to read or overwrite a symbolic-link character file")
    return target


def save_character(directory: str | Path, character: CharacterProfile) -> Path:
    if not isinstance(character, CharacterProfile):
        raise CharacterStorageError("character must be a validated CharacterProfile")
    target = _target(directory, character.id)
    try:
        encoded = json.dumps(character.to_dict(), ensure_ascii=False, allow_nan=False,
                             sort_keys=True, separators=(",", ":")).encode("utf-8")
    except (TypeError, ValueError):
        raise CharacterStorageError("Character profile cannot be safely serialized") from None
    if len(encoded) > MAX_CHARACTER_BYTES:
        raise CharacterStorageError("Character profile exceeds the 2 MiB limit")
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=target.parent, prefix=".character-",
                                         suffix=".tmp", delete=False) as stream:
            temp_name = stream.name
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, target)
        temp_name = None
    except OSError:
        raise CharacterStorageError("Could not save character; the previous file was preserved") from None
    finally:
        if temp_name is not None:
            try:
                os.unlink(temp_name)
            except OSError:
                pass
    return target


def load_character(directory: str | Path, character_id: str) -> CharacterProfile:
    target = _target(directory, character_id)
    try:
        with target.open("rb") as stream:
            raw = stream.read(MAX_CHARACTER_BYTES + 1)
    except OSError:
        raise CharacterStorageError("Could not read character profile") from None
    if len(raw) > MAX_CHARACTER_BYTES:
        raise CharacterStorageError("Character profile exceeds the 2 MiB limit")
    try:
        data = json.loads(raw.decode("utf-8"))
        return CharacterProfile.from_dict(data)
    except (UnicodeDecodeError, json.JSONDecodeError, CharacterProfileError, TypeError):
        raise CharacterStorageError("Character profile failed schema validation") from None
