"""YoloDetector — real object detector backed by Ultralytics YOLO (PyTorch).

Activated with ``VISION_DETECTOR=yolo``. Loads weights from ``YOLO__MODEL_PATH``
(e.g. a ``yolov8n.pt`` placed in ``backend/models/``) and maps model outputs to the
domain :class:`Perception` with **normalized** boxes, so downstream behaviors are
unchanged whether the detector is the mock or YOLO.

``ultralytics`` + ``torch`` are imported lazily inside ``_load`` so importing this
module (and booting on the MockDetector) never pays the heavy import cost. Inference
runs in a worker thread to keep the event loop responsive.
"""

from __future__ import annotations

import asyncio

import numpy as np

from app.core.logging import get_logger
from app.domain.interfaces.vision import Frame, VisionDetector
from app.domain.value_objects.perception import BoundingBox, Detection, Perception

logger = get_logger(__name__)


class YoloDetector(VisionDetector):
    """Ultralytics YOLO detector.

    Args:
        model_path: path to a YOLO ``.pt`` weights file.
        confidence: minimum confidence threshold.
        device: torch device — ``cpu`` or ``cuda:0``.
        target_labels: if set, only these class labels are returned (e.g.
            ``{"person"}``); ``None`` returns every detected class.
    """

    def __init__(
        self,
        model_path: str,
        *,
        confidence: float = 0.35,
        device: str = "cpu",
        target_labels: set[str] | None = None,
    ) -> None:
        self._model_path = model_path
        self._confidence = confidence
        self._device = device
        self._target_labels = target_labels
        self._model = None  # loaded lazily / on warmup

    async def warmup(self) -> None:
        await asyncio.to_thread(self._load)

    def _load(self) -> None:
        if self._model is not None:
            return
        # Lazy heavy import — keeps startup fast on the mock stack.
        from ultralytics import YOLO  # type: ignore[import-not-found]

        logger.info("yolo_loading", model_path=self._model_path, device=self._device)
        self._model = YOLO(self._model_path)

    async def detect(self, image: Frame) -> Perception:
        if image is None or image.size == 0:
            return Perception.empty()
        return await asyncio.to_thread(self._detect_sync, image)

    def _detect_sync(self, image: np.ndarray) -> Perception:
        self._load()
        assert self._model is not None
        height, width = image.shape[:2]

        results = self._model.predict(
            image,
            conf=self._confidence,
            device=self._device,
            verbose=False,
        )
        if not results:
            return Perception(detections=(), frame_width=width, frame_height=height)

        result = results[0]
        names: dict[int, str] = result.names
        boxes = result.boxes
        detections: list[Detection] = []
        if boxes is not None and len(boxes) > 0:
            xyxy = boxes.xyxy.cpu().numpy()
            confs = boxes.conf.cpu().numpy()
            classes = boxes.cls.cpu().numpy().astype(int)
            for (x1, y1, x2, y2), conf, cls in zip(xyxy, confs, classes, strict=False):
                label = names.get(int(cls), str(int(cls)))
                if self._target_labels is not None and label not in self._target_labels:
                    continue
                box = BoundingBox(
                    x=float(x1) / width,
                    y=float(y1) / height,
                    width=float(x2 - x1) / width,
                    height=float(y2 - y1) / height,
                )
                detections.append(Detection(label=label, confidence=float(conf), box=box))

        return Perception(
            detections=tuple(detections),
            frame_width=width,
            frame_height=height,
        )
