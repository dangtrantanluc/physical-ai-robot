"""API-level tests using FastAPI's TestClient with dependency overrides.

No real Postgres/Redis: the engine/redis clients are created lazily (no connection
at construction), and the endpoints under test have their DB-touching dependencies
overridden with in-memory fakes.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_container, get_robot_service
from app.application.services.memory_service import MemoryService
from app.application.services.planner_service import PlannerService
from app.application.services.robot_service import RobotService
from app.application.services.speech_service import SpeechService
from app.application.services.vision_service import VisionService
from app.core.config import Settings
from app.infrastructure.behaviors.registry import build_behavior_manager
from app.infrastructure.planner.rule_planner import RulePlanner
from app.infrastructure.speech.mock_recognizer import MockRecognizer
from app.infrastructure.vision.mock_detector import MockDetector
from app.main import create_app
from tests.conftest import (
    FakeLogRepository,
    FakeMemoryRepository,
    FakeRobotRepository,
    FakeStateStore,
)


class _FakeSession:
    async def execute(self, *args, **kwargs):
        return None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False


def test_health_ok():
    app = create_app(Settings())
    fake_container = SimpleNamespace(
        settings=Settings(),
        state_store=FakeStateStore(),
        session_factory=_FakeSession,
    )
    app.dependency_overrides[get_container] = lambda: fake_container
    with TestClient(app) as client:
        resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["checks"] == {"redis": True, "database": True}
    assert "x-correlation-id" in resp.headers


def test_step_endpoint_returns_flat_command(person_image_b64):
    app = create_app(Settings())
    settings = Settings()

    def _fake_service() -> RobotService:
        return RobotService(
            vision=VisionService(MockDetector()),
            speech=SpeechService(MockRecognizer()),
            planner=PlannerService(RulePlanner(battery_critical_pct=12.0, battery_low_pct=25.0)),
            behavior_manager=build_behavior_manager(settings),
            state_store=FakeStateStore(),
            robots=FakeRobotRepository(),
            logs=FakeLogRepository(),
            settings=settings,
            memory=MemoryService(FakeMemoryRepository()),
        )

    app.dependency_overrides[get_robot_service] = _fake_service
    with TestClient(app) as client:
        resp = client.post(
            "/robot/step",
            json={"robot_id": "realme-q-01", "image": person_image_b64, "battery": 75.0},
        )
    assert resp.status_code == 200
    body = resp.json()
    # Flat contract — exactly the keys the robot consumes.
    assert set(body) == {"behavior", "linear_velocity", "angular_velocity", "speech", "metadata"}
    assert body["behavior"] in {"idle", "follow", "search", "stop"}


def test_step_validation_error_is_enveloped():
    app = create_app(Settings())
    with TestClient(app) as client:
        resp = client.post("/robot/step", json={"battery": 50})  # missing robot_id
    assert resp.status_code == 422
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.parametrize("missing_id", ["ghost-robot"])
def test_get_unknown_robot_returns_404(missing_id):
    """The not-found path maps a domain error to the house envelope (via a fake session)."""
    app = create_app(Settings())

    # Override the session dependency so the repo query returns no rows without a DB.
    from app.api.deps import get_session

    class _Session(_FakeSession):
        async def get(self, *args, **kwargs):
            return None

    async def _fake_session():
        yield _Session()

    app.dependency_overrides[get_session] = _fake_session
    with TestClient(app) as client:
        resp = client.get(f"/robot/{missing_id}")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "ROBOT_NOT_FOUND"
