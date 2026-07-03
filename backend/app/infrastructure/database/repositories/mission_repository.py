"""SQLAlchemy MissionRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.mission import Mission
from app.domain.interfaces.repositories import MissionRepository
from app.domain.value_objects.enums import MissionStatus
from app.infrastructure.database.mappers import mission_to_entity, mission_to_model
from app.infrastructure.database.models.mission import MissionModel


class SqlMissionRepository(MissionRepository):
    """Persists missions (with their tasks) in PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, mission: Mission) -> Mission:
        model = mission_to_model(mission)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model, attribute_names=["tasks"])
        return mission_to_entity(model)

    async def get(self, mission_id: UUID) -> Mission | None:
        stmt = (
            select(MissionModel)
            .where(MissionModel.id == mission_id)
            .options(selectinload(MissionModel.tasks))
        )
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        return mission_to_entity(model) if model else None

    async def list_for_robot(self, robot_id: str, *, limit: int = 50) -> list[Mission]:
        stmt = (
            select(MissionModel)
            .where(MissionModel.robot_id == robot_id)
            .options(selectinload(MissionModel.tasks))
            .order_by(MissionModel.created_at.desc())
            .limit(limit)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [mission_to_entity(m) for m in rows]

    async def set_status(self, mission_id: UUID, status: MissionStatus) -> Mission | None:
        stmt = (
            select(MissionModel)
            .where(MissionModel.id == mission_id)
            .options(selectinload(MissionModel.tasks))
        )
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        if model is None:
            return None
        model.status = status.value
        await self._session.flush()
        return mission_to_entity(model)
