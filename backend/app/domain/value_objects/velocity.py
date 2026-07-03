"""Velocity value object — the differential-drive command the robot understands."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Velocity:
    """A 2-DOF differential-drive command.

    Attributes:
        linear: forward speed in metres/second (positive = forward).
        angular: yaw rate in radians/second (positive = counter-clockwise / left).
    """

    linear: float = 0.0
    angular: float = 0.0

    @classmethod
    def stop(cls) -> Velocity:
        """Zero-motion command."""
        return cls(0.0, 0.0)

    def clamp(self, max_linear: float, max_angular: float) -> Velocity:
        """Return a copy with each component clamped to ``±max_*``."""
        return Velocity(
            linear=_clamp(self.linear, -max_linear, max_linear),
            angular=_clamp(self.angular, -max_angular, max_angular),
        )

    def scale(self, factor: float) -> Velocity:
        """Return a copy scaled by ``factor`` (e.g. to throttle on low battery)."""
        return Velocity(self.linear * factor, self.angular * factor)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
