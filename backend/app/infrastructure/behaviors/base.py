"""BaseBehavior — shared behavior scaffolding.

Provides a single place for the cross-cutting safety concern every behavior needs:
clamping the commanded velocity to the configured motion limits. Concrete behaviors
implement only ``update`` (the interesting control logic); ``execute`` wraps it and
enforces the limits so no behavior can ever command an unsafe speed.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.interfaces.behavior import Behavior
from app.domain.value_objects.plan import BehaviorOutput
from app.domain.value_objects.robot_context import RobotContext


@dataclass(frozen=True, slots=True)
class MotionBounds:
    """Velocity ceilings injected into every behavior."""

    max_linear: float
    max_angular: float


class BaseBehavior(Behavior):
    """Common base: enforces motion limits around each behavior's ``update``."""

    def __init__(self, bounds: MotionBounds) -> None:
        self._bounds = bounds

    async def execute(self, context: RobotContext) -> BehaviorOutput:
        output = await self.update(context)
        clamped = output.velocity.clamp(self._bounds.max_linear, self._bounds.max_angular)
        if clamped == output.velocity:
            return output
        return BehaviorOutput(
            behavior=output.behavior,
            velocity=clamped,
            speech=output.speech,
            metadata=output.metadata,
        )
