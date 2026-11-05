"""Single source of truth for handoff triggers, SLA targets, and rep-brief mapping.

Customer-facing code should never import rep-specific copy from here; rep layer
consumes SLA minutes and display strings derived from this catalog.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, Final, Mapping

# --- Canonical handoff trigger identifiers (orchestrator + HandoffManager) ---


class HandoffTriggerType(str, Enum):
    """Evaluation order is ``TRIGGER_PRECEDENCE`` (HandoffManager.evaluate)."""

    NONE = "none"
    HUMAN_REQUEST = "human_request"
    # Kept as "pricing_discussion" for API/rep-brief compatibility; it means
    # pricing *interest* (attention). Negotiation is its own trigger.
    PRICING_DISCUSSION = "pricing_discussion"
    STRONG_BUYING_SIGNAL = "strong_buying_signal"
    FRUSTRATION = "frustration"
    COMPETITOR_MENTION = "competitor_mention"
    STAKEHOLDER_APPROVAL_NEEDED = "stakeholder_approval_needed"
    PRICING_NEGOTIATION = "pricing_negotiation"
    COMMITMENT_DEMAND = "commitment_demand"
    CONTRACT_LEGAL_ASK = "contract_legal_ask"


class TriggerClass(str, Enum):
    """What a trigger is allowed to do (decision D4 / conformance/taxonomy.json).

    - CONTEXT: recorded and shown to the rep; the agent continues.
    - ATTENTION: rep notified as a hot lead; the agent continues (incl. the fit check).
    - INTERVENTION: opens an intervention; the agent stops answering on its own
      until a person resolves it.
    """

    CONTEXT = "context"
    ATTENTION = "attention"
    INTERVENTION = "intervention"


TRIGGER_CLASS: Final[Mapping[str, TriggerClass]] = {
    HandoffTriggerType.HUMAN_REQUEST.value: TriggerClass.INTERVENTION,
    HandoffTriggerType.FRUSTRATION.value: TriggerClass.INTERVENTION,
    HandoffTriggerType.COMMITMENT_DEMAND.value: TriggerClass.INTERVENTION,
    HandoffTriggerType.PRICING_NEGOTIATION.value: TriggerClass.INTERVENTION,
    HandoffTriggerType.CONTRACT_LEGAL_ASK.value: TriggerClass.INTERVENTION,
    HandoffTriggerType.STRONG_BUYING_SIGNAL.value: TriggerClass.ATTENTION,
    HandoffTriggerType.PRICING_DISCUSSION.value: TriggerClass.ATTENTION,
    HandoffTriggerType.COMPETITOR_MENTION.value: TriggerClass.CONTEXT,
    HandoffTriggerType.STAKEHOLDER_APPROVAL_NEEDED.value: TriggerClass.CONTEXT,
}

# Primary-trigger precedence: every intervention outranks every attention
# trigger, which outranks every context trigger. Within a class, earlier wins.
TRIGGER_PRECEDENCE: Final[tuple[str, ...]] = (
    HandoffTriggerType.HUMAN_REQUEST.value,
    HandoffTriggerType.FRUSTRATION.value,
    HandoffTriggerType.COMMITMENT_DEMAND.value,
    HandoffTriggerType.PRICING_NEGOTIATION.value,
    HandoffTriggerType.CONTRACT_LEGAL_ASK.value,
    HandoffTriggerType.STRONG_BUYING_SIGNAL.value,
    HandoffTriggerType.PRICING_DISCUSSION.value,
    HandoffTriggerType.COMPETITOR_MENTION.value,
    HandoffTriggerType.STAKEHOLDER_APPROVAL_NEEDED.value,
)


def trigger_class(trigger_type: str) -> TriggerClass | None:
    return TRIGGER_CLASS.get(trigger_type)


# SLA in minutes (wall-clock targets for rep response).
SLA_MINUTES_BY_TRIGGER: Final[Mapping[str, int]] = {
    HandoffTriggerType.NONE.value: 0,
    HandoffTriggerType.HUMAN_REQUEST.value: 15,
    HandoffTriggerType.PRICING_DISCUSSION.value: 120,
    HandoffTriggerType.STRONG_BUYING_SIGNAL.value: 60,
    HandoffTriggerType.FRUSTRATION.value: 30,
    HandoffTriggerType.COMPETITOR_MENTION.value: 60,
    HandoffTriggerType.STAKEHOLDER_APPROVAL_NEEDED.value: 120,
    HandoffTriggerType.PRICING_NEGOTIATION.value: 60,
    HandoffTriggerType.COMMITMENT_DEMAND.value: 30,
    HandoffTriggerType.CONTRACT_LEGAL_ASK.value: 120,
}

DEFAULT_SLA_MINUTES_UNKNOWN_TRIGGER: Final[int] = 60

# --- Human-intervention policy (soul.md value 4: "humans own commitment-critical moments") ---
#
# Intervention-class triggers are the ones where the agent must stop conversing
# and let a person take over. While one is open the customer only ever
# receives an approved holding response (see ``customer_layer.holding_responses``),
# whether or not the rep is online. Context and attention triggers notify the
# rep but never silence the agent — in particular a buying signal or pricing
# interest before fit is confirmed keeps the fit check running (decision D1).
HUMAN_REQUIRED_TRIGGERS: Final[frozenset[str]] = frozenset(
    t for t, c in TRIGGER_CLASS.items() if c is TriggerClass.INTERVENTION
)

# Frustration whose target is positively identified as something other than
# this agent does not, by itself, require a human. Anything NOT in this set —
# including "current_agent" and "unspecified" — still escalates. Suppressing an
# escalation needs positive evidence; missing evidence escalates.
NON_AGENT_FRUSTRATION_TARGETS: Final[frozenset[str]] = frozenset(
    {"previous_vendor", "internal_process"}
)


def trigger_requires_human(trigger_type: str) -> bool:
    """True when this trigger means a person must take over the conversation."""
    return trigger_type in HUMAN_REQUIRED_TRIGGERS

# Map orchestration trigger -> rep-assist canonical key (RepAssistEngine / alerts).
HANDOFF_TO_REP_BRIEF_KEY: Final[Mapping[str, str]] = {
    HandoffTriggerType.NONE.value: "none",
    HandoffTriggerType.HUMAN_REQUEST.value: "human_request",
    HandoffTriggerType.PRICING_DISCUSSION.value: "pricing",
    HandoffTriggerType.STRONG_BUYING_SIGNAL.value: "buying_intent",
    HandoffTriggerType.FRUSTRATION.value: "frustration",
    HandoffTriggerType.COMPETITOR_MENTION.value: "competitor_mention",
    HandoffTriggerType.STAKEHOLDER_APPROVAL_NEEDED.value: "stakeholder_approval_needed",
    HandoffTriggerType.PRICING_NEGOTIATION.value: "pricing_negotiation",
    HandoffTriggerType.COMMITMENT_DEMAND.value: "commitment_demand",
    HandoffTriggerType.CONTRACT_LEGAL_ASK.value: "contract_legal_ask",
}


def rep_brief_key_for_handoff(trigger_type: str) -> str:
    """Translate HandoffManager trigger name to rep-layer brief key."""
    return HANDOFF_TO_REP_BRIEF_KEY.get(trigger_type, trigger_type)


def sla_minutes_for_trigger(trigger_type: str) -> int:
    """Return SLA minutes for a handoff trigger *or* rep-brief canonical key."""
    if trigger_type in SLA_MINUTES_BY_TRIGGER:
        return SLA_MINUTES_BY_TRIGGER[trigger_type]
    for handoff_key, brief_key in HANDOFF_TO_REP_BRIEF_KEY.items():
        if brief_key == trigger_type and handoff_key in SLA_MINUTES_BY_TRIGGER:
            return SLA_MINUTES_BY_TRIGGER[handoff_key]
    return DEFAULT_SLA_MINUTES_UNKNOWN_TRIGGER


def format_sla_display(minutes: int) -> str:
    """Human-readable SLA for rep UI (briefs, Slack)."""
    if minutes <= 0:
        return "n/a"
    if minutes < 60:
        return f"{minutes} min"
    if minutes % 60 == 0:
        h = minutes // 60
        return f"{h} hour" if h == 1 else f"{h} hours"
    return f"{minutes} min"


# Rep operational actions keyed by *rep brief* canonical names (not handoff names).
REP_ACTION_BY_BRIEF_KEY: Final[Dict[str, str]] = {
    "human_request": (
        "Acknowledge request; join live or reply in-channel within SLA. "
        "Confirm human handoff completed."
    ),
    "pricing": (
        "Deliver pricing/options package or book pricing call. "
        "Log quote version and decision criteria."
    ),
    "buying_intent": (
        "Advance deal: confirm scope, timeline, stakeholders; propose next step "
        "(demo, proposal, or contract)."
    ),
    "frustration": (
        "Take over tone: acknowledge issue, offer escalation path. "
        "Avoid automated-only replies until sentiment stabilizes."
    ),
    "competitor_mention": (
        "Capture competitive context; align positioning and proof points. "
        "Schedule live differentiation if needed."
    ),
    "stakeholder_approval_needed": (
        "Map approval chain and timeline; offer materials for internal sell-in."
    ),
    "pricing_negotiation": (
        "Prospect is negotiating terms (discount / price match). Respond in person; "
        "the agent has not quoted or conceded anything."
    ),
    "commitment_demand": (
        "Prospect asked for a commitment, guarantee or written promise. Only a person "
        "may answer; the agent made no commitment."
    ),
    "contract_legal_ask": (
        "Contract / legal request (redlines, MSA, DPA, terms). Route to deal desk or "
        "legal and confirm owner and timeline with the prospect."
    ),
}

DEFAULT_REP_ACTION: Final[str] = (
    "Triage: classify trigger, align owner, set next touch. "
    "If unclear, message lead with one clarifying question."
)
