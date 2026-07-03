"""Shared API envelope schemas.

Management endpoints wrap payloads in ``{success, data, meta}`` / ``{success, error}``
per the house API convention. NOTE: the real-time robot endpoints
(``/robot/step`` and the WebSocket) deliberately return a *flat* body — the embedded
robot client expects exactly that shape and every byte/millisecond counts.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorBody(BaseModel):
    code: str = Field(..., examples=["ROBOT_NOT_FOUND"])
    message: str
    correlation_id: str | None = None
    details: list | dict | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorBody


class ApiResponse(BaseModel, Generic[T]):
    """Success envelope for management endpoints."""

    success: bool = True
    data: T
    meta: dict | None = None
