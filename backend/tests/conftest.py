"""Shared test fixtures + in-memory fakes for the domain ports.

The fakes let us unit-test the application/behavior logic with zero infrastructure
(no Postgres, no Redis) — exactly the "unit-test friendly" goal of the design.
"""

from __future__ import annotations

import base64
from datetime import UTC, datetime

import cv2
import numpy as np
import pytest

from app.core.config import Settings
from app.domain.entities.memory import MemoryRecord
from app.domain.entities.robot import Robot
from app.domain.interfaces.memory import MemoryRepository
from app.domain.interfaces.repositories import LogEntry, LogRepository, RobotRepository
from app.domain.interfaces.state_store import RobotSnapshot, RobotStateStore
from app.domain.value_objects.enums import BehaviorType

# ---- Fakes -----------------------------------------------------------------


class FakeStateStore(RobotStateStore):
    def __init__(self) -> None:
        self._data: dict[str, RobotSnapshot] = {}

    async def get(self, robot_id: str) -> RobotSnapshot:
        return self._data.get(robot_id) or RobotSnapshot.initial(robot_id)

    async def set(self, snapshot: RobotSnapshot) -> None:
        self._data[snapshot.robot_id] = snapshot

    async def ping(self) -> bool:
        return True


class FakeRobotRepository(RobotRepository):
    def __init__(self) -> None:
        self.robots: dict[str, Robot] = {}

    async def get(self, robot_id: str) -> Robot | None:
        return self.robots.get(robot_id)

    async def get_or_create(self, robot_id: str, *, name: str | None = None) -> Robot:
        if robot_id not in self.robots:
            self.robots[robot_id] = Robot(id=robot_id, name=name or robot_id)
        return self.robots[robot_id]

    async def save_observation(
        self, robot_id, *, behavior, battery, mission_id, seen_at
    ) -> Robot:
        robot = await self.get_or_create(robot_id)
        robot.observe(behavior=behavior, battery=battery, mission_id=mission_id, seen_at=seen_at)
        return robot


class FakeLogRepository(LogRepository):
    def __init__(self) -> None:
        self.entries: list[LogEntry] = []

    async def add(self, entry: LogEntry) -> None:
        self.entries.append(entry)


class FakeMemoryRepository(MemoryRepository):
    def __init__(self) -> None:
        self.records: list[MemoryRecord] = []

    async def save(self, record: MemoryRecord) -> MemoryRecord:
        self.records.append(record)
        return record

    async def search(self, robot_id, query, *, limit=10) -> list[MemoryRecord]:
        return [r for r in self.records if r.robot_id == robot_id][:limit]


# ---- Fixtures --------------------------------------------------------------


@pytest.fixture
def settings() -> Settings:
    """Default settings (no .env dependence in unit tests)."""
    return Settings()


@pytest.fixture
def state_store() -> FakeStateStore:
    return FakeStateStore()


@pytest.fixture
def robot_repo() -> FakeRobotRepository:
    return FakeRobotRepository()


@pytest.fixture
def log_repo() -> FakeLogRepository:
    return FakeLogRepository()


@pytest.fixture
def memory_repo() -> FakeMemoryRepository:
    return FakeMemoryRepository()


@pytest.fixture
def now() -> datetime:
    return datetime.now(UTC)


def encode_image(image: np.ndarray) -> str:
    ok, buffer = cv2.imencode(".png", image)
    assert ok
    return base64.b64encode(buffer.tobytes()).decode("ascii")


@pytest.fixture
def person_image_b64() -> str:
    """A synthetic frame with a bright blob the MockDetector reports as a person.

    The blob sits right-of-center so follow-controller direction can be asserted.
    """
    frame = np.zeros((120, 160, 3), dtype=np.uint8)
    # White rectangle occupying the right-center region.
    cv2.rectangle(frame, (95, 30), (150, 110), (255, 255, 255), thickness=-1)
    return encode_image(frame)


@pytest.fixture
def blank_image_b64() -> str:
    return encode_image(np.zeros((120, 160, 3), dtype=np.uint8))


def encode_command(text: str) -> str:
    """Encode a voice command as the MockRecognizer expects (base64 of UTF-8 text)."""
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


@pytest.fixture(params=["follow", "stop", "search"])
def command_word(request) -> str:
    return request.param


def behavior(name: str) -> BehaviorType:
    return BehaviorType(name)
