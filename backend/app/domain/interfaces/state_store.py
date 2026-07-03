"""Hot-state store port (Redis-backed).

Holds the fast-changing per-robot state that the control loop reads/writes every
tick: the currently-active behavior, current mission, battery, last-frame metadata
and a monotonic step counter. Kept out of PostgreSQL so the loop stays low-latency
and the API stays stateless (any worker can serve the next tick).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.domain.value_objects.enums import BehaviorType


@dataclass(slots=True)
class RobotSnapshot:
    """The mutable hot state of one robot."""

    robot_id: str
    current_behavior: BehaviorType = BehaviorType.IDLE
    mission_id: str | None = None
    battery: float | None = None
    step_count: int = 0
    last_frame: dict = field(default_factory=dict)

    @classmethod
    def initial(cls, robot_id: str) -> RobotSnapshot:
        return cls(robot_id=robot_id)


class RobotStateStore(ABC):
    """Reads/writes :class:`RobotSnapshot` for a robot."""

    @abstractmethod
    async def get(self, robot_id: str) -> RobotSnapshot:
        """Return the current snapshot, or a fresh initial one if unseen."""
        raise NotImplementedError

    @abstractmethod
    async def set(self, snapshot: RobotSnapshot) -> None:
        """Persist ``snapshot`` (whole-object write)."""
        raise NotImplementedError

    @abstractmethod
    async def ping(self) -> bool:
        """Health check for the underlying store."""
        raise NotImplementedError
