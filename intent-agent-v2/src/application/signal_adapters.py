"""Pure adapters: structured extraction -> handoff inputs and trust FSM inputs.

Replace bodies with LLM-backed parsers later without changing orchestrator shape.
"""

from __future__ import annotations

from typing import Any, Dict, Final

from src.domain.trigger_catalog import NON_AGENT_FRUSTRATION_TARGETS
from src.signals.extractor import LeadSignals

# Shared lexical hints for pricing (kept in one place; extractor may overlap).
_PRICING_LEXEMES: Final[frozenset[str]] = frozenset(
    ("pricing", "price", "quote", "cost", "budget")
)


def lead_signals_to_trust_signals(lead: LeadSignals) -> Dict[str, Any]:
    """Map ``LeadSignals`` to TrustStateMachine.transition keyword arguments."""
    intent = str(lead.intent).strip().lower()
    if intent in ("general",):
        intent = "explore"
    if intent == "evaluate":
        intent = "explore"

    trust_score = 0.55
    if lead.sentiment == "positive":
        trust_score = 0.82
    elif lead.sentiment in ("negative", "frustration"):
        # Dissatisfaction aimed at a previous vendor or the prospect's own
        # process is evidence about *that*, not about trust in this agent.
        if lead.sentiment_target in NON_AGENT_FRUSTRATION_TARGETS:
            trust_score = 0.55
        else:
            trust_score = 0.28

    return {
        "intent": intent,
        "objection": lead.objection_type != "none",
        "urgency": lead.urgency,
        "trust_score": trust_score,
        "strong_buying_signal": lead.buying_signal,
    }


def handoff_signal_dict_from_lead(lead: LeadSignals, raw_message: str) -> Dict[str, Any]:
    """Build HandoffManager.should_trigger input from extraction + raw text."""
    lower = raw_message.lower()
    pricing_hit = lead.objection_type == "price" or any(
        w in lower for w in _PRICING_LEXEMES
    )
    return {
        "human_request": lead.human_request,
        "pricing_discussion": pricing_hit,
        "strong_buying_signal": lead.buying_signal,
        "sentiment": lead.sentiment,
        "sentiment_target": lead.sentiment_target,
        "competitor_mention": lead.competitor_mention,
        "stakeholder_approval_needed": lead.stakeholder_signal,
    }
