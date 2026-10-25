import pytest

from stilla.ai import comfyui_assets
from stilla.ai.comfyui_assets import ComfyUIAssetError, ComfyUIAssetStore
from stilla.ai.comfyui_config import ComfyUIConfig
from stilla.media.workspace import ProjectWorkspace


PNG = b"\\x89PNG\\r\\n\\x1a\\n" + b"minimal-image-payload"


class FakeResponse:
    def __init__(self, payload=PNG, content_type="image/png", headers=None):
        self.payload = payload
        self.headers = {"Content-Length": str(len(payload)), "Content-Type": content_type}
        if headers is not None:
            self.headers = headers

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def getcode(self):
        return 200

    def read(self, limit):
        return self.payload[:limit]


def make_workspace(tmp_path):
    workspace = ProjectWorkspace(tmp_path / "studio")
    workspace.create_project("project1", "Test project")
    return workspace


def test_saves_valid_image_into_project_assets(monkeypatch, tmp_path):
    workspace = make_workspace(tmp_path)
    seen = {}

    class Opener:
        def open(self, request, timeout):
            seen["url"] = request.full_url
            seen["timeout"] = timeout
            return FakeResponse()

    monkeypatch.setattr(comfyui_assets, "build_opener", lambda handler: Opener())
    path = ComfyUIAssetStore(ComfyUIConfig(), workspace).save_image(
        "project1", "shot_1", {"filename": "ComfyUI_00001_.png", "subfolder": "", "type": "output"}
    )
    assert path == tmp_path / "studio/projects/project1/assets/shot_1.png"
    assert path.read_bytes() == PNG
    assert seen["url"].startswith("http://127.0.0.1:8188/view?")
    assert "filename=ComfyUI_00001_.png" in seen["url"]


@pytest.mark.parametrize(
    "reference",
    [
        {"filename": "../secret.png"},
        {"filename": "folder/file.png"},
        {"filename": "ok.png", "subfolder": "../outside"},
        {"filename": "ok.png", "type": "remote"},
    ],
)
def test_rejects_unsafe_image_references_before_network(monkeypatch, tmp_path, reference):
    workspace = make_workspace(tmp_path)
    monkeypatch.setattr(comfyui_assets, "build_opener", lambda handler: pytest.fail("network called"))
    with pytest.raises((ValueError, TypeError)):
        ComfyUIAssetStore(ComfyUIConfig(), workspace).save_image("project1", "shot1", reference)


def test_rejects_non_image_payload(tmp_path, monkeypatch):
    workspace = make_workspace(tmp_path)

    class Opener:
        def open(self, request, timeout):
            return FakeResponse(b"<html>not image</html>", "text/html")

    monkeypatch.setattr(comfyui_assets, "build_opener", lambda handler: Opener())
    with pytest.raises(ComfyUIAssetError, match="unsupported or invalid image"):
        ComfyUIAssetStore(ComfyUIConfig(), workspace).save_image(
            "project1", "shot1", {"filename": "bad.png"}
        )
    assert not (tmp_path / "studio/projects/project1/assets").exists()


def test_rejects_oversized_image_before_writing(tmp_path, monkeypatch):
    workspace = make_workspace(tmp_path)

    class Opener:
        def open(self, request, timeout):
            return FakeResponse(PNG * 10, "image/png", {"Content-Length": "1000", "Content-Type": "image/png"})

    monkeypatch.setattr(comfyui_assets, "build_opener", lambda handler: Opener())
    with pytest.raises(ComfyUIAssetError, match="size limit"):
        ComfyUIAssetStore(ComfyUIConfig(max_response_bytes=128), workspace, max_asset_bytes=64).save_image(
            "project1", "shot1", {"filename": "large.png"}
        )


def test_refuses_to_overwrite_existing_asset(tmp_path, monkeypatch):
    workspace = make_workspace(tmp_path)

    class Opener:
        def open(self, request, timeout):
            return FakeResponse()

    monkeypatch.setattr(comfyui_assets, "build_opener", lambda handler: Opener())
    store = ComfyUIAssetStore(ComfyUIConfig(), workspace)
    store.save_image("project1", "shot1", {"filename": "image.png"})
    with pytest.raises(ComfyUIAssetError, match="overwrite"):
        store.save_image("project1", "shot1", {"filename": "image.png"})


def test_rejects_missing_project_before_network(monkeypatch, tmp_path):
    workspace = ProjectWorkspace(tmp_path / "studio")
    monkeypatch.setattr(comfyui_assets, "build_opener", lambda handler: pytest.fail("network called"))
    with pytest.raises(ComfyUIAssetError, match="Project"):
        ComfyUIAssetStore(ComfyUIConfig(), workspace).save_image(
            "missing", "shot1", {"filename": "image.png"}
        )


def test_rejects_symlink_assets_directory(tmp_path, monkeypatch):
    workspace = make_workspace(tmp_path)
    project = tmp_path / "studio/projects/project1"
    outside = tmp_path / "outside"
    outside.mkdir()
    (project / "assets").symlink_to(outside, target_is_directory=True)

    class Opener:
        def open(self, request, timeout):
            return FakeResponse()

    monkeypatch.setattr(comfyui_assets, "build_opener", lambda handler: Opener())
    with pytest.raises(ComfyUIAssetError, match="assets directory"):
        ComfyUIAssetStore(ComfyUIConfig(), workspace).save_image(
            "project1", "shot1", {"filename": "image.png"}
        )
    assert list(outside.iterdir()) == []
