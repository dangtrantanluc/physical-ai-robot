"""Mission and Task entities.

A Mission is a high-level goal assigned to a robot (e.g. "follow operator around
the warehouse"). It is decomposed into ordered Tasks. The planner/behaviors are
free to consult the active mission; the current RulePlanner does not require one,
so missions are optional at this stage but modelled for future navigation work.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from app.domain.value_objects.enums import MissionStatus, TaskStatus


@dataclass(slots=True)
class Task:
    """One ordered step within a mission."""

    name: str
    order_index: int = 0
    status: TaskStatus = TaskStatus.PENDING
    params: dict = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)
    mission_id: UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(slots=True)
class Mission:
    """A high-level goal for a robot, composed of ordered tasks."""

    name: str
    goal: str = ""
    robot_id: str | None = None
    status: MissionStatus = MissionStatus.PENDING
    params: dict = field(default_factory=dict)
    tasks: list[Task] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def activate(self) -> None:
        self.status = MissionStatus.ACTIVE

    def complete(self) -> None:
        self.status = MissionStatus.COMPLETED
