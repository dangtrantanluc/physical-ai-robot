"""Unit tests for the vision path (media decoding + MockDetector)."""

from __future__ import annotations

from app.infrastructure.vision.mock_detector import MockDetector
from app.utils.media import decode_image


async def test_mock_detector_finds_person_in_blob(person_image_b64):
    image = decode_image(person_image_b64)
    assert image is not None
    perception = await MockDetector().detect(image)
    assert perception.has_person
    person = perception.best_person()
    assert person is not None
    # Blob is right-of-center in the fixture.
    assert person.box.center_x > 0.5


async def test_mock_detector_empty_on_blank(blank_image_b64):
    image = decode_image(blank_image_b64)
    perception = await MockDetector().detect(image)
    assert not perception.has_person


async def test_mock_detector_handles_none():
    perception = await MockDetector().detect(None)
    assert perception.detections == ()


def test_decode_image_rejects_garbage():
    assert decode_image("not-base64-@@@") is None
    assert decode_image(None) is None
