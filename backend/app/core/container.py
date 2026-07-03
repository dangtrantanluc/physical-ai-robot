"""Composition root — the Dependency Injection container.

Builds and owns the process-wide singletons (engine, Redis, AI models, behavior
manager, stateless services) from configuration. This is the ONE place that knows
which concrete implementation backs each domain port; swapping an implementation is
a config change (``VISION_DETECTOR``, ``PLANNER``, ...), not a code change.

Per-request objects (DB session, session-bound repositories, RobotService) are NOT
built here — they are assembled in ``app/api/deps.py`` using ``Depends`` so each
request gets its own unit of work. No manual global singletons; the container is
attached to ``app.state`` and injected via ``Depends(get_container)``.
"""

from __future__ import annotations

from dataclasses import dataclass

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.application.services.planner_service import PlannerService
from app.application.services.speech_service import SpeechService
from app.application.services.vision_service import VisionService
from app.core.config import Settings
from app.core.logging import get_logger
from app.domain.interfaces.behavior import BehaviorManager
from app.domain.interfaces.planner import Planner
from app.domain.interfaces.speech import SpeechRecognizer
from app.domain.interfaces.state_store import RobotStateStore
from app.domain.interfaces.vision import VisionDetector
from app.infrastructure.behaviors.registry import build_behavior_manager
from app.infrastructure.database.session import create_engine, create_session_factory
from app.infrastructure.planner.rule_planner import RulePlanner
from app.infrastructure.redis.client import create_redis
from app.infrastructure.redis.state_store import RedisRobotStateStore
from app.infrastructure.speech.mock_recognizer import MockRecognizer
from app.infrastructure.vision.mock_detector import MockDetector

logger = get_logger(__name__)


# ---- Port factories (config-string -> implementation) ----------------------


def _build_detector(settings: Settings) -> VisionDetector:
    name = settings.vision_detector.lower()
    if name == "mock":
        return MockDetector()
    if name == "yolo":
        from app.infrastructure.vision.yolo_detector import YoloDetector

        return YoloDetector(
            settings.yolo.model_path,
            confidence=settings.yolo.confidence,
            device=settings.yolo.device,
        )
    # rtdetr / grounding_dino: same VisionDetector port, not implemented yet.
    logger.warning("unknown_detector_fallback_mock", requested=name)
    return MockDetector()


def _build_recognizer(settings: Settings) -> SpeechRecognizer:
    name = settings.speech_recognizer.lower()
    if name == "mock":
        return MockRecognizer()
    # Whisper and friends land here later; keep the app bootable meanwhile.
    logger.warning("unknown_recognizer_fallback_mock", requested=name)
    return MockRecognizer()


def _build_rule_planner(settings: Settings) -> RulePlanner:
    return RulePlanner(
        battery_critical_pct=settings.battery.critical_pct,
        battery_low_pct=settings.battery.low_pct,
    )


def _build_planner(settings: Settings) -> Planner:
    name = settings.planner.lower()
    if name == "rule":
        return _build_rule_planner(settings)
    if name == "llm":
        from app.infrastructure.planner.llm_planner import LLMPlanner

        return LLMPlanner(
            base_url=settings.llm.base_url,
            api_key=settings.llm.api_key,
            model=settings.llm.model,
            fallback=_build_rule_planner(settings),  # deterministic safety net
            battery_critical_pct=settings.battery.critical_pct,
            temperature=settings.llm.temperature,
            timeout_s=settings.llm.timeout_s,
            max_tokens=settings.llm.max_tokens,
            json_mode=settings.llm.json_mode,
        )
    logger.warning("unknown_planner_fallback_rule", requested=name)
    return _build_rule_planner(settings)


@dataclass(slots=True)
class Container:
    """Holds process-wide singletons and stateless services."""

    settings: Settings
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    redis: Redis
    state_store: RobotStateStore
    detector: VisionDetector
    recognizer: SpeechRecognizer
    planner: Planner
    behavior_manager: BehaviorManager
    vision_service: VisionService
    speech_service: SpeechService
    planner_service: PlannerService

    @classmethod
    async def create(cls, settings: Settings) -> Container:
        """Assemble the container. Called once, from the app lifespan."""
        engine = create_engine(settings)
        session_factory = create_session_factory(engine)
        redis = create_redis(settings)

        detector = _build_detector(settings)
        recognizer = _build_recognizer(settings)
        planner = _build_planner(settings)

        # Pre-load heavy models (no-op for mocks) so the first request isn't slow.
        await detector.warmup()
        await recognizer.warmup()

        container = cls(
            settings=settings,
            engine=engine,
            session_factory=session_factory,
            redis=redis,
            state_store=RedisRobotStateStore(redis),
            detector=detector,
            recognizer=recognizer,
            planner=planner,
            behavior_manager=build_behavior_manager(settings),
            vision_service=VisionService(detector),
            speech_service=SpeechService(recognizer),
            planner_service=PlannerService(planner),
        )
        logger.info(
            "container_ready",
            detector=settings.vision_detector,
            recognizer=settings.speech_recognizer,
            planner=settings.planner,
            memory_backend=settings.memory_backend,
        )
        return container

    async def shutdown(self) -> None:
        """Release external resources. Called from the app lifespan on shutdown."""
        # Close the planner's HTTP client if it holds one (e.g. LLMPlanner).
        aclose = getattr(self.planner, "aclose", None)
        if callable(aclose):
            await aclose()
        await self.redis.aclose()
        await self.engine.dispose()
        logger.info("container_shutdown")
