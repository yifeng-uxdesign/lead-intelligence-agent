"""Handoff coordinator between customer and rep layers."""

from __future__ import annotations

from typing import Dict, Tuple

from src.core.lead_context import LeadContext
from src.core.handoff_queue import HandoffQueue, HandoffTask
from src.domain.trigger_catalog import (
    NON_AGENT_FRUSTRATION_TARGETS,
    HandoffTriggerType,
    sla_minutes_for_trigger,
)


class HandoffManager:
    """Creates and dispatches inter-layer handoff tasks.

    Trigger precedence is fixed (see ``should_trigger``): first match wins.
    SLA values come from ``domain.trigger_catalog`` — single source of truth.
    """

    def __init__(self, queue: HandoffQueue) -> None:
        self._queue = queue

    def should_trigger(self, signals: Dict[str, object], context: LeadContext) -> Tuple[bool, str]:
        """Evaluate whether this conversation should be handed to a rep.

        An explicit human request is checked first and unconditionally: it does
        not depend on sentiment, trust state, fit, or rep availability.

        Returns:
            (triggered, trigger_type)
            - triggered: handoff decision
            - trigger_type: canonical trigger key or ``"none"``
        """
        # 1) Customer explicitly asks for a human.
        if bool(signals.get("human_request", False)):
            return True, HandoffTriggerType.HUMAN_REQUEST.value

        # 2) Pricing discussion starts.
        if bool(signals.get("pricing_discussion", False)):
            return True, HandoffTriggerType.PRICING_DISCUSSION.value

        # 3) Strong buying signal detected.
        if bool(signals.get("strong_buying_signal", False)):
            return True, HandoffTriggerType.STRONG_BUYING_SIGNAL.value

        # 4) Sentiment drops to frustration — unless it is positively identified
        #    as aimed at something other than this agent (a previous vendor, the
        #    prospect's own process). That is discovery material, not a failing
        #    conversation. Unknown/unspecified targets still escalate: only
        #    positive evidence may suppress a human moment.
        sentiment = str(signals.get("sentiment", context.sentiment)).strip().lower()
        if sentiment in {"frustration", "frustrated"}:
            target = str(signals.get("sentiment_target", "unspecified")).strip().lower()
            if target not in NON_AGENT_FRUSTRATION_TARGETS:
                return True, HandoffTriggerType.FRUSTRATION.value

        # 5) Competitor mention appears.
        if bool(signals.get("competitor_mention", False)):
            return True, HandoffTriggerType.COMPETITOR_MENTION.value

        # 6) Stakeholder approval is needed.
        if bool(signals.get("stakeholder_approval_needed", False)):
            return True, HandoffTriggerType.STAKEHOLDER_APPROVAL_NEEDED.value

        return False, HandoffTriggerType.NONE.value

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
