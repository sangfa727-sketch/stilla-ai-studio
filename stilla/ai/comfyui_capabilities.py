"""Read-only, schema-aware discovery of installed ComfyUI reference-conditioning nodes."""
from __future__ import annotations

from dataclasses import asdict, dataclass

from stilla.ai.comfyui_config import ComfyUIConfig
from stilla.ai.comfyui_diagnostics import _get_json

_MAX_NODE_CLASSES = 20_000
_MAX_INPUT_NAMES = 128
_MAX_CLASS_NAME = 128
_MAX_VERSION_LENGTH = 64
_MAX_CHOICE_OPTIONS = 512
_MAX_CHOICE_LENGTH = 200

# These are known ComfyUI node contracts, not fuzzy name matches. A class name
# alone is never sufficient: every required node and its required input schema
# must be present before a capability is marked available.
_GROUPS: dict[str, tuple[tuple[str, tuple[str, ...]], ...]] = {
    "ipadapter": (
        ("IPAdapterModelLoader", ("ipadapter_file",)),
        ("IPAdapterApply", ("ipadapter", "clip_vision", "image", "model", "weight")),
    ),
    "instantid": (
        ("InstantIDModelLoader", ("instantid_file",)),
        ("InstantIDFaceAnalysis", ("provider",)),
        ("ApplyInstantID", ("instantid", "insightface", "image", "model", "positive", "negative")),
    ),
}


class ComfyUICapabilityError(RuntimeError):
    """A safe error while inspecting the local ComfyUI node catalog."""


@dataclass(frozen=True, slots=True)
class RequiredInputEvidence:
    name: str
    input_type: str | None
    choice_count: int | None = None


@dataclass(frozen=True, slots=True)
class NodeEvidence:
    class_name: str
    required_inputs: tuple[str, ...]
    required_input_types: tuple[RequiredInputEvidence, ...]
    schema_valid: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "class_name": self.class_name,
            "required_inputs": list(self.required_inputs),
            "required_input_types": [asdict(item) for item in self.required_input_types],
            "schema_valid": self.schema_valid,
        }


@dataclass(frozen=True, slots=True)
class ConditioningCapability:
    capability: str
    status: str
    nodes: tuple[NodeEvidence, ...]
    missing_nodes: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "capability": self.capability,
            "status": self.status,
            "nodes": [node.to_dict() for node in self.nodes],
            "missing_nodes": list(self.missing_nodes),
        }


@dataclass(frozen=True, slots=True)
class ConditioningCapabilityReport:
    status: str
    comfyui_version: str | None
    node_count: int
    capabilities: tuple[ConditioningCapability, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "comfyui_version": self.comfyui_version,
            "node_count": self.node_count,
            "capabilities": [item.to_dict() for item in self.capabilities],
            "generation_ready": False,
        }


def _version(system_stats: object) -> str | None:
    if not isinstance(system_stats, dict):
        return None
    system = system_stats.get("system")
    if not isinstance(system, dict):
        return None
    value = system.get("comfyui_version")
    if not isinstance(value, str) or not value.strip():
        return None
    # Version is informational only; bound and strip control characters.
    clean = "".join(char for char in value.strip() if char.isprintable())
    return clean[:_MAX_VERSION_LENGTH] or None


def _required_inputs(
    node: object,
) -> tuple[tuple[str, ...], tuple[RequiredInputEvidence, ...], bool]:
    if not isinstance(node, dict):
        return (), (), False
    inputs = node.get("input")
    if not isinstance(inputs, dict):
        return (), (), False
    required = inputs.get("required", {})
    if not isinstance(required, dict) or len(required) > _MAX_INPUT_NAMES:
        return (), (), False

    names: list[str] = []
    evidence: list[RequiredInputEvidence] = []
    schema_valid = True
    for name, spec in required.items():
        if (
            not isinstance(name, str)
            or not name
            or len(name) > _MAX_CLASS_NAME
            or not name.isprintable()
        ):
            return (), (), False
        names.append(name)
        if not isinstance(spec, (list, tuple)) or not spec:
            evidence.append(RequiredInputEvidence(name, None))
            schema_valid = False
            continue

        descriptor = spec[0]
        if (
            isinstance(descriptor, str)
            and descriptor
            and len(descriptor) <= _MAX_CLASS_NAME
            and descriptor.isprintable()
        ):
            evidence.append(RequiredInputEvidence(name, descriptor))
        elif (
            isinstance(descriptor, (list, tuple))
            and 0 < len(descriptor) <= _MAX_CHOICE_OPTIONS
            and all(
                isinstance(option, str)
                and 0 < len(option) <= _MAX_CHOICE_LENGTH
                and option.isprintable()
                for option in descriptor
            )
        ):
            # Do not expose enum values: they may contain local model filenames.
            evidence.append(RequiredInputEvidence(name, "COMBO", len(descriptor)))
        else:
            evidence.append(RequiredInputEvidence(name, None))
            schema_valid = False

    return (
        tuple(sorted(names)),
        tuple(sorted(evidence, key=lambda item: item.name)),
        schema_valid,
    )


def discover_conditioning_capabilities(
    object_info: object, *, system_stats: object = None
) -> ConditioningCapabilityReport:
    """Inspect a bounded /object_info payload; never contacts ComfyUI itself."""
    if not isinstance(object_info, dict):
        raise ComfyUICapabilityError("ComfyUI node catalog must be an object")
    if len(object_info) > _MAX_NODE_CLASSES:
        raise ComfyUICapabilityError("ComfyUI node catalog exceeds the supported class limit")

    reports: list[ConditioningCapability] = []
    for capability, contracts in _GROUPS.items():
        evidence: list[NodeEvidence] = []
        missing: list[str] = []
        present = 0
        valid = 0
        for class_name, expected_inputs in contracts:
            node = object_info.get(class_name)
            if node is None:
                missing.append(class_name)
                continue
            present += 1
            names, input_types, schema_valid = _required_inputs(node)
            # Required inputs may include additional implementation
            # details, but every contract input must be explicitly required.
            schema_valid = schema_valid and set(expected_inputs).issubset(names)
            if not schema_valid:
                missing.append(class_name + " (required input schema mismatch)")
            else:
                valid += 1
            evidence.append(NodeEvidence(class_name, names, input_types, schema_valid))
        status = "available" if valid == len(contracts) else "partial" if present else "unsupported"
        reports.append(ConditioningCapability(capability, status, tuple(evidence), tuple(missing)))

    statuses = {item.status for item in reports}
    overall = "available" if statuses == {"available"} else "partial" if "available" in statuses or "partial" in statuses else "unsupported"
    return ConditioningCapabilityReport(
        status=overall,
        comfyui_version=_version(system_stats),
        node_count=len(object_info),
        capabilities=tuple(reports),
    )


def inspect_local_conditioning_capabilities(config: ComfyUIConfig) -> ConditioningCapabilityReport:
    """Read /object_info and /system_stats from the validated loopback endpoint only."""
    if not isinstance(config, ComfyUIConfig):
        raise TypeError("A validated ComfyUIConfig is required")
    try:
        stats = _get_json(config, "system_stats")
        catalog = _get_json(config, "object_info")
        return discover_conditioning_capabilities(catalog, system_stats=stats)
    except (OSError, TimeoutError, ValueError) as exc:
        raise ComfyUICapabilityError(
            "Could not safely inspect the configured local ComfyUI capabilities"
        ) from exc
