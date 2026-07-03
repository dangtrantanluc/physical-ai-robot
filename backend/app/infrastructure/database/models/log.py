"""Control-loop telemetry ORM model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class LogModel(Base):
    """``logs`` table — one row per persisted control tick (sampled).

    Write-heavy and append-only; indexed by ``(robot_id, created_at)`` for
    time-series queries.
    """

    __tablename__ = "logs"
    __table_args__ = (Index("ix_logs_robot_id_created_at", "robot_id", "created_at"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    robot_id: Mapped[str] = mapped_column(String(64), nullable=False)
    correlation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    behavior: Mapped[str] = mapped_column(String(32), nullable=False)
    linear_velocity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    angular_velocity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    speech: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    detections: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    battery: Mapped[float | None] = mapped_column(Float, nullable=True)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    inference_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    api_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    fps: Mapped[float | None] = mapped_column(Float, nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
