"""Handoff coordinator between customer and rep layers."""

from __future__ import annotations

from typing import Dict, List, Tuple

from src.core.lead_context import LeadContext
from src.core.handoff_queue import HandoffQueue, HandoffTask
from src.domain.decision_trace import TriggerHit
from src.domain.trigger_catalog import (
    NON_AGENT_FRUSTRATION_TARGETS,
    TRIGGER_CLASS,
    TRIGGER_PRECEDENCE,
    HandoffTriggerType,
    sla_minutes_for_trigger,
)


class HandoffManager:
    """Creates and dispatches inter-layer handoff tasks.

    ``evaluate`` returns every trigger that fired, ordered by
    ``TRIGGER_PRECEDENCE`` (interventions, then attention, then context); the
    first is the primary trigger. SLA values come from ``domain.trigger_catalog``.
    """

    def __init__(self, queue: HandoffQueue) -> None:
        self._queue = queue

    def evaluate(self, signals: Dict[str, object], context: LeadContext) -> List[TriggerHit]:
        """All triggers that fired this turn, primary first.

        An explicit human request is unconditional: it does not depend on
        sentiment, trust state, fit, or rep availability.
        """
        evidence: Dict[str, str] = dict(signals.get("_evidence") or {})  # type: ignore[arg-type]
        fired: Dict[str, str] = {}

        for key in (
            HandoffTriggerType.HUMAN_REQUEST.value,
            HandoffTriggerType.COMMITMENT_DEMAND.value,
            HandoffTriggerType.PRICING_NEGOTIATION.value,
            HandoffTriggerType.CONTRACT_LEGAL_ASK.value,
            HandoffTriggerType.STRONG_BUYING_SIGNAL.value,
            HandoffTriggerType.PRICING_DISCUSSION.value,
            HandoffTriggerType.COMPETITOR_MENTION.value,
            HandoffTriggerType.STAKEHOLDER_APPROVAL_NEEDED.value,
        ):
            if bool(signals.get(key, False)):
                fired[key] = evidence.get(key, f"signal {key}")

        # Frustration — unless it is positively identified as aimed at something
        # other than this agent (a previous vendor, the prospect's own process).
        # That is discovery material, not a failing conversation. Unknown /
        # unspecified targets still escalate: only positive evidence may
        # suppress a human moment.
        sentiment = str(signals.get("sentiment", context.sentiment)).strip().lower()
        if sentiment in {"frustration", "frustrated"}:
            target = str(signals.get("sentiment_target", "unspecified")).strip().lower()
            if target not in NON_AGENT_FRUSTRATION_TARGETS:
                fired[HandoffTriggerType.FRUSTRATION.value] = f"sentiment={sentiment}, target={target}"

        return [
            TriggerHit(t, TRIGGER_CLASS[t].value, fired[t])
            for t in TRIGGER_PRECEDENCE
            if t in fired
        ]

    def should_trigger(self, signals: Dict[str, object], context: LeadContext) -> Tuple[bool, str]:
        """Primary trigger only: ``(triggered, trigger_type)`` or ``(False, "none")``."""
        hits = self.evaluate(signals, context)
        if not hits:
            return False, HandoffTriggerType.NONE.value
        return True, hits[0].trigger_type

    def get_sla(self, trigger_type: str) -> int:
        """Return SLA target in minutes for a trigger type."""
        return sla_minutes_for_trigger(trigger_type)

    def request_rep_handoff(self, lead_id: str, payload: Dict[str, object]) -> None:
        task = HandoffTask(
            lead_id=lead_id,
            source_layer="customer_layer",
            target_layer="rep_layer",
            payload=dict(payload),
        )
        self._queue.enqueue(task)

    def request_customer_handoff(self, lead_id: str, payload: Dict[str, object]) -> None:
        task = HandoffTask(
            lead_id=lead_id,
            source_layer="rep_layer",
            target_layer="customer_layer",
            payload=dict(payload),
        )
        self._queue.enqueue(task)
        # TODO: Attach correlation IDs for traceability across handoffs.
