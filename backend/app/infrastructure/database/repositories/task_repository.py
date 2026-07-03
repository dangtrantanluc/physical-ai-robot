"""SQLAlchemy TaskRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.mission import Task
from app.domain.interfaces.repositories import TaskRepository
from app.infrastructure.database.mappers import task_to_entity, task_to_model
from app.infrastructure.database.models.mission import TaskModel


class SqlTaskRepository(TaskRepository):
    """Persists mission tasks in PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_many(self, tasks: list[Task]) -> list[Task]:
        models = [task_to_model(t) for t in tasks]
        self._session.add_all(models)
        await self._session.flush()
        return [task_to_entity(m) for m in models]

    async def list_for_mission(self, mission_id: UUID) -> list[Task]:
        stmt = (
            select(TaskModel)
            .where(TaskModel.mission_id == mission_id)
            .order_by(TaskModel.order_index)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [task_to_entity(t) for t in rows]
