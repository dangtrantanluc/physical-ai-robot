"""Structured logging via structlog.

- Console renderer in development, JSON renderer in staging/production.
- A ``correlation_id`` (and any other context bound via
  :func:`structlog.contextvars.bind_contextvars`) is merged into every event, so
  a single request can be traced FE -> BE -> DB.
- The robot control loop logs the metrics required by the spec: robot_id,
  behavior, latency, fps, inference_time, api_time.

Usage::

    from app.core.logging import get_logger
    logger = get_logger(__name__)
    logger.info("robot_step", robot_id=rid, behavior="follow", latency_ms=12.3)
"""

from __future__ import annotations

import logging
import sys

import structlog

from app.core.config import Settings

# Re-export helpers so call sites depend only on this module.
bind_contextvars = structlog.contextvars.bind_contextvars
clear_contextvars = structlog.contextvars.clear_contextvars
unbind_contextvars = structlog.contextvars.unbind_contextvars


def configure_logging(settings: Settings) -> None:
    """Configure structlog + stdlib logging. Idempotent; call once at startup."""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]

    renderer: structlog.types.Processor = (
        structlog.processors.JSONRenderer()
        if settings.log_json
        else structlog.dev.ConsoleRenderer(colors=not settings.log_json)
    )

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Route stdlib logging (uvicorn, sqlalchemy) through the same level.
    logging.basicConfig(level=level, handlers=[logging.StreamHandler(sys.stdout)], force=True)
    for noisy in ("uvicorn.access",):
        logging.getLogger(noisy).setLevel(max(level, logging.INFO))


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger."""
    return structlog.get_logger(name)
