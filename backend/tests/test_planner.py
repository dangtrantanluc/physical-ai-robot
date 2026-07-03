"""Unit tests for the RulePlanner decision logic."""

from __future__ import annotations

import pytest

from app.domain.value_objects.enums import BehaviorType
from app.domain.value_objects.perception import (
    PERSON_LABEL,
    BoundingBox,
    Detection,
    Perception,
)
from app.domain.value_objects.robot_context import RobotContext
from app.domain.value_objects.speech import Transcript
from app.infrastructure.planner.rule_planner import RulePlanner

pytestmark = pytest.mark.asyncio


def make_planner() -> RulePlanner:
    return RulePlanner(battery_critical_pct=12.0, battery_low_pct=25.0)


def person_perception() -> Perception:
    det = Detection(PERSON_LABEL, 0.9, BoundingBox(0.4, 0.3, 0.2, 0.4))
    return Perception(detections=(det,), frame_width=100, frame_height=100)


async def test_critical_battery_forces_stop():
    plan = await make_planner().plan(
        RobotContext(robot_id="r1", battery=5.0, current_behavior=BehaviorType.FOLLOW)
    )
    assert plan.behavior is BehaviorType.STOP
    assert plan.reason == "battery_critical"


async def test_voice_command_maps_to_behavior():
    ctx = RobotContext(
        robot_id="r1",
        transcript=Transcript(text="please follow me", confidence=0.9),
        battery=90.0,
    )
    plan = await make_planner().plan(ctx)
    assert plan.behavior is BehaviorType.FOLLOW
    assert plan.reason == "voice_command"


async def test_voice_command_overrides_low_relevant_perception():
    ctx = RobotContext(
        robot_id="r1",
        transcript=Transcript(text="dừng lại", confidence=0.9),  # Vietnamese "stop"
        perception=person_perception(),
        battery=90.0,
        current_behavior=BehaviorType.FOLLOW,
    )
    plan = await make_planner().plan(ctx)
    assert plan.behavior is BehaviorType.STOP


async def test_follow_continuity_searches_when_person_lost():
    ctx = RobotContext(
        robot_id="r1",
        perception=Perception.empty(),
        battery=90.0,
        current_behavior=BehaviorType.FOLLOW,
    )
    plan = await make_planner().plan(ctx)
    assert plan.behavior is BehaviorType.SEARCH
    assert plan.reason == "person_lost"


async def test_search_acquires_person_and_follows():
    ctx = RobotContext(
        robot_id="r1",
        perception=person_perception(),
        battery=90.0,
        current_behavior=BehaviorType.SEARCH,
    )
    plan = await make_planner().plan(ctx)
    assert plan.behavior is BehaviorType.FOLLOW
    assert plan.reason == "person_acquired"


async def test_stop_is_sticky_without_command():
    ctx = RobotContext(robot_id="r1", battery=90.0, current_behavior=BehaviorType.STOP)
    plan = await make_planner().plan(ctx)
    assert plan.behavior is BehaviorType.STOP


async def test_default_is_idle():
    ctx = RobotContext(robot_id="r1", battery=90.0, current_behavior=BehaviorType.IDLE)
    plan = await make_planner().plan(ctx)
    assert plan.behavior is BehaviorType.IDLE
