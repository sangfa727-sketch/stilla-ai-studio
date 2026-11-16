import pytest

from stilla.ai.comfyui_capabilities import (
    ComfyUICapabilityError,
    discover_conditioning_capabilities,
    inspect_local_conditioning_capabilities,
)
from stilla.ai.comfyui_config import ComfyUIConfig


def node(*required):
    return {"input": {"required": {name: ["STRING"] for name in required}}}


def catalog_with_ipadapter():
    return {
        "IPAdapterModelLoader": node("ipadapter_file"),
        "IPAdapterApply": node("ipadapter", "clip_vision", "image", "model", "weight"),
    }


def test_exact_installed_node_schemas_report_ipadapter_available():
    report = discover_conditioning_capabilities(
        catalog_with_ipadapter(),
        system_stats={"system": {"comfyui_version": "0.3.26"}},
    )
    result = report.to_dict()
    ipadapter = next(item for item in result["capabilities"] if item["capability"] == "ipadapter")
    assert ipadapter["status"] == "available"
    assert report.comfyui_version == "0.3.26"
    assert result["generation_ready"] is False
    assert result["status"] == "partial"


def test_absent_nodes_are_unsupported_not_guessed():
    report = discover_conditioning_capabilities({"KSampler": node("seed")})
    assert all(item.status == "unsupported" for item in report.capabilities)
    assert report.status == "unsupported"


def test_partial_node_pack_reports_missing_classes():
    report = discover_conditioning_capabilities({"IPAdapterModelLoader": node("ipadapter_file")})
    ipadapter = next(item for item in report.capabilities if item.capability == "ipadapter")
    assert ipadapter.status == "partial"
    assert ipadapter.missing_nodes == ("IPAdapterApply",)


def test_malformed_or_incomplete_schema_fails_closed():
    report = discover_conditioning_capabilities({
        "IPAdapterModelLoader": {"input": {"required": "bad"}},
        "IPAdapterApply": node("ipadapter", "clip_vision", "image", "model"),
    })
    ipadapter = next(item for item in report.capabilities if item.capability == "ipadapter")
    assert ipadapter.status == "partial"
    assert all(not item.schema_valid for item in ipadapter.nodes)


def test_renamed_custom_nodes_are_not_fuzzy_matched():
    report = discover_conditioning_capabilities({
        "MyCustomIPAdapterLoader": node("ipadapter_file"),
        "MyCustomIPAdapterApply": node("ipadapter", "clip_vision", "image", "model", "weight"),
    })
    assert next(item for item in report.capabilities if item.capability == "ipadapter").status == "unsupported"


@pytest.mark.parametrize("catalog", [None, [], "invalid"])
def test_invalid_catalog_shape_is_rejected(catalog):
    with pytest.raises(ComfyUICapabilityError):
        discover_conditioning_capabilities(catalog)


def test_oversized_catalog_is_rejected():
    # Exercise the bound without allocating an enormous mapping.
    class HugeMapping(dict):
        def __len__(self):
            return 20_001

    with pytest.raises(ComfyUICapabilityError, match="class limit"):
        discover_conditioning_capabilities(HugeMapping())


def test_local_inspection_reads_only_stats_and_catalog(monkeypatch):
    calls = []

    def fake_get_json(config, path):
        calls.append(path)
        if path == "system_stats":
            return {"system": {"comfyui_version": "test-version"}}
        return catalog_with_ipadapter()

    monkeypatch.setattr("stilla.ai.comfyui_capabilities._get_json", fake_get_json)
    report = inspect_local_conditioning_capabilities(ComfyUIConfig())
    assert report.comfyui_version == "test-version"
    assert calls == ["system_stats", "object_info"]
    assert "prompt" not in calls


def test_unavailable_local_server_returns_sanitized_error(monkeypatch):
    def fail(config, path):
        raise OSError("private host details")

    monkeypatch.setattr("stilla.ai.comfyui_capabilities._get_json", fail)
    with pytest.raises(ComfyUICapabilityError) as error:
        inspect_local_conditioning_capabilities(ComfyUIConfig())
    assert "private host details" not in str(error.value)
