"""YoloDetector — production detector stub (PyTorch/Ultralytics).

This module intentionally imports ``torch``/``ultralytics`` LAZILY inside methods so
importing the package (and booting the app with the MockDetector) never pays the
heavy import cost. Flesh out ``_load`` / ``detect`` and set ``VISION_DETECTOR=yolo``
to activate it via the container factory — no changes to services or behaviors.

The same pattern applies to RT-DETR and Grounding DINO: subclass VisionDetector,
map model outputs to :class:`Detection` objects with normalized boxes.
"""

from __future__ import annotations

from app.core.logging import get_logger
from app.domain.interfaces.vision import Frame, VisionDetector
from app.domain.value_objects.perception import Perception

logger = get_logger(__name__)


class YoloDetector(VisionDetector):
    """Ultralytics YOLO detector. Not wired by default — see module docstring."""

    def __init__(self, model_path: str, *, confidence: float = 0.35) -> None:
        self._model_path = model_path
        self._confidence = confidence
        self._model = None  # loaded lazily on first use / warmup

    async def warmup(self) -> None:
        self._load()

    def _load(self) -> None:
        if self._model is not None:
            return
        # Lazy heavy import — keeps app startup fast when using MockDetector.
        from ultralytics import YOLO  # type: ignore[import-not-found]

        logger.info("yolo_loading", model_path=self._model_path)
        self._model = YOLO(self._model_path)

    async def detect(self, image: Frame) -> Perception:  # pragma: no cover - stub
        raise NotImplementedError(
            "YoloDetector is a stub. Implement inference here (run model, map "
            "results.boxes to normalized Detection objects) and return a Perception."
        )
