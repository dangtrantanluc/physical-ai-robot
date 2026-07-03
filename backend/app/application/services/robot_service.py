"""RobotService — orchestrates one control-loop tick (the /robot/step use case).

This is the heart of the "Robot Brain". For each tick it:

  1. loads the robot's hot state (Redis),
  2. perceives (vision) and listens (speech) concurrently,
  3. asks the planner which behavior should be active,
  4. switches to and executes that behavior (producing a velocity command),
  5. persists state (Redis) and sampled telemetry (Postgres),
  6. returns exactly the flat command the robot understands.

It depends only on ports/services injected via the constructor, so every collaborator
(detector, recognizer, planner, repositories) can be faked in unit tests.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from app.application.dto.step import StepCommand, StepResult
from app.application.services.memory_service import MemoryService
from app.application.services.planner_service import PlannerService
from app.application.services.speech_service import SpeechService
from app.application.services.vision_service import VisionService
from app.core.config import Settings
from app.core.logging import get_logger
from app.domain.interfaces.behavior import BehaviorManager
from app.domain.interfaces.repositories import LogEntry, LogRepository, RobotRepository
from app.domain.interfaces.state_store import RobotStateStore
from app.domain.value_objects.robot_context import RobotContext
from app.utils.timing import Stopwatch, fps_from_ms

logger = get_logger(__name__)


class RobotService:
    """Executes the perception → planning → behavior control loop."""

    def __init__(
        self,
        *,
        vision: VisionService,
        speech: SpeechService,
        planner: PlannerService,
        behavior_manager: BehaviorManager,
        state_store: RobotStateStore,
        robots: RobotRepository,
        logs: LogRepository,
        settings: Settings,
        memory: MemoryService | None = None,
    ) -> None:
        self._vision = vision
        self._speech = speech
        self._planner = planner
        self._behaviors = behavior_manager
        self._state = state_store
        self._robots = robots
        self._logs = logs
        self._settings = settings
        self._memory = memory

    async def step(self, command: StepCommand) -> StepResult:
        """Run one control tick and return the actuation command."""
        total = Stopwatch()
        with total:
            snapshot = await self._state.get(command.robot_id)

            # Perceive + listen concurrently (both are independent I/O/CPU tasks).
            inference = Stopwatch()
            with inference:
                perception, transcript = await asyncio.gather(
                    self._vision.perceive(command.image_b64),
                    self._speech.listen(command.audio_b64),
                )

            context = RobotContext(
                robot_id=command.robot_id,
                perception=perception,
                transcript=transcript,
                battery=command.battery if command.battery is not None else snapshot.battery,
                reported_state=command.reported_state,
                current_behavior=snapshot.current_behavior,
                mission_id=snapshot.mission_id,
                correlation_id=command.correlation_id,
            )

            plan = await self._planner.decide(context)
            behavior = self._behaviors.switch_behavior(
                snapshot.current_behavior, plan.behavior, context
            )
            output = await self._behaviors.execute(behavior, context)

            speech = plan.speech or output.speech
            now = datetime.now(UTC)

            await self._persist(command, snapshot, context, plan, output, speech, now)

        latency_ms = total.elapsed_ms
        fps = fps_from_ms(latency_ms)
        logger.info(
            "robot_step",
            robot_id=command.robot_id,
            behavior=plan.behavior.value,
            reason=plan.reason,
            detections=len(perception.detections),
            linear=round(output.velocity.linear, 4),
            angular=round(output.velocity.angular, 4),
            latency_ms=round(latency_ms, 2),
            inference_ms=round(inference.elapsed_ms, 2),
            fps=round(fps, 2),
            correlation_id=command.correlation_id,
        )

        metadata = {
            "reason": plan.reason,
            "detections": perception.summary(),
            "inference_ms": round(inference.elapsed_ms, 2),
            "latency_ms": round(latency_ms, 2),
            "fps": round(fps, 2),
            "target_fps": self._settings.robot_fps,
            **output.metadata,
        }
        return StepResult(
            behavior=plan.behavior,
            linear_velocity=output.velocity.linear,
            angular_velocity=output.velocity.angular,
            speech=speech,
            metadata=metadata,
        )

    async def _persist(
        self,
        command: StepCommand,
        snapshot,
        context: RobotContext,
        plan,
        output,
        speech: str | None,
        now: datetime,
    ) -> None:
        """Write hot state (always) + sampled durable telemetry (Postgres)."""
        # Hot state — always updated, cheap.
        snapshot.current_behavior = plan.behavior
        snapshot.mission_id = context.mission_id
        snapshot.battery = context.battery
        snapshot.step_count += 1
        snapshot.last_frame = {
            "detections": context.perception.summary(),
            "at": now.isoformat(),
        }
        await self._state.set(snapshot)

        if not self._settings.persist_logs:
            return
        # Sample durable writes to keep the hot loop off the DB at high FPS.
        if snapshot.step_count % self._settings.log_sample_n != 0:
            return

        await self._robots.save_observation(
            command.robot_id,
            behavior=plan.behavior,
            battery=context.battery,
            mission_id=context.mission_id,
            seen_at=now,
        )
        await self._logs.add(
            LogEntry(
                robot_id=command.robot_id,
                correlation_id=command.correlation_id,
                behavior=plan.behavior.value,
                linear_velocity=output.velocity.linear,
                angular_velocity=output.velocity.angular,
                speech=speech,
                transcript=context.transcript.text or None,
                detections=len(context.perception.detections),
                battery=context.battery,
                metadata={"reason": plan.reason},
            )
        )

        # Record voice interactions as memories (infrequent → negligible cost).
        if self._memory is not None and context.has_voice_command:
            await self._memory.remember(
                command.robot_id,
                context.transcript.text,
                kind="interaction",
                metadata={"behavior": plan.behavior.value, "reason": plan.reason},
            )
