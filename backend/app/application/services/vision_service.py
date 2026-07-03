"""VisionService — decode a frame and run detection.

Thin use-case wrapper over the :class:`VisionDetector` port. Owns the transport
concern (base64 -> image) so behaviors/planners receive a clean domain
:class:`Perception`.
"""

from __future__ import annotations

from app.domain.interfaces.vision import VisionDetector
from app.domain.value_objects.perception import Perception
from app.utils.media import decode_image


class VisionService:
    """Turns a base64 frame into a :class:`Perception`."""

    def __init__(self, detector: VisionDetector) -> None:
        self._detector = detector

    async def perceive(self, image_b64: str | None) -> Perception:
        image = decode_image(image_b64)
        if image is None:
            return Perception.empty()
        return await self._detector.detect(image)
