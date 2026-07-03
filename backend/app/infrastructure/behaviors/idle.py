"""IdleBehavior — do nothing, safely."""

from __future__ import annotations

from app.domain.value_objects.enums import BehaviorType
from app.domain.value_objects.plan import BehaviorOutput
from app.domain.value_objects.robot_context import RobotContext
from app.infrastructure.behaviors.base import BaseBehavior


class IdleBehavior(BaseBehavior):
    """Robot holds position with zero velocity, awaiting a command."""

    behavior_type = BehaviorType.IDLE

    async def update(self, context: RobotContext) -> BehaviorOutput:
        return BehaviorOutput.idle(self.behavior_type)
