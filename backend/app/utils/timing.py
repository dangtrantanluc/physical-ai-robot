"""Timing helpers for latency/FPS metrics.

Uses :func:`time.perf_counter` (monotonic, high-resolution) — never wall-clock —
so measurements are immune to clock adjustments.
"""

from __future__ import annotations

from time import perf_counter
from types import TracebackType


class Stopwatch:
    """Context manager that measures elapsed milliseconds.

    Example::

        with Stopwatch() as sw:
            await detector.detect(frame)
        logger.info("inference", inference_ms=sw.elapsed_ms)
    """

    __slots__ = ("_start", "_elapsed_ms")

    def __init__(self) -> None:
        self._start = 0.0
        self._elapsed_ms = 0.0

    def __enter__(self) -> Stopwatch:
        self._start = perf_counter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self._elapsed_ms = (perf_counter() - self._start) * 1000.0

    @property
    def elapsed_ms(self) -> float:
        """Elapsed milliseconds. Valid after the ``with`` block exits."""
        return self._elapsed_ms


def fps_from_ms(elapsed_ms: float) -> float:
    """Convert a per-tick duration (ms) into an instantaneous FPS estimate."""
    if elapsed_ms <= 0:
        return 0.0
    return 1000.0 / elapsed_ms
