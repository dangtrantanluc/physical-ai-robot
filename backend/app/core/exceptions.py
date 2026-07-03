"""Application/domain exception hierarchy.

These are transport-agnostic: the API layer (app/api/errors.py) maps them to HTTP
responses. Business/domain code raises these, never ``HTTPException`` directly, so
the domain stays free of framework concerns.
"""

from __future__ import annotations


class AppError(Exception):
    """Base class for all expected application errors.

    Attributes:
        code: stable machine-readable error code (SCREAMING_SNAKE_CASE).
        message: human-readable description.
        status_code: suggested HTTP status for the API layer.
        details: optional structured context.
    """

    code: str = "APP_ERROR"
    status_code: int = 500

    def __init__(self, message: str, *, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(AppError):
    code = "NOT_FOUND"
    status_code = 404


class ValidationAppError(AppError):
    code = "VALIDATION_ERROR"
    status_code = 400


class ConflictError(AppError):
    code = "CONFLICT"
    status_code = 409


class RobotNotFoundError(NotFoundError):
    code = "ROBOT_NOT_FOUND"


class MissionNotFoundError(NotFoundError):
    code = "MISSION_NOT_FOUND"


class BehaviorNotRegisteredError(AppError):
    code = "BEHAVIOR_NOT_REGISTERED"
    status_code = 422


class InferenceError(AppError):
    """Raised when a vision/speech/planner model fails to produce a result."""

    code = "INFERENCE_ERROR"
    status_code = 502
