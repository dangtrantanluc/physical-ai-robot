"""MemoryService — record and recall robot memories.

Wraps the :class:`MemoryRepository` port. Used by the control loop to record notable
interactions (e.g. voice commands) and available for future recall-augmented
planning without any planner changes.
"""

from __future__ import annotations

from app.domain.entities.memory import MemoryRecord
from app.domain.interfaces.memory import MemoryRepository


class MemoryService:
    """Stores and searches robot memories."""

    def __init__(self, repository: MemoryRepository) -> None:
        self._repository = repository

    async def remember(
        self,
        robot_id: str,
        content: str,
        *,
        kind: str = "observation",
        metadata: dict | None = None,
    ) -> MemoryRecord:
        record = MemoryRecord(
            robot_id=robot_id,
            content=content,
            kind=kind,
            metadata=metadata or {},
        )
        return await self._repository.save(record)

    async def recall(
        self,
        robot_id: str,
        query: str,
        *,
        limit: int = 10,
    ) -> list[MemoryRecord]:
        return await self._repository.search(robot_id, query, limit=limit)
