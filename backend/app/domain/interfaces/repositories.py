"""Persistence ports for durable entities.

Implemented by SQLAlchemy repositories in ``app/infrastructure/database``. Returned
values are domain entities, never ORM rows — the domain never imports SQLAlchemy.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.domain.entities.mission import Mission, Task
from app.domain.entities.robot import Robot
from app.domain.value_objects.enums import BehaviorType, MissionStatus


class RobotRepository(ABC):
    """CRUD for :class:`Robot`."""

    @abstractmethod
    async def get(self, robot_id: str) -> Robot | None:
        raise NotImplementedError

    @abstractmethod
    async def get_or_create(self, robot_id: str, *, name: str | None = None) -> Robot:
        """Return the robot, registering it on first contact (upsert)."""
        raise NotImplementedError

    @abstractmethod
    async def save_observation(
        self,
        robot_id: str,
        *,
        behavior: BehaviorType,
        battery: float | None,
        mission_id: str | None,
        seen_at: datetime,
    ) -> Robot:
        """Persist the latest control-tick observation for ``robot_id``."""
        raise NotImplementedError


class MissionRepository(ABC):
    """CRUD for :class:`Mission`."""

    @abstractmethod
    async def create(self, mission: Mission) -> Mission:
        raise NotImplementedError

    @abstractmethod
    async def get(self, mission_id: UUID) -> Mission | None:
        raise NotImplementedError

    @abstractmethod
    async def list_for_robot(self, robot_id: str, *, limit: int = 50) -> list[Mission]:
        raise NotImplementedError

    @abstractmethod
    async def set_status(self, mission_id: UUID, status: MissionStatus) -> Mission | None:
        raise NotImplementedError


class TaskRepository(ABC):
    """CRUD for :class:`Task`."""

    @abstractmethod
    async def add_many(self, tasks: list[Task]) -> list[Task]:
        raise NotImplementedError

    @abstractmethod
    async def list_for_mission(self, mission_id: UUID) -> list[Task]:
        raise NotImplementedError


@dataclass(slots=True)
class LogEntry:
    """A single control-loop telemetry record (write-only, for observability)."""

    robot_id: str
    behavior: str
    linear_velocity: float
    angular_velocity: float
    speech: str | None = None
    transcript: str | None = None
    detections: int = 0
    battery: float | None = None
    latency_ms: float | None = None
    inference_ms: float | None = None
    api_ms: float | None = None
    fps: float | None = None
    correlation_id: str | None = None
    metadata: dict = field(default_factory=dict)
    created_at: datetime | None = None


class LogRepository(ABC):
    """Append-only sink for control-loop telemetry."""

    @abstractmethod
    async def add(self, entry: LogEntry) -> None:
        raise NotImplementedError
