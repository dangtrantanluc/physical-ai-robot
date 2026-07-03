"""PostgreSQL-backed MemoryRepository.

Uses a case-insensitive text match (ILIKE) over the most recent records. This is
deliberately simple: the port's contract is "return relevant records", and a later
ChromaDB/Qdrant implementation will satisfy the same contract with vector search —
without any change to the planner that consumes it.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.memory import MemoryRecord
from app.domain.interfaces.memory import MemoryRepository
from app.infrastructure.database.mappers import memory_to_entity, memory_to_model
from app.infrastructure.database.models.memory import MemoryModel


class PostgresMemoryRepository(MemoryRepository):
    """Stores robot memories in the ``memories`` table."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, record: MemoryRecord) -> MemoryRecord:
        model = memory_to_model(record)
        self._session.add(model)
        await self._session.flush()
        return memory_to_entity(model)

    async def search(
        self,
        robot_id: str,
        query: str,
        *,
        limit: int = 10,
    ) -> list[MemoryRecord]:
        stmt = select(MemoryModel).where(MemoryModel.robot_id == robot_id)
        if query.strip():
            stmt = stmt.where(MemoryModel.content.ilike(f"%{query.strip()}%"))
        stmt = stmt.order_by(MemoryModel.created_at.desc()).limit(limit)
        rows = (await self._session.execute(stmt)).scalars().all()
        return [memory_to_entity(m) for m in rows]
