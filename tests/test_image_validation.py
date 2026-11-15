from __future__ import annotations

import binascii
import struct
import zlib

import pytest

from stilla.media.image_validation import (
    MAX_IMAGE_PIXELS,
    ImageValidationError,
    inspect_image,
    verify_image_bytes,
)


def _png(width: int = 1, height: int = 1) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
        )

    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    pixels = zlib.compress(b"\x00\x20\x80\xc0\xff")
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", pixels) + chunk(b"IEND", b"")


def _jpeg(width: int = 1, height: int = 1) -> bytes:
    frame = (
        b"\xff\xc0"
        + b"\x00\x0b"
        + b"\x08"
        + height.to_bytes(2, "big")
        + width.to_bytes(2, "big")
        + b"\x01\x01\x11\x00"
    )
    return b"\xff\xd8" + frame + b"\xff\xd9"


def _webp(width: int = 1, height: int = 1) -> bytes:
    data = b"\x00\x00\x00\x00" + (width - 1).to_bytes(3, "little") + (height - 1).to_bytes(3, "little")
    chunk = b"VP8X" + len(data).to_bytes(4, "little") + data
    body = b"WEBP" + chunk
    return b"RIFF" + len(body).to_bytes(4, "little") + body


@pytest.mark.parametrize(
    ("payload", "kind", "mime", "extension"),
    [
        (_png(), "png", "image/png", ".png"),
        (_jpeg(), "jpeg", "image/jpeg", ".jpg"),
        (_webp(), "webp", "image/webp", ".webp"),
    ],
)
def test_inspects_supported_image_headers(payload: bytes, kind: str, mime: str, extension: str) -> None:
    result = inspect_image(payload)
    assert result["kind"] == kind
    assert result["mime_type"] == mime
    assert result["extension"] == extension
    assert result["width"] == 1
    assert result["height"] == 1
    assert result["pixels"] == 1


@pytest.mark.parametrize(
    "payload",
    [
        b"",
        b"\x89PNG\r\n\x1a\n",
        b"\xff\xd8\xff\xd9",
        b"RIFF\x00\x00\x00\x00WEBP",
        b"not an image",
    ],
)
def test_rejects_incomplete_or_malformed_image_headers(payload: bytes) -> None:
    with pytest.raises(ImageValidationError):
        inspect_image(payload)


@pytest.mark.parametrize("payload", [_png(10_001, 1), _jpeg(1, 10_001), _webp(10_001, 1)])
def test_rejects_images_exceeding_dimension_limits(payload: bytes) -> None:
    with pytest.raises(ImageValidationError, match="dimensions"):
        inspect_image(payload)


def test_pixel_limit_is_a_fixed_safety_budget() -> None:
    assert MAX_IMAGE_PIXELS == 40_000_000
    with pytest.raises(ImageValidationError, match="dimensions"):
        inspect_image(_png(8_000, 6_000))


def test_fully_decodes_valid_png_pixels() -> None:
    result = verify_image_bytes(_png())
    assert result["mime_type"] == "image/png"
    assert result["width"] == 1
    assert result["height"] == 1


def test_rejects_corrupt_png_pixel_stream_even_with_valid_header() -> None:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
        )

    header = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    payload = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", b"not-zlib") + chunk(b"IEND", b"")
    with pytest.raises(ImageValidationError, match="corrupt or unsafe"):
        verify_image_bytes(payload)
