"""Perception value objects — the output of the vision subsystem.

Coordinates are normalized to ``[0, 1]`` relative to frame width/height so that
behaviors are resolution-independent (the same follow controller works whether the
frame is 640x480 or 1920x1080).
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Semantic constant rather than a magic string sprinkled through behaviors.
PERSON_LABEL = "person"


@dataclass(frozen=True, slots=True)
class BoundingBox:
    """Normalized bounding box in ``[0, 1]`` coordinates (x, y = top-left)."""

    x: float
    y: float
    width: float
    height: float

    @property
    def center_x(self) -> float:
        return self.x + self.width / 2.0

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2.0

    @property
    def area(self) -> float:
        return self.width * self.height


@dataclass(frozen=True, slots=True)
class Detection:
    """A single detected object."""

    label: str
    confidence: float
    box: BoundingBox

    @property
    def is_person(self) -> bool:
        return self.label == PERSON_LABEL


@dataclass(frozen=True, slots=True)
class Perception:
    """The full result of running a detector on one frame."""

    detections: tuple[Detection, ...] = field(default_factory=tuple)
    frame_width: int = 0
    frame_height: int = 0

    @classmethod
    def empty(cls) -> Perception:
        return cls()

    @property
    def has_person(self) -> bool:
        return any(d.is_person for d in self.detections)

    def best_person(self) -> Detection | None:
        """Return the highest-confidence person detection, or ``None``."""
        persons = [d for d in self.detections if d.is_person]
        if not persons:
            return None
        return max(persons, key=lambda d: d.confidence)

    def summary(self) -> dict[str, int]:
        """Label -> count map, useful for logging / last-frame metadata."""
        out: dict[str, int] = {}
        for d in self.detections:
            out[d.label] = out.get(d.label, 0) + 1
        return out
