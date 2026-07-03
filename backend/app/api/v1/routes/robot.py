"""Robot endpoints: the control loop (`/robot/step`) and robot reads."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.api.deps import SessionDep, get_robot_service
from app.application.services.robot_service import RobotService
from app.core.exceptions import RobotNotFoundError
from app.infrastructure.database.repositories import SqlRobotRepository
from app.schemas.common import ApiResponse
from app.schemas.robot import RobotRead, StepRequest, StepResponse

router = APIRouter(prefix="/robot", tags=["robot"])


@router.post(
    "/step",
    response_model=StepResponse,
    summary="Run one control-loop tick",
    response_description="Flat actuation command the robot applies directly",
)
async def step(
    payload: StepRequest,
    request: Request,
    service: Annotated[RobotService, Depends(get_robot_service)],
) -> StepResponse:
    """The core robot loop.

    The robot POSTs its latest frame/audio/telemetry; the brain returns the
    behavior + velocity command (and optional speech). Response is intentionally
    flat — exactly what the embedded client consumes.
    """
    correlation_id = getattr(request.state, "correlation_id", None)
    result = await service.step(payload.to_command(correlation_id=correlation_id))
    return StepResponse.from_result(result)


@router.get(
    "/{robot_id}",
    response_model=ApiResponse[RobotRead],
    summary="Get a robot's current record",
)
async def get_robot(robot_id: str, session: SessionDep) -> ApiResponse[RobotRead]:
    robot = await SqlRobotRepository(session).get(robot_id)
    if robot is None:
        raise RobotNotFoundError(f"Robot '{robot_id}' not found", details={"robot_id": robot_id})
    return ApiResponse(data=RobotRead.model_validate(robot))
