"""Redis implementation of the RobotStateStore port.

Each robot's hot state is stored as a single JSON blob under ``robot:{id}:state``
with a TTL, so stale robots expire automatically. Whole-object read/write keeps the
control loop simple and race-free enough for a single robot's sequential ticks.
"""

from __future__ import annotations

import json

from redis.asyncio import Redis

from app.domain.interfaces.state_store import RobotSnapshot, RobotStateStore
from app.domain.value_objects.enums import BehaviorType

# Robots that go silent for this long are evicted from hot state (they re-init on
# their next tick). 1 hour is ample for an intermittent mobile client.
_STATE_TTL_SECONDS = 3600


def _key(robot_id: str) -> str:
    return f"robot:{robot_id}:state"


class RedisRobotStateStore(RobotStateStore):
    """Persists :class:`RobotSnapshot` in Redis."""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def get(self, robot_id: str) -> RobotSnapshot:
        raw = await self._redis.get(_key(robot_id))
        if not raw:
            return RobotSnapshot.initial(robot_id)
        data = json.loads(raw)
        return RobotSnapshot(
            robot_id=robot_id,
            current_behavior=BehaviorType(data.get("current_behavior", "idle")),
            mission_id=data.get("mission_id"),
            battery=data.get("battery"),
            step_count=int(data.get("step_count", 0)),
            last_frame=data.get("last_frame", {}),
        )

    async def set(self, snapshot: RobotSnapshot) -> None:
        payload = {
            "current_behavior": snapshot.current_behavior.value,
            "mission_id": snapshot.mission_id,
            "battery": snapshot.battery,
            "step_count": snapshot.step_count,
            "last_frame": snapshot.last_frame,
        }
        await self._redis.set(
            _key(snapshot.robot_id),
            json.dumps(payload),
            ex=_STATE_TTL_SECONDS,
        )

    async def ping(self) -> bool:
        try:
            return bool(await self._redis.ping())
        except Exception:  # noqa: BLE001 — health check must never raise
            return False
