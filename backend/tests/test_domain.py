"""Unit tests for domain value objects."""

from __future__ import annotations

from app.domain.value_objects.perception import (
    PERSON_LABEL,
    BoundingBox,
    Detection,
    Perception,
)
from app.domain.value_objects.velocity import Velocity


def test_velocity_clamp_limits_both_components():
    v = Velocity(linear=5.0, angular=-9.0).clamp(0.6, 1.5)
    assert v.linear == 0.6
    assert v.angular == -1.5


def test_velocity_scale():
    assert Velocity(1.0, 2.0).scale(0.5) == Velocity(0.5, 1.0)


def test_velocity_stop():
    assert Velocity.stop() == Velocity(0.0, 0.0)


def test_bounding_box_center_and_area():
    box = BoundingBox(x=0.2, y=0.1, width=0.4, height=0.5)
    assert box.center_x == 0.4
    assert box.center_y == 0.35
    assert abs(box.area - 0.2) < 1e-9


def test_perception_best_person_picks_highest_confidence():
    low = Detection(PERSON_LABEL, 0.4, BoundingBox(0, 0, 0.1, 0.1))
    high = Detection(PERSON_LABEL, 0.8, BoundingBox(0.5, 0.5, 0.1, 0.1))
    chair = Detection("chair", 0.99, BoundingBox(0, 0, 0.2, 0.2))
    perception = Perception(detections=(low, high, chair), frame_width=100, frame_height=100)

    assert perception.has_person
    assert perception.best_person() is high
    assert perception.summary() == {PERSON_LABEL: 2, "chair": 1}


def test_perception_empty_has_no_person():
    empty = Perception.empty()
    assert not empty.has_person
    assert empty.best_person() is None
