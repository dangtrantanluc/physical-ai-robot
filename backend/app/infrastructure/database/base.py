"""SQLAlchemy declarative base + shared mixins.

A deterministic constraint naming convention is set so Alembic autogenerate
produces stable, predictable migration names.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class TimestampMixin:
    """Adds server-managed ``created_at`` / ``updated_at`` columns.

    ``eager_defaults`` makes SQLAlchemy fetch server-side default/onupdate values via
    RETURNING in the same INSERT/UPDATE statement. Without it, an UPDATE expires the
    ``onupdate`` column and reading it back triggers a lazy SELECT — which fails on an
    async session (``MissingGreenlet``). This folds that read into the write, so no
    extra round-trip.
    """

    __mapper_args__ = {"eager_defaults": True}

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
