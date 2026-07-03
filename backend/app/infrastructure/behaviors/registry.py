"""Default behavior wiring.

Builds a :class:`BehaviorManagerImpl` pre-loaded with the initial behavior set from
configuration. Registering a new behavior is a one-line addition here (plus its
class) — existing behaviors are untouched (Open/Closed Principle).
"""

from __future__ import annotations

from app.core.config import Settings
from app.infrastructure.behaviors.base import MotionBounds
from app.infrastructure.behaviors.follow import FollowBehavior
from app.infrastructure.behaviors.idle import IdleBehavior
from app.infrastructure.behaviors.manager import BehaviorManagerImpl
from app.infrastructure.behaviors.search import SearchBehavior
from app.infrastructure.behaviors.stop import StopBehavior


def build_behavior_manager(settings: Settings) -> BehaviorManagerImpl:
    """Construct and populate the behavior manager from settings."""
    bounds = MotionBounds(
        max_linear=settings.motion.max_linear_speed,
        max_angular=settings.motion.max_angular_speed,
    )

    manager = BehaviorManagerImpl()
    manager.register(IdleBehavior(bounds))
    manager.register(StopBehavior(bounds))
    manager.register(FollowBehavior(bounds, settings=settings.follow))
    manager.register(SearchBehavior(bounds, angular_speed=settings.search.angular_speed))
    # Future behaviors (AVOID, NAVIGATE, DOCK, ...) register here.
    return manager
