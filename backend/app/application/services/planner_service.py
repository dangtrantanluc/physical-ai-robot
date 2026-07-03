"""PlannerService — use-case wrapper over the Planner port.

Kept deliberately thin: it delegates to whichever :class:`Planner` implementation
was injected (rule/LLM/RL). It exists so the orchestrating RobotService depends on a
stable application service rather than a concrete planner, and so cross-cutting
concerns (metrics, guardrails) have a single home later.
"""

from __future__ import annotations

from app.domain.interfaces.planner import Planner
from app.domain.value_objects.plan import Plan
from app.domain.value_objects.robot_context import RobotContext


class PlannerService:
    """Decides the next behavior for a context."""

    def __init__(self, planner: Planner) -> None:
        self._planner = planner

    async def decide(self, context: RobotContext) -> Plan:
        return await self._planner.plan(context)
