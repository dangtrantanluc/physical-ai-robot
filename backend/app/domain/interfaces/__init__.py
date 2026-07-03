"""Domain ports — abstract interfaces implemented by the infrastructure layer.

The application layer depends only on these abstractions (Dependency Inversion),
so any implementation can be swapped via configuration/DI without changing
business logic.
"""

from app.domain.interfaces.behavior import Behavior, BehaviorManager
from app.domain.interfaces.memory import MemoryRepository
from app.domain.interfaces.planner import Planner
from app.domain.interfaces.repositories import (
    LogEntry,
    LogRepository,
    MissionRepository,
    RobotRepository,
    TaskRepository,
)
from app.domain.interfaces.speech import SpeechRecognizer
from app.domain.interfaces.state_store import RobotSnapshot, RobotStateStore
from app.domain.interfaces.vision import Frame, VisionDetector

__all__ = [
    "Behavior",
    "BehaviorManager",
    "VisionDetector",
    "Frame",
    "SpeechRecognizer",
    "Planner",
    "MemoryRepository",
    "RobotRepository",
    "MissionRepository",
    "TaskRepository",
    "LogRepository",
    "LogEntry",
    "RobotStateStore",
    "RobotSnapshot",
]
