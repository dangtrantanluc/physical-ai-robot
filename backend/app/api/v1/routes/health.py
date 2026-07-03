"""Health endpoint — liveness + dependency readiness."""

from __future__ import annotations

from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from sqlalchemy import text

from app import __version__
from app.api.deps import ContainerDep
from app.core.container import Container

router = APIRouter(tags=["system"])


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    checks: dict[str, bool]


async def _check_db(container: Container) -> bool:
    try:
        async with container.session_factory() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:  # noqa: BLE001 — health probe must not raise
        return False


@router.get("/health", response_model=HealthResponse, summary="Service health")
async def health(
    container: ContainerDep,
    response: Response,
) -> HealthResponse:
    """Return service status and per-dependency readiness.

    Responds 200 when healthy, 503 when any dependency is down (so orchestrators
    and UptimeRobot can act on it).
    """
    redis_ok = await container.state_store.ping()
    db_ok = await _check_db(container)
    healthy = redis_ok and db_ok
    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthResponse(
        status="ok" if healthy else "degraded",
        version=__version__,
        environment=container.settings.environment.value,
        checks={"redis": redis_ok, "database": db_ok},
    )
