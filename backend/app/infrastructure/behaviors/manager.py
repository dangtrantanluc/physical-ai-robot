"""BehaviorManagerImpl — registry + lifecycle for behaviors.

Holds a ``BehaviorType -> Behavior`` registry. Behaviors are stateless singletons;
the *active* behavior for a given robot lives in the state store, so this manager is
safe to share across robots and workers. ``switch_behavior`` fires the stop/start
lifecycle hooks only on an actual transition.
"""

from __future__ import annotations

from app.core.exceptions import BehaviorNotRegisteredError
from app.core.logging import get_logger
from app.domain.interfaces.behavior import Behavior, BehaviorManager
from app.domain.value_objects.enums import BehaviorType
from app.domain.value_objects.plan import BehaviorOutput
from app.domain.value_objects.robot_context import RobotContext

logger = get_logger(__name__)


class BehaviorManagerImpl(BehaviorManager):
    """Concrete behavior manager."""

    def __init__(self) -> None:
        self._registry: dict[BehaviorType, Behavior] = {}

    def register(self, behavior: Behavior) -> None:
        self._registry[behavior.behavior_type] = behavior
        logger.debug("behavior_registered", behavior=behavior.name)

    def get(self, behavior_type: BehaviorType) -> Behavior:
        try:
            return self._registry[behavior_type]
        except KeyError as exc:
            raise BehaviorNotRegisteredError(
                f"Behavior '{behavior_type.value}' is not registered",
                details={"behavior": behavior_type.value},
            ) from exc

    def switch_behavior(
        self,
        current: BehaviorType,
        target: BehaviorType,
        context: RobotContext,
    ) -> Behavior:
        target_behavior = self.get(target)
        if current == target:
            return target_behavior
        # Real transition: tear down the old, spin up the new.
        self.get(current).stop(context)
        target_behavior.start(context)
        logger.info(
            "behavior_switch",
            robot_id=context.robot_id,
            from_behavior=current.value,
            to_behavior=target.value,
        )
        return target_behavior

    async def execute(self, behavior: Behavior, context: RobotContext) -> BehaviorOutput:
        return await behavior.execute(context)

    @property
    def registered(self) -> list[BehaviorType]:
        return list(self._registry.keys())
