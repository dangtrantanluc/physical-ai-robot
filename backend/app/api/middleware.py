"""HTTP middleware — correlation IDs.

Assigns/propagates an ``x-correlation-id`` per request and binds it to the structlog
context so every log line for the request is traceable. The id is echoed back in the
response header so a client (or the robot) can quote it when reporting an issue.
"""

from __future__ import annotations

from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import bind_contextvars, clear_contextvars

CORRELATION_HEADER = "x-correlation-id"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Bind a correlation id to the logging context for the request's lifetime."""

    async def dispatch(self, request: Request, call_next) -> Response:
        correlation_id = request.headers.get(CORRELATION_HEADER) or uuid4().hex
        request.state.correlation_id = correlation_id
        clear_contextvars()
        bind_contextvars(correlation_id=correlation_id, path=request.url.path)
        try:
            response = await call_next(request)
        finally:
            clear_contextvars()
        response.headers[CORRELATION_HEADER] = correlation_id
        return response
