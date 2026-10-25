import pytest

from stilla.ai.generation import (
    GenerationContractError,
    ImageGenerationProvider,
    ImageGenerationRequest,
    ImageGenerationResult,
)


def test_request_defaults_are_bounded() -> None:
    request = ImageGenerationRequest(prompt="A cinematic mountain sunrise")
    assert (request.width, request.height, request.output_format) == (512, 512, "png")


@pytest.mark.parametrize("kwargs", [
    {"prompt": ""},
    {"prompt": "image", "width": True},
    {"prompt": "image", "height": 2048},
    {"prompt": "image", "output_format": "gif"},
    {"prompt": "image", "seed": -1},
    {"prompt": "image", "seed": True},
])
def test_invalid_request_is_rejected(kwargs: dict[str, object]) -> None:
    with pytest.raises(GenerationContractError):
        ImageGenerationRequest(**kwargs)


def test_prompt_length_is_bounded() -> None:
    with pytest.raises(GenerationContractError):
        ImageGenerationRequest(prompt="x" * 20_001)


def test_result_requires_safe_project_relative_path() -> None:
    with pytest.raises(GenerationContractError, match="project-relative"):
        ImageGenerationResult("local_diffusion", "asset1", "/tmp/image.png", "image/png", 512, 512)


@pytest.mark.parametrize("path", ["../outside.png", "assets/../outside.png", "assets//image.png", "C:\\image.png"])
def test_result_rejects_path_traversal(path: str) -> None:
    with pytest.raises(GenerationContractError):
        ImageGenerationResult("local_diffusion", "asset1", path, "image/png", 512, 512)


def test_result_rejects_invalid_metadata() -> None:
    with pytest.raises(GenerationContractError):
        ImageGenerationResult("../provider", "asset1", "assets/image.png", "image/png", 512, 512)
    with pytest.raises(GenerationContractError):
        ImageGenerationResult("local_diffusion", "asset1", "assets/image.png", "image/gif", 512, 512)


def test_provider_protocol_is_runtime_checkable() -> None:
    class FakeProvider:
        provider_id = "local_diffusion"

        def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
            return ImageGenerationResult(
                self.provider_id, "image1", "assets/image1.png", "image/png",
                request.width, request.height, request.seed,
            )

    provider: ImageGenerationProvider = FakeProvider()
    result = provider.generate(ImageGenerationRequest("Test scene"))
    assert result.relative_path == "assets/image1.png"
