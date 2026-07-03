"""SearchBehavior — rotate in place to reacquire a lost target."""

from __future__ import annotations

from app.domain.value_objects.enums import BehaviorType
from app.domain.value_objects.plan import BehaviorOutput
from app.domain.value_objects.robot_context import RobotContext
from app.domain.value_objects.velocity import Velocity
from app.infrastructure.behaviors.base import BaseBehavior, MotionBounds


class SearchBehavior(BaseBehavior):
    """Scan by rotating in place until the planner switches back to follow."""

    behavior_type = BehaviorType.SEARCH

    def __init__(self, bounds: MotionBounds, *, angular_speed: float) -> None:
        super().__init__(bounds)
        self._angular_speed = angular_speed

    async def update(self, context: RobotContext) -> BehaviorOutput:
        # Positive angular = rotate left (CCW). No forward motion while scanning.
        return BehaviorOutput(
            behavior=self.behavior_type,
            velocity=Velocity(linear=0.0, angular=self._angular_speed),
            metadata={"scanning": True},
        )
