"""FollowBehavior — proportional visual servoing to follow a person.

Two decoupled proportional controllers:
  * Angular: steer so the person's bounding box is horizontally centered.
  * Linear:  drive so the person's bounding-box height matches a target ratio
             (a monocular distance proxy — a bigger box means the person is closer).

All coordinates are normalized (0..1), so the controller is resolution-independent.
Gains, target ratio and deadzone come from configuration — no magic numbers.
"""

from __future__ import annotations

from app.core.config import FollowSettings
from app.domain.value_objects.enums import BehaviorType
from app.domain.value_objects.plan import BehaviorOutput
from app.domain.value_objects.robot_context import RobotContext
from app.domain.value_objects.velocity import Velocity
from app.infrastructure.behaviors.base import BaseBehavior, MotionBounds

_FRAME_CENTER = 0.5


class FollowBehavior(BaseBehavior):
    """Visual-servoing follow controller."""

    behavior_type = BehaviorType.FOLLOW

    def __init__(self, bounds: MotionBounds, *, settings: FollowSettings) -> None:
        super().__init__(bounds)
        self._cfg = settings

    async def update(self, context: RobotContext) -> BehaviorOutput:
        person = context.perception.best_person()
        if person is None:
            # No target this tick — command a stop. (The planner will normally have
            # switched us to SEARCH already.)
            return BehaviorOutput(
                behavior=self.behavior_type,
                velocity=Velocity.stop(),
                metadata={"target": False},
            )

        box = person.box

        # --- Angular: center the target horizontally ---
        offset_x = box.center_x - _FRAME_CENTER  # >0 => target is to the right
        if abs(offset_x) <= self._cfg.deadzone:  # noqa: SIM108 (clarity over ternary)
            angular = 0.0  # within deadzone: hold heading
        else:
            # Turn toward the target: right offset -> turn right (negative angular).
            angular = -self._cfg.kp_angular * offset_x

        # --- Linear: hold target distance via bbox height ---
        height_error = self._cfg.target_bbox_ratio - box.height  # >0 => too far -> forward
        linear = self._cfg.kp_linear * height_error

        return BehaviorOutput(
            behavior=self.behavior_type,
            velocity=Velocity(linear=linear, angular=angular),
            metadata={
                "target": True,
                "confidence": round(person.confidence, 3),
                "offset_x": round(offset_x, 3),
                "bbox_height": round(box.height, 3),
            },
        )
