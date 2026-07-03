"""Mission endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import get_mission_service
from app.application.services.mission_service import MissionService
from app.schemas.common import ApiResponse
from app.schemas.mission import MissionCreate, MissionRead

router = APIRouter(prefix="/mission", tags=["mission"])


@router.post(
    "",
    response_model=ApiResponse[MissionRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create a mission",
)
async def create_mission(
    payload: MissionCreate,
    service: Annotated[MissionService, Depends(get_mission_service)],
) -> ApiResponse[MissionRead]:
    mission = await service.create_mission(
        name=payload.name,
        goal=payload.goal,
        robot_id=payload.robot_id,
        params=payload.params,
        tasks=[t.model_dump() for t in payload.tasks],
    )
    return ApiResponse(data=MissionRead.model_validate(mission))


@router.get(
    "/{mission_id}",
    response_model=ApiResponse[MissionRead],
    summary="Get a mission by id",
)
async def get_mission(
    mission_id: UUID,
    service: Annotated[MissionService, Depends(get_mission_service)],
) -> ApiResponse[MissionRead]:
    mission = await service.get_mission(mission_id)
    return ApiResponse(data=MissionRead.model_validate(mission))
