"""MemoryRecord entity — a single remembered fact/event.

The initial backend stores these in PostgreSQL with a text query. The optional
``embedding`` field is modelled now so the exact same entity can later be persisted
to ChromaDB/Qdrant for semantic search — without changing the planner or the
:class:`~app.domain.interfaces.memory.MemoryRepository` port.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass(slots=True)
class MemoryRecord:
    """Something the robot should remember."""

    robot_id: str
    content: str
    kind: str = "observation"  # observation | event | fact | interaction
    metadata: dict = field(default_factory=dict)
    embedding: list[float] | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime | None = None
