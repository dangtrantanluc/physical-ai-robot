"""StopBehavior — commanded emergency/explicit halt.

Distinct from Idle: Stop is entered deliberately (voice command or safety override)
and is 'sticky' in the planner (stays until explicitly changed). Behaviorally it
also commands zero velocity, but keeping it separate makes intent explicit in logs
and lets a future version add e.g. active braking.
"""

from __future__ import annotations

from app.domain.value_objects.enums import BehaviorType
from app.domain.value_objects.plan import BehaviorOutput
from app.domain.value_objects.robot_context import RobotContext
from app.infrastructure.behaviors.base import BaseBehavior


class StopBehavior(BaseBehavior):
    """Robot is explicitly stopped."""

    behavior_type = BehaviorType.STOP

    async def update(self, context: RobotContext) -> BehaviorOutput:
        return BehaviorOutput.idle(self.behavior_type)
