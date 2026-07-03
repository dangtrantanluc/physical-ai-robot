"""Aggregate API router — composes all v1 route modules."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routes import health, mission, robot, ws

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(robot.router)
api_router.include_router(mission.router)
api_router.include_router(ws.router)
