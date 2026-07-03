"""LLMPlanner — behavior selection via a third-party LLM API (provider-neutral).

Activated with ``PLANNER=llm``. Calls an OpenAI-compatible ``/chat/completions``
endpoint configured entirely via env (``LLM__BASE_URL`` / ``LLM__API_KEY`` /
``LLM__MODEL``), so it works with OpenAI, OpenRouter, Groq, Together, a local
vLLM/Ollama server, or any compatible gateway — plug in your own endpoint.

Design (safety-first, robust):
  * A **critical-battery STOP is decided in code**, never delegated to the LLM — a
    hard safety stop must be deterministic.
  * The LLM is asked for a compact JSON decision (behavior + reason + optional
    speech), parsed tolerantly.
  * **Any** failure (network, timeout, bad JSON, unknown behavior) falls back to the
    injected :class:`RulePlanner`, so the control loop never breaks because the API
    is slow or down.

Note on cadence: an LLM call per tick is unrealistic at 10 FPS — use this planner at
a low control frequency, or for high-level goal selection, and let behaviors run the
fast loop. (A per-robot decision cache/throttle can be layered on later.)
"""

from __future__ import annotations

import json

import httpx

from app.core.logging import get_logger
from app.domain.interfaces.planner import Planner
from app.domain.value_objects.enums import BehaviorType
from app.domain.value_objects.plan import Plan
from app.domain.value_objects.robot_context import RobotContext

logger = get_logger(__name__)

_ALLOWED = [b.value for b in BehaviorType]
_SYSTEM_PROMPT = (
    "You are the decision module of a physical follow-robot. Given the robot's "
    "current state, choose the single next behavior.\n"
    f"Allowed behaviors: {_ALLOWED}.\n"
    "Guidance: obey an explicit voice command; if following and the person is lost, "
    "search; if searching and a person appears, follow; otherwise hold a sensible "
    "state. Respond with ONLY compact JSON, no prose: "
    '{"behavior": "<one of allowed>", "reason": "<short>", "speech": "<short sentence or null>"}'
)


class LLMPlanner(Planner):
    """Provider-neutral LLM planner with a deterministic rule fallback."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        fallback: Planner,
        battery_critical_pct: float,
        temperature: float = 0.2,
        timeout_s: float = 6.0,
        max_tokens: int = 200,
        json_mode: bool = False,
    ) -> None:
        self._url = base_url.rstrip("/") + "/chat/completions"
        self._api_key = api_key
        self._model = model
        self._fallback = fallback
        self._battery_critical = battery_critical_pct
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._json_mode = json_mode
        self._client = httpx.AsyncClient(timeout=timeout_s)

    async def plan(self, context: RobotContext) -> Plan:
        # Deterministic safety override — never left to the model.
        if context.battery is not None and context.battery <= self._battery_critical:
            return Plan(
                behavior=BehaviorType.STOP,
                reason="battery_critical",
                speech="Battery critically low. Stopping.",
            )
        try:
            return await self._plan_via_llm(context)
        except Exception as exc:  # noqa: BLE001 — control loop must survive any API failure
            logger.warning("llm_planner_fallback", error=str(exc))
            return await self._fallback.plan(context)

    async def _plan_via_llm(self, context: RobotContext) -> Plan:
        payload: dict = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": self._describe(context)},
            ],
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
        }
        if self._json_mode:
            payload["response_format"] = {"type": "json_object"}

        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        resp = await self._client.post(self._url, json=payload, headers=headers)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]

        decision = _extract_json(content)
        behavior = BehaviorType(str(decision["behavior"]).strip().lower())
        reason = str(decision.get("reason", "")).strip()[:120]
        speech = decision.get("speech")
        speech = str(speech).strip() if speech else None

        logger.debug("llm_planner_decision", behavior=behavior.value, reason=reason)
        return Plan(behavior=behavior, reason=f"llm:{reason}" if reason else "llm", speech=speech)

    @staticmethod
    def _describe(context: RobotContext) -> str:
        perception = context.perception
        return (
            "Robot state:\n"
            f"- current_behavior: {context.current_behavior.value}\n"
            f"- battery_percent: {context.battery}\n"
            f"- voice_command: {context.transcript.text or '(none)'}\n"
            f"- detections: {perception.summary()} "
            f"(person_visible={perception.has_person})\n"
            "Choose the next behavior."
        )

    async def aclose(self) -> None:
        await self._client.aclose()


def _extract_json(text: str) -> dict:
    """Tolerantly extract a JSON object from an LLM reply (handles code fences/prose)."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned[:4].lower() == "json":
            cleaned = cleaned[4:]
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(cleaned[start : end + 1])
    return json.loads(cleaned)
