"""RobotContext — the consolidated per-tick input to planners and behaviors.

This is what a planner reasons over and what a behavior acts on. It bundles the
perception, the recognized voice command, telemetry (battery, reported state) and
the robot's currently-active behavior. Passing one immutable object keeps method
signatures stable as the system grows (a future NavigationBehavior can read a new
field without changing the ``Behavior`` interface).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.value_objects.enums import BehaviorType
from app.domain.value_objects.perception import Perception
from app.domain.value_objects.speech import Transcript


@dataclass(frozen=True, slots=True)
class RobotContext:
    """Everything the brain knows about one robot at one instant."""

    robot_id: str
    perception: Perception = field(default_factory=Perception.empty)
    transcript: Transcript = field(default_factory=Transcript.empty)
    battery: float | None = None
    reported_state: str | None = None
    current_behavior: BehaviorType = BehaviorType.IDLE
    mission_id: str | None = None
    correlation_id: str | None = None

    @property
    def has_voice_command(self) -> bool:
        return not self.transcript.is_empty
