"""Runtime settings ORM model (key/value overrides persisted in DB)."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin


class SettingModel(TimestampMixin, Base):
    """``settings`` table — operator-tunable values without a redeploy."""

    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
