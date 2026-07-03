"""Unit tests for behaviors and the behavior manager."""

from __future__ import annotations

import pytest

from app.core.config import FollowSettings
from app.core.exceptions import BehaviorNotRegisteredError
from app.domain.value_objects.enums import BehaviorType
from app.domain.value_objects.perception import (
    PERSON_LABEL,
    BoundingBox,
    Detection,
    Perception,
)
from app.domain.value_objects.robot_context import RobotContext
from app.infrastructure.behaviors.base import MotionBounds
from app.infrastructure.behaviors.follow import FollowBehavior
from app.infrastructure.behaviors.idle import IdleBehavior
from app.infrastructure.behaviors.registry import build_behavior_manager
from app.infrastructure.behaviors.search import SearchBehavior
from app.infrastructure.behaviors.stop import StopBehavior

pytestmark = pytest.mark.asyncio

BOUNDS = MotionBounds(max_linear=0.6, max_angular=1.5)


def context_with_person(center_x: float, height: float) -> RobotContext:
    box = BoundingBox(x=center_x - 0.1, y=0.3, width=0.2, height=height)
    det = Detection(PERSON_LABEL, 0.9, box)
    return RobotContext(
        robot_id="r1",
        perception=Perception(detections=(det,), frame_width=100, frame_height=100),
    )


async def test_idle_and_stop_command_zero_velocity():
    ctx = RobotContext(robot_id="r1")
    idle_out = await IdleBehavior(BOUNDS).execute(ctx)
    stop_out = await StopBehavior(BOUNDS).execute(ctx)
    assert idle_out.velocity.linear == 0.0 and idle_out.velocity.angular == 0.0
    assert stop_out.behavior is BehaviorType.STOP


async def test_search_rotates_in_place():
    out = await SearchBehavior(BOUNDS, angular_speed=0.8).execute(RobotContext(robot_id="r1"))
    assert out.velocity.linear == 0.0
    assert out.velocity.angular == pytest.approx(0.8)


async def test_follow_turns_right_for_target_on_right():
    follow = FollowBehavior(BOUNDS, settings=FollowSettings())
    # Person right of center (center_x=0.8) => negative (right) angular.
    out = await follow.execute(context_with_person(center_x=0.8, height=0.2))
    assert out.velocity.angular < 0
    # Person appears small (far) => drive forward.
    assert out.velocity.linear > 0
    assert out.metadata["target"] is True


async def test_follow_deadzone_no_turn_when_centered():
    follow = FollowBehavior(BOUNDS, settings=FollowSettings())
    out = await follow.execute(context_with_person(center_x=0.5, height=0.45))
    assert out.velocity.angular == 0.0


async def test_follow_stops_without_target():
    follow = FollowBehavior(BOUNDS, settings=FollowSettings())
    out = await follow.execute(RobotContext(robot_id="r1", perception=Perception.empty()))
    assert out.velocity.linear == 0.0 and out.velocity.angular == 0.0
    assert out.metadata["target"] is False


async def test_base_behavior_clamps_to_motion_bounds():
    tight = MotionBounds(max_linear=0.1, max_angular=0.1)
    follow = FollowBehavior(tight, settings=FollowSettings(kp_angular=10.0, kp_linear=10.0))
    out = await follow.execute(context_with_person(center_x=0.95, height=0.05))
    assert abs(out.velocity.linear) <= 0.1
    assert abs(out.velocity.angular) <= 0.1


async def test_manager_switch_fires_lifecycle(settings):
    manager = build_behavior_manager(settings)
    ctx = RobotContext(robot_id="r1")
    behavior = manager.switch_behavior(BehaviorType.IDLE, BehaviorType.FOLLOW, ctx)
    assert behavior.behavior_type is BehaviorType.FOLLOW


async def test_manager_unknown_behavior_raises():
    from app.infrastructure.behaviors.manager import BehaviorManagerImpl

    manager = BehaviorManagerImpl()  # empty registry
    with pytest.raises(BehaviorNotRegisteredError):
        manager.get(BehaviorType.FOLLOW)
