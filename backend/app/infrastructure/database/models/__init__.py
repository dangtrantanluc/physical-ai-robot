"""ORM models.

Importing this package registers every model on ``Base.metadata`` — Alembic's
``env.py`` imports it so autogenerate sees the full schema.
"""

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.log import LogModel
from app.infrastructure.database.models.memory import MemoryModel
from app.infrastructure.database.models.mission import MissionModel, TaskModel
from app.infrastructure.database.models.robot import RobotModel
from app.infrastructure.database.models.setting import SettingModel

__all__ = [
    "Base",
    "RobotModel",
    "MissionModel",
    "TaskModel",
    "LogModel",
    "SettingModel",
    "MemoryModel",
]
