"""DTOs for the robot control-loop use case (POST /robot/step).

These are plain dataclasses so the application layer stays free of Pydantic/HTTP.
The API layer maps its Pydantic request/response schemas to/from these.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.value_objects.enums import BehaviorType


@dataclass(slots=True)
class StepCommand:
    """One control-loop request from a robot."""

    robot_id: str
    image_b64: str | None = None
    audio_b64: str | None = None
    reported_state: str | None = None
    battery: float | None = None
    correlation_id: str | None = None


@dataclass(slots=True)
class StepResult:
    """The brain's decision for one tick — exactly what the robot actuates."""

    behavior: BehaviorType
    linear_velocity: float
    angular_velocity: float
    speech: str | None = None
    metadata: dict = field(default_factory=dict)
