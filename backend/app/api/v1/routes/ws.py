"""WebSocket control loop — a persistent, low-overhead channel for `/robot/step`.

Same semantics as the HTTP endpoint but over a long-lived socket: the robot streams
step frames as JSON, the brain streams back flat commands. Each message is its own
unit of work (fresh DB session, committed per tick) so a failure on one tick never
corrupts another.
"""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.api.deps import build_robot_service
from app.core.logging import bind_contextvars, clear_contextvars, get_logger
from app.schemas.robot import StepRequest, StepResponse

router = APIRouter(tags=["robot"])
logger = get_logger(__name__)


@router.websocket("/robot/ws")
async def robot_ws(websocket: WebSocket) -> None:
    """Bidirectional control loop.

    Client -> server: JSON matching :class:`StepRequest`.
    Server -> client: JSON matching :class:`StepResponse`, or an error frame
    ``{"error": {...}}`` for a malformed message (the socket stays open).
    """
    container = websocket.app.state.container
    await websocket.accept()
    logger.info("ws_connected", client=str(websocket.client))
    try:
        while True:
            raw = await websocket.receive_json()
            try:
                payload = StepRequest.model_validate(raw)
            except ValidationError as exc:
                await websocket.send_json(
                    {"error": {"code": "VALIDATION_ERROR", "details": exc.errors()}}
                )
                continue

            correlation_id = raw.get("correlation_id") if isinstance(raw, dict) else None
            clear_contextvars()
            bind_contextvars(correlation_id=correlation_id, transport="ws")

            # One unit of work per message.
            async with container.session_factory() as session:
                try:
                    service = build_robot_service(session, container)
                    result = await service.step(
                        payload.to_command(correlation_id=correlation_id)
                    )
                    await session.commit()
                except Exception:
                    await session.rollback()
                    logger.exception("ws_step_failed", robot_id=payload.robot_id)
                    await websocket.send_json({"error": {"code": "INTERNAL_ERROR"}})
                    continue

            await websocket.send_json(StepResponse.from_result(result).model_dump())
    except WebSocketDisconnect:
        logger.info("ws_disconnected", client=str(websocket.client))
    finally:
        clear_contextvars()
