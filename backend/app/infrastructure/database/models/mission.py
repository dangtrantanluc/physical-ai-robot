"""Mission and Task ORM models."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin


class MissionModel(TimestampMixin, Base):
    """``missions`` table."""

    __tablename__ = "missions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    robot_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("robots.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    goal: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", index=True)
    params: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tasks: Mapped[list[TaskModel]] = relationship(
        back_populates="mission",
        cascade="all, delete-orphan",
        order_by="TaskModel.order_index",
    )


class TaskModel(TimestampMixin, Base):
    """``tasks`` table — ordered steps of a mission."""

    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    mission_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("missions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    params: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    mission: Mapped[MissionModel] = relationship(back_populates="tasks")
