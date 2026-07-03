"""RulePlanner — a deterministic, priority-ordered rule engine.

Decides *which behavior* should be active for a given :class:`RobotContext`. Rules
are evaluated in priority order (safety first, then explicit human command, then
autonomous perception-driven transitions); the first rule that fires wins. Adding a
rule = adding one small method to ``_RULES`` — no nested if/else pyramid.

Later this whole class can be replaced by an LLMPlanner or RLPlanner behind the
same :class:`Planner` port; behaviors never change.
"""

from __future__ import annotations

from collections.abc import Callable

from app.core.logging import get_logger
from app.domain.interfaces.planner import Planner
from app.domain.value_objects.enums import BehaviorType
from app.domain.value_objects.plan import Plan
from app.domain.value_objects.robot_context import RobotContext

logger = get_logger(__name__)

# Voice-command keyword maps (English + Vietnamese). Kept as data, not code.
_COMMAND_KEYWORDS: dict[BehaviorType, tuple[str, ...]] = {
    BehaviorType.STOP: ("stop", "halt", "dừng", "đứng", "ngừng"),
    BehaviorType.FOLLOW: ("follow", "come", "theo", "đi theo", "bám"),
    BehaviorType.SEARCH: ("search", "find", "look", "tìm", "kiếm"),
    BehaviorType.IDLE: ("idle", "rest", "wait", "nghỉ", "chờ", "đợi"),
}

_RulePredicate = Callable[["RulePlanner", RobotContext], Plan | None]


class RulePlanner(Planner):
    """Rule-based behavior selector."""

    def __init__(self, *, battery_critical_pct: float, battery_low_pct: float) -> None:
        self._battery_critical = battery_critical_pct
        self._battery_low = battery_low_pct

    async def plan(self, context: RobotContext) -> Plan:
        for rule in self._RULES:
            plan = rule(self, context)
            if plan is not None:
                logger.debug(
                    "planner_decision",
                    robot_id=context.robot_id,
                    behavior=plan.behavior.value,
                    reason=plan.reason,
                )
                return plan
        # Unreachable: the final fallback rule always returns a plan.
        return Plan(behavior=BehaviorType.IDLE, reason="default")

    # ---- Rules (priority order) --------------------------------------------

    def _rule_critical_battery(self, ctx: RobotContext) -> Plan | None:
        """Safety override: halt when battery is critically low."""
        if ctx.battery is not None and ctx.battery <= self._battery_critical:
            return Plan(
                behavior=BehaviorType.STOP,
                reason="battery_critical",
                speech="Battery critically low. Stopping.",
            )
        return None

    def _rule_voice_command(self, ctx: RobotContext) -> Plan | None:
        """Explicit human command wins over autonomous logic."""
        if not ctx.has_voice_command:
            return None
        text = ctx.transcript.text
        for behavior, keywords in _COMMAND_KEYWORDS.items():
            if any(word in text for word in keywords):
                return Plan(
                    behavior=behavior,
                    reason="voice_command",
                    speech=self._ack(behavior),
                    params={"command": text},
                )
        return None

    def _rule_follow_continuity(self, ctx: RobotContext) -> Plan | None:
        """While following: keep following if the person is visible, else search."""
        if ctx.current_behavior is not BehaviorType.FOLLOW:
            return None
        if ctx.perception.has_person:
            return Plan(behavior=BehaviorType.FOLLOW, reason="person_tracked")
        return Plan(
            behavior=BehaviorType.SEARCH,
            reason="person_lost",
            speech="I lost you. Searching.",
        )

    def _rule_search_acquire(self, ctx: RobotContext) -> Plan | None:
        """While searching: switch to follow the moment a person is found."""
        if ctx.current_behavior is not BehaviorType.SEARCH:
            return None
        if ctx.perception.has_person:
            return Plan(
                behavior=BehaviorType.FOLLOW,
                reason="person_acquired",
                speech="Found you.",
            )
        return Plan(behavior=BehaviorType.SEARCH, reason="still_searching")

    def _rule_hold(self, ctx: RobotContext) -> Plan | None:
        """No command and not in an autonomous loop: hold the current behavior.

        STOP is sticky (requires an explicit command to leave); everything else
        settles to IDLE.
        """
        if ctx.current_behavior is BehaviorType.STOP:
            return Plan(behavior=BehaviorType.STOP, reason="hold_stop")
        return None

    def _rule_default(self, ctx: RobotContext) -> Plan | None:
        """Terminal fallback — always fires."""
        return Plan(behavior=BehaviorType.IDLE, reason="idle_default")

    @staticmethod
    def _ack(behavior: BehaviorType) -> str | None:
        return {
            BehaviorType.FOLLOW: "Okay, following you.",
            BehaviorType.SEARCH: "Searching now.",
            BehaviorType.STOP: "Stopping.",
            BehaviorType.IDLE: "Standing by.",
        }.get(behavior)

    # Evaluated top-to-bottom; first non-None wins.
    _RULES: tuple[_RulePredicate, ...] = (
        _rule_critical_battery,
        _rule_voice_command,
        _rule_follow_continuity,
        _rule_search_acquire,
        _rule_hold,
        _rule_default,
    )
