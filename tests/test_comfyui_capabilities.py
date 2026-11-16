import pytest

from stilla.ai.comfyui_capabilities import (
    ComfyUICapabilityError,
    inspect_comfyui_capabilities,
)


def node():
    return {"input": {"required": {}}, "output": []}


def test_reports_basic_nodes_and_reference_conditioning_candidate_without_overclaiming():
    catalog = {
        "CLIPTextEncode": node(),
        "KSampler": node(),
        "LoadImage": node(),
        "SaveImage": node(),
        "IPAdapterAdvanced": node(),
        "CheckpointLoaderSimple": node(),
    }
    result = inspect_comfyui_capabilities(catalog)
    assert result.basic_text_to_image_available
    assert result.missing_basic_nodes == ()
    assert result.reference_conditioning_candidates == ("IPAdapterAdvanced",)
    assert result.to_dict()["reference_conditioning_verified"] is False


def test_reports_missing_basic_nodes():
    result = inspect_comfyui_capabilities({"KSampler": node()})
    assert not result.basic_text_to_image_available
    assert result.missing_basic_nodes == ("CLIPTextEncode", "LoadImage", "SaveImage")


@pytest.mark.parametrize("catalog", [None, [], {}, {"node": None}, {"node": {"input": []}}])
def test_rejects_invalid_or_empty_catalog(catalog):
    with pytest.raises(ComfyUICapabilityError):
        inspect_comfyui_capabilities(catalog)


def test_rejects_unsafe_node_names():
    with pytest.raises(ComfyUICapabilityError, match="invalid node name"):
        inspect_comfyui_capabilities({"../outside": node()})


def test_rejects_catalog_over_node_limit():
    # Use an overridden-size fixture without constructing huge metadata payloads.
    catalog = {f"Node{i}": node() for i in range(50_001)}
    with pytest.raises(ComfyUICapabilityError, match="node limit"):
        inspect_comfyui_capabilities(catalog)
