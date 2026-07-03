"""Domain enumerations."""

from __future__ import annotations

from enum import Enum


class BehaviorType(str, Enum):
    """The behaviors the robot brain can switch between.

    New behaviors (e.g. AVOID, NAVIGATE, DOCK) can be added here without touching
    existing behavior implementations — the registry maps a type to an instance.
    """

    IDLE = "idle"
    FOLLOW = "follow"
    SEARCH = "search"
    STOP = "stop"


class MissionStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"
