"""Planner port.

A planner maps the current :class:`RobotContext` to a :class:`Plan` (which
behavior to run + why). The planner NEVER calls a model directly and NEVER
computes velocities — that is the behavior's job. This keeps RulePlanner,
LLMPlanner and RLPlanner interchangeable.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.value_objects.plan import Plan
from app.domain.value_objects.robot_context import RobotContext


class Planner(ABC):
    """Decides which behavior should be active for the given context."""

    @abstractmethod
    async def plan(self, context: RobotContext) -> Plan:
        """Return a :class:`Plan` for ``context``."""
        raise NotImplementedError
