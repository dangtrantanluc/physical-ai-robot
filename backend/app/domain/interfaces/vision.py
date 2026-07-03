"""Vision port.

Implementations live in ``app/infrastructure/vision`` (MockDetector today; YOLO /
RT-DETR / Grounding DINO later). Business logic depends only on this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np

from app.domain.value_objects.perception import Perception

# A decoded image frame: HxWxC uint8 BGR array (OpenCV convention).
Frame = np.ndarray


class VisionDetector(ABC):
    """Detects objects in a single image frame."""

    @abstractmethod
    async def detect(self, image: Frame) -> Perception:
        """Run detection on ``image`` and return a :class:`Perception`.

        Implementations must not raise on empty/blank frames — return
        ``Perception.empty()`` instead. Heavy models should offload CPU/GPU work
        (e.g. via a thread/process pool) to keep the event loop responsive.
        """
        raise NotImplementedError

    async def warmup(self) -> None:
        """Optional: pre-load weights / run a dummy inference. Default: no-op."""
        return None
