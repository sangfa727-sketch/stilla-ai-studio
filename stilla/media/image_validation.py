"""Bounded image-container metadata checks for local reference assets.

The embedded browser engine performs the full pixel decode before a preview is shown.
This module validates container structure and dimensions before large data is handed to it.
"""
from __future__ import annotations

from io import BytesIO
import warnings
from typing import Any


MAX_IMAGE_SIDE = 10_000
MAX_IMAGE_PIXELS = 40_000_000
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_JPEG_SOF = {
    0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,
}


class ImageValidationError(ValueError):
    """Raised when an image container or its declared dimensions are unsafe."""


def _dimensions(width: int, height: int) -> tuple[int, int]:
    if (
        isinstance(width, bool)
        or isinstance(height, bool)
        or width < 1
        or height < 1
        or width > MAX_IMAGE_SIDE
        or height > MAX_IMAGE_SIDE
        or width * height > MAX_IMAGE_PIXELS
    ):
        raise ImageValidationError("Image dimensions exceed the supported safety limits")
    return width, height


def _png(raw: bytes) -> tuple[int, int]:
    if (
        len(raw) < 33
        or raw[:8] != _PNG_SIGNATURE
        or int.from_bytes(raw[8:12], "big") != 13
        or raw[12:16] != b"IHDR"
    ):
        raise ImageValidationError("PNG header is incomplete or invalid")
    return _dimensions(
        int.from_bytes(raw[16:20], "big"),
        int.from_bytes(raw[20:24], "big"),
    )


def _jpeg(raw: bytes) -> tuple[int, int]:
    if len(raw) < 4 or raw[:2] != b"\xff\xd8":
        raise ImageValidationError("JPEG header is incomplete or invalid")
    offset = 2
    while offset < len(raw):
        if raw[offset] != 0xFF:
            raise ImageValidationError("JPEG marker sequence is invalid")
        while offset < len(raw) and raw[offset] == 0xFF:
            offset += 1
        if offset >= len(raw):
            break
        marker = raw[offset]
        offset += 1
        if marker in {0xD9, 0xDA}:
            break
        if marker == 0x01 or 0xD0 <= marker <= 0xD7:
            continue
        if offset + 2 > len(raw):
            raise ImageValidationError("JPEG segment length is missing")
        segment_length = int.from_bytes(raw[offset : offset + 2], "big")
        if segment_length < 2 or offset + segment_length > len(raw):
            raise ImageValidationError("JPEG segment is truncated")
        if marker in _JPEG_SOF:
            if segment_length < 8:
                raise ImageValidationError("JPEG frame header is incomplete")
            height = int.from_bytes(raw[offset + 3 : offset + 5], "big")
            width = int.from_bytes(raw[offset + 5 : offset + 7], "big")
            return _dimensions(width, height)
        offset += segment_length
    raise ImageValidationError("JPEG frame dimensions were not found")


def _webp(raw: bytes) -> tuple[int, int]:
    if len(raw) < 20 or raw[:4] != b"RIFF" or raw[8:12] != b"WEBP":
        raise ImageValidationError("WebP header is incomplete or invalid")
    riff_end = 8 + int.from_bytes(raw[4:8], "little")
    if riff_end < 20 or riff_end > len(raw):
        raise ImageValidationError("WebP RIFF length is invalid")
    offset = 12
    while offset + 8 <= riff_end:
        chunk_type = raw[offset : offset + 4]
        chunk_size = int.from_bytes(raw[offset + 4 : offset + 8], "little")
        data_start = offset + 8
        data_end = data_start + chunk_size
        if data_end > riff_end:
            raise ImageValidationError("WebP chunk is truncated")
        data = raw[data_start:data_end]
        if chunk_type == b"VP8X" and chunk_size >= 10:
            width = int.from_bytes(data[4:7], "little") + 1
            height = int.from_bytes(data[7:10], "little") + 1
            return _dimensions(width, height)
        if chunk_type == b"VP8 " and chunk_size >= 10 and data[3:6] == b"\x9d\x01\x2a":
            width = int.from_bytes(data[6:8], "little") & 0x3FFF
            height = int.from_bytes(data[8:10], "little") & 0x3FFF
            return _dimensions(width, height)
        if chunk_type == b"VP8L" and chunk_size >= 5 and data[0] == 0x2F:
            width = 1 + (((data[2] & 0x3F) << 8) | data[1])
            height = 1 + (((data[4] & 0x0F) << 10) | (data[3] << 2) | (data[2] >> 6))
            return _dimensions(width, height)
        offset = data_end + (chunk_size & 1)
    raise ImageValidationError("WebP image dimensions were not found")


def verify_image_bytes(raw: bytes) -> dict[str, Any]:
    """Fully decode a bounded image using Pillow before it is persisted or previewed."""
    info = inspect_image(raw)
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError:
        raise ImageValidationError("Pillow image decoding support is not installed") from None

    expected_format = {"png": "PNG", "jpeg": "JPEG", "webp": "WEBP"}[info["kind"]]
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(raw)) as image:
                if image.format != expected_format or image.size != (info["width"], info["height"]):
                    raise ImageValidationError("Decoded image metadata does not match its container")
                image.verify()
            with Image.open(BytesIO(raw)) as image:
                image.load()
                if image.format != expected_format or image.size != (info["width"], info["height"]):
                    raise ImageValidationError("Decoded image metadata changed during validation")
    except ImageValidationError:
        raise
    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        SyntaxError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ):
        raise ImageValidationError("Image pixel data is corrupt or unsafe to decode") from None
    return info


def inspect_image(raw: bytes) -> dict[str, Any]:
    """Validate a PNG/JPEG/WebP container header and return bounded dimensions."""
    if not isinstance(raw, bytes) or not raw:
        raise ImageValidationError("Image data is empty")
    if raw.startswith(_PNG_SIGNATURE):
        width, height = _png(raw)
        kind, extension, mime_type = "png", ".png", "image/png"
    elif raw.startswith(b"\xff\xd8\xff"):
        width, height = _jpeg(raw)
        kind, extension, mime_type = "jpeg", ".jpg", "image/jpeg"
    elif len(raw) >= 12 and raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        width, height = _webp(raw)
        kind, extension, mime_type = "webp", ".webp", "image/webp"
    else:
        raise ImageValidationError("Only PNG, JPEG, and WebP images are supported")
    return {
        "kind": kind,
        "extension": extension,
        "mime_type": mime_type,
        "width": width,
        "height": height,
        "pixels": width * height,
    }
