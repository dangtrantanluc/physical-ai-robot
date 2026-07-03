"""Decode base64 media payloads from the robot into usable buffers.

The Android client sends the camera frame and audio chunk as base64 strings in the
``/robot/step`` body. These helpers turn them into an OpenCV image / raw bytes.
They are tolerant: malformed or empty payloads yield ``None`` rather than raising,
so a single bad frame never crashes the control loop.
"""

from __future__ import annotations

import base64
import binascii

import cv2
import numpy as np

from app.core.logging import get_logger

logger = get_logger(__name__)

# Data-URI prefix guard, e.g. "data:image/jpeg;base64,....".
_DATA_URI_SEP = ";base64,"


def _strip_data_uri(payload: str) -> str:
    if payload.startswith("data:") and _DATA_URI_SEP in payload:
        return payload.split(_DATA_URI_SEP, 1)[1]
    return payload


def decode_base64(payload: str | None) -> bytes | None:
    """Decode a (optionally data-URI-prefixed) base64 string to bytes."""
    if not payload:
        return None
    try:
        return base64.b64decode(_strip_data_uri(payload), validate=False)
    except (binascii.Error, ValueError):
        logger.warning("media_decode_failed", kind="base64")
        return None


def decode_image(payload: str | None) -> np.ndarray | None:
    """Decode a base64 image string into a BGR ``ndarray`` (OpenCV convention).

    Returns ``None`` for empty/undecodable/corrupt image data.
    """
    raw = decode_base64(payload)
    if not raw:
        return None
    buffer = np.frombuffer(raw, dtype=np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if image is None:
        logger.warning("media_decode_failed", kind="image")
    return image


def decode_audio(payload: str | None) -> bytes | None:
    """Decode a base64 audio string into raw bytes (encoding is recognizer-defined)."""
    return decode_base64(payload)
