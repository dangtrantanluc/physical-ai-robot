"""MockDetector — a dependency-light stand-in for a real object detector.

It performs a genuine (if naive) OpenCV analysis so downstream behaviors receive
realistic, content-dependent perception: it thresholds the frame, finds the largest
foreground blob, and reports it as a ``person`` detection. This lets the follow /
search behaviors be exercised end-to-end before a real model is wired in.

Swap for a real detector by implementing :class:`VisionDetector` (see the YOLO stub)
and setting ``VISION_DETECTOR=yolo`` — no business logic changes.
"""

from __future__ import annotations

import asyncio

import cv2
import numpy as np

from app.domain.interfaces.vision import Frame, VisionDetector
from app.domain.value_objects.perception import (
    PERSON_LABEL,
    BoundingBox,
    Detection,
    Perception,
)

# Minimum blob area (as a fraction of the frame) to count as a detection — filters
# out speckle noise.
_MIN_AREA_RATIO = 0.02
_MAX_CONFIDENCE = 0.9


class MockDetector(VisionDetector):
    """Heuristic detector for development and tests."""

    async def detect(self, image: Frame) -> Perception:
        if image is None or image.size == 0:
            return Perception.empty()
        # OpenCV work is CPU-bound → run off the event loop.
        return await asyncio.to_thread(self._detect_sync, image)

    def _detect_sync(self, image: np.ndarray) -> Perception:
        height, width = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        # Otsu threshold separates the dominant foreground blob from background.
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return Perception(detections=(), frame_width=width, frame_height=height)

        largest = max(contours, key=cv2.contourArea)
        area_ratio = cv2.contourArea(largest) / float(width * height)
        if area_ratio < _MIN_AREA_RATIO:
            return Perception(detections=(), frame_width=width, frame_height=height)

        x, y, w, h = cv2.boundingRect(largest)
        box = BoundingBox(
            x=x / width,
            y=y / height,
            width=w / width,
            height=h / height,
        )
        confidence = min(_MAX_CONFIDENCE, 0.4 + area_ratio)
        detection = Detection(label=PERSON_LABEL, confidence=confidence, box=box)
        return Perception(
            detections=(detection,),
            frame_width=width,
            frame_height=height,
        )
