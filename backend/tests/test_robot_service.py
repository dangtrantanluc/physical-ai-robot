"""Integration-style test of RobotService.step using in-memory fakes.

Exercises the full control loop (perceive -> plan -> switch -> execute -> persist)
with real vision/speech/planner/behavior components but faked persistence.
"""

from __future__ import annotations

import base64

import pytest

from app.application.dto.step import StepCommand
from app.application.services.memory_service import MemoryService
from app.application.services.planner_service import PlannerService
from app.application.services.robot_service import RobotService
from app.application.services.speech_service import SpeechService
from app.application.services.vision_service import VisionService
from app.domain.value_objects.enums import BehaviorType
from app.infrastructure.behaviors.registry import build_behavior_manager
from app.infrastructure.planner.rule_planner import RulePlanner
from app.infrastructure.speech.mock_recognizer import MockRecognizer
from app.infrastructure.vision.mock_detector import MockDetector

pytestmark = pytest.mark.asyncio


def command_audio(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


@pytest.fixture
def robot_service(settings, state_store, robot_repo, log_repo, memory_repo) -> RobotService:
    return RobotService(
        vision=VisionService(MockDetector()),
        speech=SpeechService(MockRecognizer()),
        planner=PlannerService(
            RulePlanner(
                battery_critical_pct=settings.battery.critical_pct,
                battery_low_pct=settings.battery.low_pct,
            )
        ),
        behavior_manager=build_behavior_manager(settings),
        state_store=state_store,
        robots=robot_repo,
        logs=log_repo,
        settings=settings,
        memory=MemoryService(memory_repo),
    )


async def test_follow_command_drives_follow_behavior(
    robot_service, person_image_b64, state_store, robot_repo, log_repo, memory_repo
):
    result = await robot_service.step(
        StepCommand(
            robot_id="robot-1",
            image_b64=person_image_b64,
            audio_b64=command_audio("follow me"),
            battery=88.0,
            correlation_id="corr-1",
        )
    )

    assert result.behavior is BehaviorType.FOLLOW
    assert result.metadata["reason"] == "voice_command"
    assert "fps" in result.metadata

    # Hot state persisted.
    snapshot = await state_store.get("robot-1")
    assert snapshot.current_behavior is BehaviorType.FOLLOW
    assert snapshot.step_count == 1

    # Durable telemetry + robot registration + voice memory persisted.
    assert len(log_repo.entries) == 1
    assert log_repo.entries[0].correlation_id == "corr-1"
    assert robot_repo.robots["robot-1"].current_behavior is BehaviorType.FOLLOW
    assert len(memory_repo.records) == 1
    assert memory_repo.records[0].kind == "interaction"


async def test_critical_battery_forces_stop(robot_service, person_image_b64):
    result = await robot_service.step(
        StepCommand(robot_id="robot-2", image_b64=person_image_b64, battery=3.0)
    )
    assert result.behavior is BehaviorType.STOP
    assert result.linear_velocity == 0.0
    assert result.speech is not None


async def test_step_survives_empty_payload(robot_service):
    result = await robot_service.step(StepCommand(robot_id="robot-3"))
    assert result.behavior is BehaviorType.IDLE
    assert result.linear_velocity == 0.0


async def test_log_sampling_skips_durable_writes(
    settings, state_store, robot_repo, log_repo, memory_repo, person_image_b64
):
    settings.log_sample_n = 5  # persist only every 5th step
    service = RobotService(
        vision=VisionService(MockDetector()),
        speech=SpeechService(MockRecognizer()),
        planner=PlannerService(
            RulePlanner(battery_critical_pct=12.0, battery_low_pct=25.0)
        ),
        behavior_manager=build_behavior_manager(settings),
        state_store=state_store,
        robots=robot_repo,
        logs=log_repo,
        settings=settings,
        memory=MemoryService(memory_repo),
    )
    for _ in range(4):
        await service.step(StepCommand(robot_id="r", image_b64=person_image_b64, battery=90.0))
    assert log_repo.entries == []  # nothing durable yet (steps 1-4)
    await service.step(StepCommand(robot_id="r", image_b64=person_image_b64, battery=90.0))
    assert len(log_repo.entries) == 1  # step 5 persisted
