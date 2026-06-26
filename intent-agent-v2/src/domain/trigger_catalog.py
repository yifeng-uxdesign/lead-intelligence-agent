"""Single source of truth for handoff triggers, SLA targets, and rep-brief mapping.

Customer-facing code should never import rep-specific copy from here; rep layer
consumes SLA minutes and display strings derived from this catalog.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, Final, Mapping

# --- Canonical handoff trigger identifiers (orchestrator + HandoffManager) ---


class HandoffTriggerType(str, Enum):
    """Ordered evaluation is implemented in HandoffManager.should_trigger."""

    NONE = "none"
    HUMAN_REQUEST = "human_request"
    PRICING_DISCUSSION = "pricing_discussion"
    STRONG_BUYING_SIGNAL = "strong_buying_signal"
    FRUSTRATION = "frustration"
    COMPETITOR_MENTION = "competitor_mention"
    STAKEHOLDER_APPROVAL_NEEDED = "stakeholder_approval_needed"


# SLA in minutes (wall-clock targets for rep response).
SLA_MINUTES_BY_TRIGGER: Final[Mapping[str, int]] = {
    HandoffTriggerType.NONE.value: 0,
    HandoffTriggerType.HUMAN_REQUEST.value: 15,
    HandoffTriggerType.PRICING_DISCUSSION.value: 120,
    HandoffTriggerType.STRONG_BUYING_SIGNAL.value: 60,
    HandoffTriggerType.FRUSTRATION.value: 30,
    HandoffTriggerType.COMPETITOR_MENTION.value: 60,
    HandoffTriggerType.STAKEHOLDER_APPROVAL_NEEDED.value: 120,
}

DEFAULT_SLA_MINUTES_UNKNOWN_TRIGGER: Final[int] = 60

# Map orchestration trigger -> rep-assist canonical key (RepAssistEngine / alerts).
HANDOFF_TO_REP_BRIEF_KEY: Final[Mapping[str, str]] = {
    HandoffTriggerType.NONE.value: "none",
    HandoffTriggerType.HUMAN_REQUEST.value: "human_request",
    HandoffTriggerType.PRICING_DISCUSSION.value: "pricing",
    HandoffTriggerType.STRONG_BUYING_SIGNAL.value: "buying_intent",
    HandoffTriggerType.FRUSTRATION.value: "frustration",
    HandoffTriggerType.COMPETITOR_MENTION.value: "competitor_mention",
    HandoffTriggerType.STAKEHOLDER_APPROVAL_NEEDED.value: "stakeholder_approval_needed",
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
}

DEFAULT_REP_ACTION: Final[str] = (
    "Triage: classify trigger, align owner, set next touch. "
    "If unclear, message lead with one clarifying question."
)
