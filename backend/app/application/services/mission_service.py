"""MissionService — create and query missions."""

from __future__ import annotations

from uuid import UUID

from app.core.exceptions import MissionNotFoundError
from app.domain.entities.mission import Mission, Task
from app.domain.interfaces.repositories import MissionRepository
from app.domain.value_objects.enums import MissionStatus


class MissionService:
    """Use cases for missions and their tasks."""

    def __init__(self, missions: MissionRepository) -> None:
        self._missions = missions

    async def create_mission(
        self,
        *,
        name: str,
        goal: str = "",
        robot_id: str | None = None,
        params: dict | None = None,
        tasks: list[dict] | None = None,
    ) -> Mission:
        """Create a mission with optional ordered tasks."""
        mission = Mission(
            name=name,
            goal=goal,
            robot_id=robot_id,
            status=MissionStatus.PENDING,
            params=params or {},
        )
        for index, task in enumerate(tasks or []):
            mission.tasks.append(
                Task(
                    name=task["name"],
                    order_index=task.get("order_index", index),
                    params=task.get("params", {}),
                    mission_id=mission.id,
                )
            )
        return await self._missions.create(mission)

    async def get_mission(self, mission_id: UUID) -> Mission:
        mission = await self._missions.get(mission_id)
        if mission is None:
            raise MissionNotFoundError(
                f"Mission {mission_id} not found", details={"mission_id": str(mission_id)}
            )
        return mission

    async def list_for_robot(self, robot_id: str, *, limit: int = 50) -> list[Mission]:
        return await self._missions.list_for_robot(robot_id, limit=limit)

    async def set_status(self, mission_id: UUID, status: MissionStatus) -> Mission:
        mission = await self._missions.set_status(mission_id, status)
        if mission is None:
            raise MissionNotFoundError(
                f"Mission {mission_id} not found", details={"mission_id": str(mission_id)}
            )
        return mission
