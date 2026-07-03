"""Robot entity — the durable record of a physical robot."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domain.value_objects.enums import BehaviorType


@dataclass(slots=True)
class Robot:
    """A physical robot known to the brain.

    Identity is the device-provided ``id`` (e.g. ``realme-q-01``). Mutable state
    (battery, current behavior/mission, last-seen) is updated each control tick.
    """

    id: str
    name: str
    status: str = "online"
    battery: float | None = None
    current_behavior: BehaviorType = BehaviorType.IDLE
    current_mission_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_seen_at: datetime | None = None

    def observe(
        self,
        *,
        behavior: BehaviorType,
        battery: float | None,
        mission_id: str | None,
        seen_at: datetime,
    ) -> None:
        """Apply a fresh observation from a control tick (mutates in place)."""
        self.current_behavior = behavior
        if battery is not None:
            self.battery = battery
        self.current_mission_id = mission_id
        self.last_seen_at = seen_at
        self.status = "online"
