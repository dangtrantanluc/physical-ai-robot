"""Translation between ORM models and domain entities.

Repositories return domain entities, never ORM rows, so the domain/application
layers never import SQLAlchemy. All conversion lives here in one place.
"""

from __future__ import annotations

from app.domain.entities.memory import MemoryRecord
from app.domain.entities.mission import Mission, Task
from app.domain.entities.robot import Robot
from app.domain.value_objects.enums import BehaviorType, MissionStatus, TaskStatus
from app.infrastructure.database.models.memory import MemoryModel
from app.infrastructure.database.models.mission import MissionModel, TaskModel
from app.infrastructure.database.models.robot import RobotModel


def robot_to_entity(model: RobotModel) -> Robot:
    return Robot(
        id=model.id,
        name=model.name,
        status=model.status,
        battery=model.battery,
        current_behavior=BehaviorType(model.current_behavior),
        current_mission_id=model.current_mission_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
        last_seen_at=model.last_seen_at,
    )


def task_to_entity(model: TaskModel) -> Task:
    return Task(
        id=model.id,
        mission_id=model.mission_id,
        name=model.name,
        order_index=model.order_index,
        status=TaskStatus(model.status),
        params=dict(model.params or {}),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def mission_to_entity(model: MissionModel, *, with_tasks: bool = True) -> Mission:
    return Mission(
        id=model.id,
        robot_id=model.robot_id,
        name=model.name,
        goal=model.goal,
        status=MissionStatus(model.status),
        params=dict(model.params or {}),
        tasks=[task_to_entity(t) for t in model.tasks] if with_tasks else [],
        created_at=model.created_at,
        updated_at=model.updated_at,
        started_at=model.started_at,
        completed_at=model.completed_at,
    )


def task_to_model(entity: Task) -> TaskModel:
    return TaskModel(
        id=entity.id,
        mission_id=entity.mission_id,
        name=entity.name,
        order_index=entity.order_index,
        status=entity.status.value,
        params=entity.params,
    )


def mission_to_model(entity: Mission) -> MissionModel:
    return MissionModel(
        id=entity.id,
        robot_id=entity.robot_id,
        name=entity.name,
        goal=entity.goal,
        status=entity.status.value,
        params=entity.params,
        tasks=[task_to_model(t) for t in entity.tasks],
    )


def memory_to_entity(model: MemoryModel) -> MemoryRecord:
    return MemoryRecord(
        id=model.id,
        robot_id=model.robot_id,
        kind=model.kind,
        content=model.content,
        embedding=model.embedding,
        metadata=dict(model.meta or {}),
        created_at=model.created_at,
    )


def memory_to_model(entity: MemoryRecord) -> MemoryModel:
    return MemoryModel(
        id=entity.id,
        robot_id=entity.robot_id,
        kind=entity.kind,
        content=entity.content,
        embedding=entity.embedding,
        meta=entity.metadata,
    )
