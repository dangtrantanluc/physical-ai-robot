"""initial schema: robots, missions, tasks, logs, settings, memories

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-03

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    now = sa.text("now()")
    empty_jsonb = sa.text("'{}'::jsonb")

    op.create_table(
        "robots",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="online"),
        sa.Column("battery", sa.Float(), nullable=True),
        sa.Column(
            "current_behavior", sa.String(length=32), nullable=False, server_default="idle"
        ),
        sa.Column("current_mission_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_robots"),
    )

    op.create_table(
        "missions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("robot_id", sa.String(length=64), nullable=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("goal", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column(
            "params",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=empty_jsonb,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["robot_id"],
            ["robots.id"],
            name="fk_missions_robot_id_robots",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_missions"),
    )
    op.create_index("ix_missions_robot_id", "missions", ["robot_id"])
    op.create_index("ix_missions_status", "missions", ["status"])

    op.create_table(
        "tasks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("mission_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column(
            "params",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=empty_jsonb,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
        sa.ForeignKeyConstraint(
            ["mission_id"],
            ["missions.id"],
            name="fk_tasks_mission_id_missions",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_tasks"),
    )
    op.create_index("ix_tasks_mission_id", "tasks", ["mission_id"])

    op.create_table(
        "logs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("robot_id", sa.String(length=64), nullable=False),
        sa.Column("correlation_id", sa.String(length=64), nullable=True),
        sa.Column("behavior", sa.String(length=32), nullable=False),
        sa.Column("linear_velocity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("angular_velocity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("speech", sa.Text(), nullable=True),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("detections", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("battery", sa.Float(), nullable=True),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("inference_ms", sa.Float(), nullable=True),
        sa.Column("api_ms", sa.Float(), nullable=True),
        sa.Column("fps", sa.Float(), nullable=True),
        sa.Column(
            "meta",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=empty_jsonb,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
        sa.PrimaryKeyConstraint("id", name="pk_logs"),
    )
    op.create_index("ix_logs_robot_id_created_at", "logs", ["robot_id", "created_at"])

    op.create_table(
        "settings",
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column(
            "value",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=empty_jsonb,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
        sa.PrimaryKeyConstraint("key", name="pk_settings"),
    )

    op.create_table(
        "memories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("robot_id", sa.String(length=64), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False, server_default="observation"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "meta",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=empty_jsonb,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=now),
        sa.PrimaryKeyConstraint("id", name="pk_memories"),
    )
    op.create_index("ix_memories_robot_id", "memories", ["robot_id"])
    op.create_index("ix_memories_created_at", "memories", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_memories_created_at", table_name="memories")
    op.drop_index("ix_memories_robot_id", table_name="memories")
    op.drop_table("memories")

    op.drop_table("settings")

    op.drop_index("ix_logs_robot_id_created_at", table_name="logs")
    op.drop_table("logs")

    op.drop_index("ix_tasks_mission_id", table_name="tasks")
    op.drop_table("tasks")

    op.drop_index("ix_missions_status", table_name="missions")
    op.drop_index("ix_missions_robot_id", table_name="missions")
    op.drop_table("missions")

    op.drop_table("robots")
