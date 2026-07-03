"""FastAPI dependency providers — the request-scoped DI wiring.

Process-wide singletons come from the :class:`Container` on ``app.state``;
per-request objects (DB session, session-bound repositories, RobotService) are built
here via ``Depends`` so each request is its own unit of work. No manual singletons.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.memory_service import MemoryService
from app.application.services.mission_service import MissionService
from app.application.services.planner_service import PlannerService
from app.application.services.robot_service import RobotService
from app.application.services.speech_service import SpeechService
from app.application.services.vision_service import VisionService
from app.core.config import Settings
from app.core.container import Container
from app.domain.interfaces.behavior import BehaviorManager
from app.domain.interfaces.memory import MemoryRepository
from app.domain.interfaces.state_store import RobotStateStore
from app.infrastructure.database.repositories import (
    SqlLogRepository,
    SqlMissionRepository,
    SqlRobotRepository,
)
from app.infrastructure.memory.postgres_memory_repository import PostgresMemoryRepository


def get_container(request: Request) -> Container:
    """Return the process-wide container attached at startup."""
    return request.app.state.container


def get_settings(container: Annotated[Container, Depends(get_container)]) -> Settings:
    return container.settings


async def get_session(
    container: Annotated[Container, Depends(get_container)],
) -> AsyncIterator[AsyncSession]:
    """Yield a request-scoped session; commit on success, rollback on error."""
    async with container.session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


SessionDep = Annotated[AsyncSession, Depends(get_session)]
ContainerDep = Annotated[Container, Depends(get_container)]


# ---- Singletons from the container ----------------------------------------


def get_state_store(container: ContainerDep) -> RobotStateStore:
    return container.state_store


def get_behavior_manager(container: ContainerDep) -> BehaviorManager:
    return container.behavior_manager


def get_vision_service(container: ContainerDep) -> VisionService:
    return container.vision_service


def get_speech_service(container: ContainerDep) -> SpeechService:
    return container.speech_service


def get_planner_service(container: ContainerDep) -> PlannerService:
    return container.planner_service


# ---- Request-scoped repositories & services -------------------------------


def get_memory_repository(session: SessionDep, container: ContainerDep) -> MemoryRepository:
    # Only the Postgres backend exists today; the string selects future backends.
    return PostgresMemoryRepository(session)


def get_memory_service(
    repo: Annotated[MemoryRepository, Depends(get_memory_repository)],
) -> MemoryService:
    return MemoryService(repo)


def get_mission_service(session: SessionDep) -> MissionService:
    return MissionService(SqlMissionRepository(session))


def build_robot_service(session: AsyncSession, container: Container) -> RobotService:
    """Assemble a RobotService from a session + container.

    Plain function (no ``Depends``) so both the HTTP dependency and the WebSocket
    route — which manages its own per-message session — can share one assembly path.
    """
    return RobotService(
        vision=container.vision_service,
        speech=container.speech_service,
        planner=container.planner_service,
        behavior_manager=container.behavior_manager,
        state_store=container.state_store,
        robots=SqlRobotRepository(session),
        logs=SqlLogRepository(session),
        settings=container.settings,
        memory=MemoryService(PostgresMemoryRepository(session)),
    )


def get_robot_service(session: SessionDep, container: ContainerDep) -> RobotService:
    """Assemble a RobotService for this request (session-bound repos + singletons)."""
    return build_robot_service(session, container)


# ---- Auth (future-ready, permissive when no keys configured) --------------


async def require_api_key(
    container: ContainerDep,
    x_api_key: Annotated[str | None, Header()] = None,
) -> None:
    """Enforce an API key only when ``API_KEYS`` is configured; else no-op."""
    settings = container.settings
    if not settings.auth_enabled:
        return
    if x_api_key not in settings.api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
