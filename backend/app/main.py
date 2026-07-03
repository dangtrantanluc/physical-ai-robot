"""FastAPI application factory + ASGI entrypoint.

Run with: ``uvicorn app.main:app``.

The application owns a single :class:`Container` (built on startup, disposed on
shutdown) that holds all process-wide singletons. Business logic lives in the
application/domain layers; this module only wires transport, middleware and lifecycle.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import __version__
from app.api.errors import register_exception_handlers
from app.api.middleware import CorrelationIdMiddleware
from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.container import Container
from app.core.logging import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build the DI container on startup; dispose it on shutdown."""
    settings: Settings = app.state.settings
    app.state.container = await Container.create(settings)
    logger.info("app_startup", version=__version__, environment=settings.environment.value)
    try:
        yield
    finally:
        await app.state.container.shutdown()
        logger.info("app_shutdown")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Application factory (also used by tests with overridden settings)."""
    settings = settings or get_settings()
    configure_logging(settings)

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description="Backend 'Robot Brain' — Clean Architecture + DDD.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    app.state.settings = settings

    app.add_middleware(CorrelationIdMiddleware)
    register_exception_handlers(app)
    # Routes are mounted at root to honor the device-facing contract
    # (POST /robot/step, GET /robot/{id}, /mission, WS /robot/ws, /health).
    app.include_router(api_router)
    return app


app = create_app()
