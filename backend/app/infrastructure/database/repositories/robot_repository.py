"""SQLAlchemy RobotRepository."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.robot import Robot
from app.domain.interfaces.repositories import RobotRepository
from app.domain.value_objects.enums import BehaviorType
from app.infrastructure.database.mappers import robot_to_entity
from app.infrastructure.database.models.robot import RobotModel


class SqlRobotRepository(RobotRepository):
    """Persists robots in PostgreSQL. One instance per unit of work (session)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, robot_id: str) -> Robot | None:
        model = await self._session.get(RobotModel, robot_id)
        return robot_to_entity(model) if model else None

    async def get_or_create(self, robot_id: str, *, name: str | None = None) -> Robot:
        model = await self._session.get(RobotModel, robot_id)
        if model is None:
            model = RobotModel(id=robot_id, name=name or robot_id)
            self._session.add(model)
            await self._session.flush()
        return robot_to_entity(model)

    async def save_observation(
        self,
        robot_id: str,
        *,
        behavior: BehaviorType,
        battery: float | None,
        mission_id: str | None,
        seen_at: datetime,
    ) -> Robot:
        model = await self._session.get(RobotModel, robot_id)
        if model is None:
            model = RobotModel(id=robot_id, name=robot_id)
            self._session.add(model)

        model.current_behavior = behavior.value
        if battery is not None:
            model.battery = battery
        model.current_mission_id = mission_id
        model.last_seen_at = seen_at
        model.status = "online"
        await self._session.flush()
        return robot_to_entity(model)

    async def list_all(self, *, limit: int = 100) -> list[Robot]:
        stmt = select(RobotModel).order_by(RobotModel.last_seen_at.desc()).limit(limit)
        rows = (await self._session.execute(stmt)).scalars().all()
        return [robot_to_entity(r) for r in rows]
