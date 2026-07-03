"""Mission and Task schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    order_index: int = 0
    params: dict = Field(default_factory=dict)


class MissionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, examples=["Patrol warehouse"])
    goal: str = Field("", max_length=2000)
    robot_id: str | None = Field(None, max_length=64)
    params: dict = Field(default_factory=dict)
    tasks: list[TaskCreate] = Field(default_factory=list)


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    order_index: int
    status: str
    params: dict


class MissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    robot_id: str | None
    name: str
    goal: str
    status: str
    params: dict
    tasks: list[TaskRead]
    created_at: datetime | None
    updated_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
