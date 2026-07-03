"""Robot ORM model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin


class RobotModel(TimestampMixin, Base):
    """``robots`` table. Identity is the device-provided id (e.g. ``realme-q-01``)."""

    __tablename__ = "robots"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="online")
    battery: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_behavior: Mapped[str] = mapped_column(String(32), nullable=False, default="idle")
    current_mission_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
