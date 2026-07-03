"""Global exception handlers.

Maps domain/application :class:`AppError`s (and uncaught errors) to the house error
envelope. Full detail (with stack trace) is logged server-side; the client only ever
sees a safe message + a correlation id — never a stack trace.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError
from app.core.logging import get_logger

logger = get_logger(__name__)


def _correlation_id(request: Request) -> str | None:
    return getattr(request.state, "correlation_id", None)


def _error_body(code: str, message: str, request: Request, details=None) -> dict:
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "correlation_id": _correlation_id(request),
            "details": details,
        },
    }


def register_exception_handlers(app: FastAPI) -> None:
    """Attach handlers to the app."""

    @app.exception_handler(AppError)
    async def _handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        if exc.status_code >= 500:
            logger.error(
                "app_error",
                code=exc.code,
                message=exc.message,
                path=request.url.path,
                details=exc.details,
            )
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.message, request, exc.details or None),
        )

    @app.exception_handler(RequestValidationError)
    async def _handle_validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=_error_body(
                "VALIDATION_ERROR", "Request validation failed", request, exc.errors()
            ),
        )

    @app.exception_handler(Exception)
    async def _handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        # Log the full error server-side; never leak internals to the client.
        logger.exception("unhandled_exception", path=request.url.path)
        return JSONResponse(
            status_code=500,
            content=_error_body(
                "INTERNAL_ERROR", "Internal server error, please try again later", request
            ),
        )
