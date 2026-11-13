"""Narrow PyWebView bridge for local, project-scoped persistence.

Only native file dialogs choose filesystem locations. Browser-supplied paths are never
accepted. All project operations are rooted beneath one explicitly selected workspace.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import threading
from pathlib import Path
from typing import Any
from uuid import uuid4

from stilla.characters.revisions import (
    CharacterRevisionError,
    append_character_revision,
    create_character_revision_ledger,
    load_character_revision_ledger,
    mark_character_deleted,
    profile_digest,
    save_character_revision_ledger,
)
from stilla.characters.schema import CharacterProfile, CharacterProfileError
from stilla.characters.storage import CharacterStorageError, load_character, save_character
from stilla.characters.storyboard import CharacterBoundShotPlan, StoryboardBindingError
from stilla.media.workspace import (
    ProjectWorkspace,
    WorkspaceConflictError,
    WorkspaceError,
)

_PROJECT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_CHARACTER_ID = _PROJECT_ID
_MAX_REFERENCE_BYTES = 10 * 1024 * 1024
_ALLOWED_IMAGES = {
    "png": (".png", lambda b: b.startswith(b"\x89PNG\r\n\x1a\n")),
    "jpeg": (".jpg", lambda b: b.startswith(b"\xff\xd8\xff")),
    "webp": (".webp", lambda b: len(b) >= 12 and b[:4] == b"RIFF" and b[8:12] == b"WEBP"),
}


class DesktopAPIError(ValueError):
    """Sanitized error safe to return to the local UI."""


class DesktopWorkspaceAPI:
    """Small allow-listed bridge; it exposes no arbitrary path or shell operations."""

    def __init__(self, workspace_root: str | Path | None = None) -> None:
        default_root = Path.home() / "Videos" / "STILLA Projects"
        self._lock = threading.RLock()
        self._window: Any = None
        self._workspace = ProjectWorkspace(workspace_root or default_root)

    def _attach_window(self, window: Any) -> None:
        self._window = window

    def get_runtime_info(self) -> dict[str, Any]:
        return {
            "runtime": "pywebview",
            "bridge_version": 2,
            "workspace_root": str(self._workspace.root),
            "ready": True,
        }

    def choose_workspace_directory(self) -> dict[str, Any]:
        """Open a native directory picker; JS cannot supply an arbitrary filesystem path."""
        if self._window is None:
            raise DesktopAPIError("Desktop window is not ready")
        import webview

        selected = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        if not selected:
            return {"cancelled": True}
        candidate = Path(selected[0]).expanduser().resolve()
        if not candidate.exists() or not candidate.is_dir():
            raise DesktopAPIError("Selected workspace directory is unavailable")
        with self._lock:
            self._workspace = ProjectWorkspace(candidate)
        return {"cancelled": False, "workspace_root": str(candidate)}

    def list_projects(self) -> list[dict[str, Any]]:
        with self._lock:
            try:
                return self._workspace.list_projects()
            except (OSError, WorkspaceError):
                raise DesktopAPIError("Could not list local projects") from None

    def create_project(self, title: str, language: str = "en") -> dict[str, Any]:
        project_id = uuid4().hex
        with self._lock:
            try:
                return self._workspace.create_project(project_id, title, language=language)
            except (OSError, WorkspaceError):
                raise DesktopAPIError("Could not create local project") from None

    def save_document(self, project_id: str, name: str, value: Any) -> dict[str, Any]:
        self._require_project(project_id)
        self._validate_document(name, value)
        self._bounded_json(value)
        with self._lock:
            try:
                self._workspace.save_document(project_id, name, value)
            except (OSError, WorkspaceError):
                raise DesktopAPIError("Could not save project document") from None
        return {"saved": True, "project_id": project_id, "document": name}

    def load_document(self, project_id: str, name: str) -> Any:
        value = self.load_document_versioned(project_id, name)["value"]
        if value is None and name != "storyboard":
            raise DesktopAPIError("Could not load project document")
        return value

    def load_document_versioned(self, project_id: str, name: str) -> dict[str, Any]:
        self._require_project(project_id)
        if name not in {"brief", "script", "storyboard", "settings"}:
            raise DesktopAPIError("Unsupported project document")
        with self._lock:
            try:
                result = self._workspace.load_document_versioned(project_id, name)
            except (OSError, WorkspaceError):
                raise DesktopAPIError("Could not load project document") from None
        value = result["value"]
        if value is None and name == "storyboard":
            value = self._empty_storyboard()
        elif value is not None:
            self._validate_document(name, value)
        return {"value": value, "revision": result["revision"]}

    def save_document_versioned(
        self, project_id: str, name: str, value: Any, expected_revision: str | None
    ) -> dict[str, Any]:
        self._require_project(project_id)
        self._validate_document(name, value)
        self._bounded_json(value)
        with self._lock:
            try:
                revision = self._workspace.save_document_versioned(
                    project_id, name, value, expected_revision
                )
            except WorkspaceConflictError:
                raise DesktopAPIError(
                    "This document changed in another window. Reload it before saving."
                ) from None
            except (OSError, WorkspaceError):
                raise DesktopAPIError("Could not save project document") from None
        return {
            "saved": True,
            "project_id": project_id,
            "document": name,
            "revision": revision,
        }

    def save_character_profile(
        self, project_id: str, profile_data: Any, expected_revision: int | None = None
    ) -> dict[str, Any]:
        project = self._require_project(project_id)
        try:
            profile = CharacterProfile.from_dict(profile_data)
        except (CharacterProfileError, TypeError):
            raise DesktopAPIError("Character profile failed validation") from None
        if expected_revision is not None and (
            isinstance(expected_revision, bool)
            or not isinstance(expected_revision, int)
            or expected_revision < 0
        ):
            raise DesktopAPIError("Expected character revision is invalid")
        directory = project / "characters"
        self._safe_directory(directory, project)
        with self._lock, self._workspace.project_lock(project_id):
            try:
                record = self._load_character_record_locked(directory, profile.id)
                ledger = load_character_revision_ledger(directory, profile.id)
                if ledger is not None and ledger["deleted_at"] is not None:
                    raise DesktopAPIError("Deleted character IDs cannot be reused")
                current_revision = record["revision"] if record else 0
                if expected_revision is not None and expected_revision != current_revision:
                    raise DesktopAPIError(
                        "This character changed in another window. Reload it before saving."
                    )
                if ledger is None:
                    ledger = create_character_revision_ledger(profile)
                else:
                    ledger = append_character_revision(ledger, profile)
                save_character_revision_ledger(directory, ledger)
                mirror_recovery_pending = False
                try:
                    save_character(directory, profile)
                except (OSError, CharacterStorageError):
                    # The immutable ledger is authoritative; the legacy profile file is a mirror.
                    mirror_recovery_pending = True
            except DesktopAPIError:
                raise
            except (CharacterRevisionError, CharacterStorageError, WorkspaceError, OSError):
                raise DesktopAPIError("Could not safely save character revision") from None
        return {
            "saved": True,
            "character_id": profile.id,
            "revision": ledger["current_revision"],
            "updated_at": ledger["updated_at"],
            "mirror_recovery_pending": mirror_recovery_pending,
        }

    def list_character_profile_records(self, project_id: str) -> list[dict[str, Any]]:
        project = self._require_project(project_id)
        directory = project / "characters"
        self._safe_directory(directory, project)
        revisions_dir = directory / "revisions"
        self._safe_directory(revisions_dir, project)
        identifiers: set[str] = set()
        for path in directory.glob("*.character.json"):
            character_id = path.name.removesuffix(".character.json")
            if _CHARACTER_ID.fullmatch(character_id):
                identifiers.add(character_id)
        for path in revisions_dir.glob("*.revisions.json"):
            character_id = path.name.removesuffix(".revisions.json")
            if _CHARACTER_ID.fullmatch(character_id):
                identifiers.add(character_id)
        records: list[dict[str, Any]] = []
        try:
            with self._lock, self._workspace.project_lock(project_id):
                for character_id in sorted(identifiers):
                    record = self._load_character_record_locked(directory, character_id)
                    if record is not None:
                        records.append(record)
        except (CharacterRevisionError, CharacterStorageError, WorkspaceError, OSError):
            raise DesktopAPIError(
                "Project character history failed validation; existing data was preserved."
            ) from None
        return sorted(records, key=lambda item: item["updated_at"], reverse=True)

    def list_character_profiles(self, project_id: str) -> list[dict[str, Any]]:
        return [record["profile"] for record in self.list_character_profile_records(project_id)]

    def delete_character_profile(self, project_id: str, character_id: str) -> dict[str, Any]:
        project = self._require_project(project_id)
        if not isinstance(character_id, str) or not _CHARACTER_ID.fullmatch(character_id):
            raise DesktopAPIError("Invalid character identifier")
        directory = project / "characters"
        self._safe_directory(directory, project)
        target = directory / f"{character_id}.character.json"
        with self._lock, self._workspace.project_lock(project_id):
            try:
                record = self._load_character_record_locked(directory, character_id)
                if record is None:
                    raise DesktopAPIError("Character profile does not exist")
                ledger = load_character_revision_ledger(directory, character_id)
                if ledger is None:
                    raise DesktopAPIError("Character revision history is unavailable")
                save_character_revision_ledger(directory, mark_character_deleted(ledger))
                cleanup_pending = False
                if target.is_symlink():
                    raise DesktopAPIError("Character profile path is unsafe")
                try:
                    target.unlink(missing_ok=True)
                except OSError:
                    cleanup_pending = True
            except DesktopAPIError:
                raise
            except (CharacterRevisionError, CharacterStorageError, WorkspaceError, OSError):
                raise DesktopAPIError("Could not safely delete character profile") from None
        return {
            "deleted": True,
            "character_id": character_id,
            "history_preserved": True,
            "cleanup_pending": cleanup_pending,
        }

    def load_character_profile(self, project_id: str, character_id: str) -> dict[str, Any]:
        if not isinstance(character_id, str) or not _CHARACTER_ID.fullmatch(character_id):
            raise DesktopAPIError("Invalid character identifier")
        project = self._require_project(project_id)
        directory = project / "characters"
        self._safe_directory(directory, project)
        with self._lock, self._workspace.project_lock(project_id):
            try:
                record = self._load_character_record_locked(directory, character_id)
            except (CharacterRevisionError, CharacterStorageError, WorkspaceError, OSError):
                raise DesktopAPIError("Could not safely load character profile") from None
        if record is None:
            raise DesktopAPIError("Character profile does not exist")
        return record["profile"]

    def import_character_reference(self, project_id: str, character_id: str) -> dict[str, Any]:
        """Import an image only through a native picker; never accept a JS-provided path."""
        project = self._require_project(project_id)
        if not isinstance(character_id, str) or not _CHARACTER_ID.fullmatch(character_id):
            raise DesktopAPIError("Invalid character identifier")
        self._safe_directory(project / "characters", project)
        if self._window is None:
            raise DesktopAPIError("Desktop window is not ready")
        import webview

        selected = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=("Image files (*.png;*.jpg;*.jpeg;*.webp)",),
        )
        if not selected:
            return {"cancelled": True}
        source = Path(selected[0])
        try:
            if source.is_symlink() or not source.is_file() or source.stat().st_size > _MAX_REFERENCE_BYTES:
                raise DesktopAPIError("Image must be a regular file no larger than 10 MiB")
            raw = source.read_bytes()
        except OSError:
            raise DesktopAPIError("Could not read selected image") from None
        if not raw or len(raw) > _MAX_REFERENCE_BYTES:
            raise DesktopAPIError("Image must be between 1 byte and 10 MiB")
        detected = next(
            ((kind, suffix) for kind, (suffix, check) in _ALLOWED_IMAGES.items() if check(raw)),
            None,
        )
        if detected is None:
            raise DesktopAPIError("Only valid PNG, JPEG, and WebP image signatures are accepted")
        kind, suffix = detected
        relative = Path("characters") / "references" / character_id / f"{uuid4().hex}{suffix}"
        target = project / relative
        self._safe_directory(target.parent, project)
        digest = hashlib.sha256(raw).hexdigest()
        try:
            with self._lock, self._workspace.project_lock(project_id):
                record = self._load_character_record_locked(project / "characters", character_id)
                if record is None:
                    raise DesktopAPIError("Character profile does not exist")
                self._atomic_create(target, raw)
        except DesktopAPIError:
            raise
        except (CharacterRevisionError, CharacterStorageError, WorkspaceError, OSError):
            raise DesktopAPIError("Could not verify the character before importing its reference") from None
        return {
            "cancelled": False,
            "asset_id": target.stem,
            "relative_path": relative.as_posix(),
            "mime_type": {"png": "image/png", "jpeg": "image/jpeg", "webp": "image/webp"}[kind],
            "size_bytes": len(raw),
            "sha256": digest,
        }

    def _load_character_record_locked(
        self, directory: Path, character_id: str
    ) -> dict[str, Any] | None:
        profile_path = directory / f"{character_id}.character.json"
        if profile_path.is_symlink():
            raise CharacterStorageError("Character profile path is unsafe")
        current_profile = None
        if profile_path.exists():
            current_profile = load_character(directory, character_id)
        ledger = load_character_revision_ledger(directory, character_id)
        if ledger is None:
            if current_profile is None:
                return None
            ledger = create_character_revision_ledger(current_profile)
            save_character_revision_ledger(directory, ledger)
            return {
                "profile": current_profile.to_dict(),
                "revision": 1,
                "updated_at": ledger["updated_at"],
                "mirror_recovery_pending": False,
            }
        if ledger["deleted_at"] is not None:
            if profile_path.exists():
                profile_path.unlink()
            return None

        latest = ledger["revisions"][-1]
        latest_profile = CharacterProfile.from_dict(latest["profile"])
        current_digest = profile_digest(current_profile) if current_profile is not None else None
        mirror_recovery_pending = current_digest != latest["profile_sha256"]
        if mirror_recovery_pending:
            previous_digests = {
                entry["profile_sha256"] for entry in ledger["revisions"][:-1]
            }
            if current_digest is not None and current_digest not in previous_digests:
                raise CharacterRevisionError(
                    "Current character profile diverges from its immutable revision history"
                )
            try:
                save_character(directory, latest_profile)
                mirror_recovery_pending = False
            except (OSError, CharacterStorageError):
                # The validated immutable ledger remains readable and is the source of truth.
                mirror_recovery_pending = True
        return {
            "profile": latest_profile.to_dict(),
            "revision": ledger["current_revision"],
            "updated_at": ledger["updated_at"],
            "mirror_recovery_pending": mirror_recovery_pending,
        }

    def _require_project(self, project_id: str) -> Path:
        if not isinstance(project_id, str) or not _PROJECT_ID.fullmatch(project_id):
            raise DesktopAPIError("Invalid project identifier")
        try:
            self._workspace.load_project(project_id)
        except (OSError, WorkspaceError):
            raise DesktopAPIError("Project does not exist or is unavailable") from None
        root = self._workspace.root.resolve()
        projects = root / "projects"
        project = projects / project_id
        if projects.is_symlink() or project.is_symlink():
            raise DesktopAPIError("Project path is unsafe")
        resolved = project.resolve()
        if not resolved.is_relative_to(projects.resolve()):
            raise DesktopAPIError("Project path escapes the workspace")
        return resolved

    @staticmethod
    def _safe_directory(path: Path, project: Path) -> None:
        project = project.resolve()
        current = project
        for part in path.relative_to(project).parts:
            current = current / part
            if current.is_symlink():
                raise DesktopAPIError("Project asset directory contains a symbolic link")
            current.mkdir(exist_ok=True)
            if not current.resolve().is_relative_to(project):
                raise DesktopAPIError("Project asset path escapes the project")

    @staticmethod
    def _atomic_create(target: Path, data: bytes) -> None:
        if target.exists() or target.is_symlink():
            raise DesktopAPIError("Asset already exists")
        temp_name: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", dir=target.parent, prefix=".stilla-import-", suffix=".tmp", delete=False
            ) as stream:
                temp_name = stream.name
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.link(temp_name, target)
        except FileExistsError:
            raise DesktopAPIError("Asset already exists") from None
        except OSError:
            raise DesktopAPIError("Could not store imported image") from None
        finally:
            if temp_name is not None:
                try:
                    os.unlink(temp_name)
                except OSError:
                    pass

    @staticmethod
    def _bounded_json(value: Any) -> None:
        try:
            raw = json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")
        except (TypeError, ValueError, RecursionError):
            raise DesktopAPIError("Document must contain valid JSON data") from None
        if len(raw) > 2_000_000:
            raise DesktopAPIError("Document exceeds the 2 MB limit")

    @staticmethod
    def _empty_storyboard() -> dict[str, Any]:
        return {
            "schema_version": 1,
            "shot_plan": {
                "id": "story_plan",
                "title": "Project storyboard",
                "shots": [],
            },
            "character_revisions": [],
            "bindings": [],
        }

    @staticmethod
    def _validate_document(name: str, value: Any) -> None:
        if not isinstance(name, str) or name not in {"brief", "script", "storyboard", "settings"}:
            raise DesktopAPIError("Unsupported project document")
        if name == "storyboard":
            try:
                CharacterBoundShotPlan.from_dict(value)
            except (StoryboardBindingError, TypeError):
                raise DesktopAPIError("Storyboard data failed validation") from None
