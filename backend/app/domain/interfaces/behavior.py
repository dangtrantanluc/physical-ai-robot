"""Behavior and BehaviorManager ports.

The behavior system replaces a large ``if/else`` state machine with a registry of
self-contained behaviors. Each behavior owns its lifecycle (``start`` / ``update``
/ ``stop``) and its per-tick actuation (``execute``). Adding a new behavior means
adding a class and registering it — no existing code changes (Open/Closed).

Behaviors are intentionally *stateless* with respect to a specific robot: the
"currently active behavior" is persisted in the state store (Redis), so the API
stays horizontally scalable (any worker can serve any robot's next tick).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.value_objects.enums import BehaviorType
from app.domain.value_objects.plan import BehaviorOutput
from app.domain.value_objects.robot_context import RobotContext


class Behavior(ABC):
    """A single robot behavior."""

    #: The type this behavior handles. Set by concrete subclasses.
    behavior_type: BehaviorType

    @property
    def name(self) -> str:
        return self.behavior_type.value

    def start(self, context: RobotContext) -> None:
        """Lifecycle hook: called when this behavior becomes active. Default no-op."""
        return None

    def stop(self, context: RobotContext) -> None:
        """Lifecycle hook: called when this behavior is deactivated. Default no-op."""
        return None

    @abstractmethod
    async def update(self, context: RobotContext) -> BehaviorOutput:
        """Compute one tick of actuation for ``context``. The core of a behavior."""
        raise NotImplementedError

    async def execute(self, context: RobotContext) -> BehaviorOutput:
        """Template method: the public per-tick entry point.

        Defaults to :meth:`update`; subclasses may override to add pre/post logic
        (e.g. safety clamping) around the core computation.
        """
        return await self.update(context)


class BehaviorManager(ABC):
    """Registers behaviors and drives switching + execution."""

    @abstractmethod
    def register(self, behavior: Behavior) -> None:
        """Add a behavior to the registry (keyed by its ``behavior_type``)."""
        raise NotImplementedError

    @abstractmethod
    def get(self, behavior_type: BehaviorType) -> Behavior:
        """Return the registered behavior for ``behavior_type``.

        Raises :class:`BehaviorNotRegisteredError` if absent.
        """
        raise NotImplementedError

    @abstractmethod
    def switch_behavior(
        self,
        current: BehaviorType,
        target: BehaviorType,
        context: RobotContext,
    ) -> Behavior:
        """Transition from ``current`` to ``target``, firing stop/start hooks.

        Returns the now-active target behavior. A no-op transition (current ==
        target) does not re-fire lifecycle hooks.
        """
        raise NotImplementedError

    @abstractmethod
    async def execute(self, behavior: Behavior, context: RobotContext) -> BehaviorOutput:
        """Execute one tick of ``behavior`` for ``context``."""
        raise NotImplementedError
