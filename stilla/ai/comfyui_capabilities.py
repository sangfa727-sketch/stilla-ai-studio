"""Fail-closed capability discovery for a local ComfyUI node catalog.

Presence of a custom node is only a candidate signal; it does not prove that a
particular workflow template can use it for identity conditioning.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

_NODE_NAME = re.compile(r"^[A-Za-z0-9_. -]{1,256}$")
_MAX_NODES = 50_000
_REQUIRED_TEXT_TO_IMAGE = ("CLIPTextEncode", "KSampler", "LoadImage", "SaveImage")
_REFERENCE_PREFIXES = ("IPAdapter", "ApplyPulid", "Pulid", "InstantID", "FaceID")


class ComfyUICapabilityError(ValueError):
    """Raised when the ComfyUI node catalog is malformed or exceeds safe bounds."""


@dataclass(frozen=True, slots=True)
class ComfyUIWorkflowCapabilities:
    """Bounded, read-only view of node classes exposed by ComfyUI."""

    node_count: int
    basic_text_to_image_available: bool
    missing_basic_nodes: tuple[str, ...]
    reference_conditioning_candidates: tuple[str, ...]
    available_nodes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_count": self.node_count,
            "basic_text_to_image_available": self.basic_text_to_image_available,
            "missing_basic_nodes": list(self.missing_basic_nodes),
            "reference_conditioning_candidates": list(self.reference_conditioning_candidates),
            "available_nodes": list(self.available_nodes),
            "reference_conditioning_verified": False,
        }


def inspect_comfyui_capabilities(object_info: object) -> ComfyUIWorkflowCapabilities:
    """Inspect /object_info without assuming custom-node compatibility.

    This reports installed node names only. A candidate IP-Adapter/PuLID/InstantID
    node must still be matched against a reviewed workflow template and its exact
    input schema before STILLA may claim reference conditioning is supported.
    """
    if not isinstance(object_info, dict):
        raise ComfyUICapabilityError("ComfyUI node catalog must be an object")
    if not 1 <= len(object_info) <= _MAX_NODES:
        raise ComfyUICapabilityError("ComfyUI node catalog is empty or exceeds the node limit")

    names: list[str] = []
    for name, metadata in object_info.items():
        if not isinstance(name, str) or not _NODE_NAME.fullmatch(name):
            raise ComfyUICapabilityError("ComfyUI node catalog contains an invalid node name")
        if not isinstance(metadata, dict):
            raise ComfyUICapabilityError("ComfyUI node metadata must be an object")
        # Validate the shape used by ComfyUI's object_info response while leaving
        # extension-specific input schemas opaque until a template binds them.
        inputs = metadata.get("input")
        if inputs is not None and not isinstance(inputs, dict):
            raise ComfyUICapabilityError("ComfyUI node input metadata must be an object")
        names.append(name)

    available = set(names)
    missing = tuple(node for node in _REQUIRED_TEXT_TO_IMAGE if node not in available)
    candidates = tuple(sorted(
        name for name in names
        if any(name.startswith(prefix) for prefix in _REFERENCE_PREFIXES)
    ))
    return ComfyUIWorkflowCapabilities(
        node_count=len(names),
        basic_text_to_image_available=not missing,
        missing_basic_nodes=missing,
        reference_conditioning_candidates=candidates,
        available_nodes=tuple(sorted(names)),
    )
