"""Provider-neutral contracts for image generation.

This module defines validated requests and results only. It does not download models,
start external processes, contact remote APIs, or write generated files.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, Protocol, runtime_checkable

_PROVIDER_ID = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
_ASSET_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_MAX_PROMPT = 20_000
_MAX_NEGATIVE_PROMPT = 10_000
_ALLOWED_SIZES = {256, 384, 512, 640, 768, 896, 1024}
_ALLOWED_FORMATS = {"png", "jpeg", "webp"}


class GenerationContractError(ValueError):
    """An image generation request or result violates the provider contract."""


def _text(value: object, field: str, maximum: int, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise GenerationContractError(f"{field} must be text")
    if len(value) > maximum or (not allow_empty and not value.strip()):
        raise GenerationContractError(f"{field} is empty or exceeds the supported limit")
    return value


@dataclass(frozen=True, slots=True)
class ImageGenerationRequest:
    """A bounded request that a generation provider may support."""

    prompt: str
    width: int = 512
    height: int = 512
    output_format: Literal["png", "jpeg", "webp"] = "png"
    negative_prompt: str = ""
    seed: int | None = None

    def __post_init__(self) -> None:
        _text(self.prompt, "prompt", _MAX_PROMPT)
        _text(self.negative_prompt, "negative_prompt", _MAX_NEGATIVE_PROMPT, allow_empty=True)
        for field, value in (("width", self.width), ("height", self.height)):
            if isinstance(value, bool) or not isinstance(value, int) or value not in _ALLOWED_SIZES:
                raise GenerationContractError(f"{field} must be a supported integer size")
        if self.output_format not in _ALLOWED_FORMATS:
            raise GenerationContractError("output_format must be png, jpeg, or webp")
        if self.seed is not None and (
            isinstance(self.seed, bool) or not isinstance(self.seed, int) or not 0 <= self.seed <= 2**32 - 1
        ):
            raise GenerationContractError("seed must be an unsigned 32-bit integer")


@dataclass(frozen=True, slots=True)
class ImageGenerationResult:
    """Metadata for a successfully generated project-relative image asset."""

    provider_id: str
    asset_id: str
    relative_path: str
    media_type: Literal["image/png", "image/jpeg", "image/webp"]
    width: int
    height: int
    seed: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.provider_id, str) or not _PROVIDER_ID.fullmatch(self.provider_id):
            raise GenerationContractError("provider_id must be a safe provider identifier")
        if not isinstance(self.asset_id, str) or not _ASSET_ID.fullmatch(self.asset_id):
            raise GenerationContractError("asset_id must be a safe identifier")
        path = _text(self.relative_path, "relative_path", 2048)
        normalized = path.replace("\\", "/")
        if normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized):
            raise GenerationContractError("relative_path must be project-relative")
        if any(part in {"", ".", ".."} for part in normalized.split("/")):
            raise GenerationContractError("relative_path contains an unsafe path segment")
        if self.media_type not in {"image/png", "image/jpeg", "image/webp"}:
            raise GenerationContractError("unsupported image media type")
        for field, value in (("width", self.width), ("height", self.height)):
            if isinstance(value, bool) or not isinstance(value, int) or value not in _ALLOWED_SIZES:
                raise GenerationContractError(f"{field} must be a supported integer size")
        if self.seed is not None and (
            isinstance(self.seed, bool) or not isinstance(self.seed, int) or not 0 <= self.seed <= 2**32 - 1
        ):
            raise GenerationContractError("seed must be an unsigned 32-bit integer")


@runtime_checkable
class ImageGenerationProvider(Protocol):
    """Interface for an explicitly selected image-generation backend."""

    @property
    def provider_id(self) -> str:
        """Stable, non-secret identifier for this provider."""

    def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """Generate one image and return metadata for its saved project asset."""
