"""Plan and BehaviorOutput value objects.

``Plan`` is what a :class:`~app.domain.interfaces.planner.Planner` produces — a
decision about *which* behavior should be active and why. ``BehaviorOutput`` is
what a :class:`~app.domain.interfaces.behavior.Behavior` produces — the concrete
actuation (velocity + optional speech) for one tick.

Separating "decide" (planner) from "act" (behavior) lets us later swap a
RulePlanner for an LLMPlanner or RLPlanner without changing any behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.value_objects.enums import BehaviorType
from app.domain.value_objects.velocity import Velocity


@dataclass(frozen=True, slots=True)
class Plan:
    """A planning decision."""

    behavior: BehaviorType
    reason: str = ""
    speech: str | None = None
    params: dict = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class BehaviorOutput:
    """The actuation result of running a behavior for one tick."""

    behavior: BehaviorType
    velocity: Velocity = field(default_factory=Velocity.stop)
    speech: str | None = None
    metadata: dict = field(default_factory=dict)

    @classmethod
    def idle(cls, behavior: BehaviorType, *, speech: str | None = None) -> BehaviorOutput:
        return cls(behavior=behavior, velocity=Velocity.stop(), speech=speech)
