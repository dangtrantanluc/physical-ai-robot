"""Robot control-loop and read schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.application.dto.step import StepCommand, StepResult


class StepRequest(BaseModel):
    """Body of ``POST /robot/step`` — one control tick from the robot.

    ``image`` and ``audio`` are base64 strings (optionally data-URI prefixed);
    either may be omitted for a tick.
    """

    robot_id: str = Field(..., min_length=1, max_length=64, examples=["realme-q-01"])
    image: str | None = Field(None, description="base64-encoded camera frame")
    audio: str | None = Field(None, description="base64-encoded audio chunk")
    state: str | None = Field(None, description="robot-reported state label")
    battery: float | None = Field(None, ge=0, le=100, description="battery percent")

    def to_command(self, *, correlation_id: str | None = None) -> StepCommand:
        return StepCommand(
            robot_id=self.robot_id,
            image_b64=self.image,
            audio_b64=self.audio,
            reported_state=self.state,
            battery=self.battery,
            correlation_id=correlation_id,
        )


class StepResponse(BaseModel):
    """Flat response the robot actuates directly. NOT wrapped in an envelope."""

    behavior: str = Field(..., examples=["follow"])
    linear_velocity: float = Field(..., description="metres/second")
    angular_velocity: float = Field(..., description="radians/second")
    speech: str | None = None
    metadata: dict = Field(default_factory=dict)

    @classmethod
    def from_result(cls, result: StepResult) -> StepResponse:
        return cls(
            behavior=result.behavior.value,
            linear_velocity=result.linear_velocity,
            angular_velocity=result.angular_velocity,
            speech=result.speech,
            metadata=result.metadata,
        )


class RobotRead(BaseModel):
    """Robot resource representation."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    status: str
    battery: float | None
    current_behavior: str
    current_mission_id: str | None
    last_seen_at: datetime | None
    created_at: datetime | None
    updated_at: datetime | None
