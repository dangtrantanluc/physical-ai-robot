"""SQLAlchemy LogRepository (append-only telemetry sink)."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces.repositories import LogEntry, LogRepository
from app.infrastructure.database.models.log import LogModel


class SqlLogRepository(LogRepository):
    """Writes control-loop telemetry rows to PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entry: LogEntry) -> None:
        self._session.add(
            LogModel(
                robot_id=entry.robot_id,
                correlation_id=entry.correlation_id,
                behavior=entry.behavior,
                linear_velocity=entry.linear_velocity,
                angular_velocity=entry.angular_velocity,
                speech=entry.speech,
                transcript=entry.transcript,
                detections=entry.detections,
                battery=entry.battery,
                latency_ms=entry.latency_ms,
                inference_ms=entry.inference_ms,
                api_ms=entry.api_ms,
                fps=entry.fps,
                meta=entry.metadata,
            )
        )
        await self._session.flush()
