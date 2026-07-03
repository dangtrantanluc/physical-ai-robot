"""Memory port.

Backed by PostgreSQL today, ChromaDB/Qdrant later. The planner depends only on
this interface, so swapping the store never touches planning logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.memory import MemoryRecord


class MemoryRepository(ABC):
    """Stores and retrieves :class:`MemoryRecord` items."""

    @abstractmethod
    async def save(self, record: MemoryRecord) -> MemoryRecord:
        """Persist ``record`` and return it (with any store-assigned fields)."""
        raise NotImplementedError

    @abstractmethod
    async def search(
        self,
        robot_id: str,
        query: str,
        *,
        limit: int = 10,
    ) -> list[MemoryRecord]:
        """Return up to ``limit`` records for ``robot_id`` relevant to ``query``.

        The PostgreSQL backend uses a text match; a vector backend will use
        embedding similarity — the signature is identical.
        """
        raise NotImplementedError
