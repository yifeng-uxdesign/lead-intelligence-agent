"""Pure adapters: structured extraction -> handoff inputs and trust FSM inputs.

Replace bodies with LLM-backed parsers later without changing orchestrator shape.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Final, Optional, Pattern, Tuple

from src.domain.trigger_catalog import NON_AGENT_FRUSTRATION_TARGETS
from src.signals.extractor import LeadSignals

# Shared lexical hints for pricing (kept in one place; extractor may overlap).
_PRICING_LEXEMES: Final[frozenset[str]] = frozenset(
    ("pricing", "price", "quote", "cost", "budget")
)


# Lexical evidence for intervention triggers the extractor has no label for yet.
# Deliberately narrow: each must mean the prospect wants something only a person
# may give (decision D4). Questions *about* accountability ("who is responsible
# if it's wrong?") or capability ("can you guarantee a lift?") are answered by the
# agent and do not match. Replace with interpreter labels in roadmap step 7.
_NEGOTIATION: Final[Tuple[Pattern[str], ...]] = tuple(re.compile(p, re.I) for p in (
    r"\bdiscount",
    r"\b\d+\s?%\s?off\b",
    r"\bcheaper\b",
    r"\b(lower|better|best|reduced?)\s+(the\s+)?(price|rate|deal|offer|quote)\b",
    r"\bnegotiat",
    r"\bprice[- ]match",
    r"\bmatch\s+(their|the|a|that)\s+(price|quote|offer)\b",
    r"\bwaive\b",
))
_COMMITMENT: Final[Tuple[Pattern[str], ...]] = tuple(re.compile(p, re.I) for p in (
    r"\bin writing\b",
    r"\bwritten\s+(guarantee|commitment|promise)\b",
    r"\brefund\b",
    r"\bmoney[- ]back\b",
))
_CONTRACT_LEGAL: Final[Tuple[Pattern[str], ...]] = tuple(re.compile(p, re.I) for p in (
    r"\bcontract",
    r"\bredline",
    r"\bmsa\b",
    r"\bmaster services?\s+agreement\b",
    r"\bdpa\b",
    r"\bdata processing agreement\b",
    r"\bterms\s+(and|&)\s+conditions\b",
    r"\bindemnif",
    r"\bliability cap\b",
))


def _first_match(patterns: Tuple[Pattern[str], ...], text: str) -> Optional[str]:
    for rx in patterns:
        m = rx.search(text)
        if m:
            return m.group(0)
    return None


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
    """Build HandoffManager input from extraction + raw text.

    ``_evidence`` maps each lexically-detected trigger key to the text that
    matched, so the decision trace can say *why* it fired.
    """
    raw = raw_message or ""
    lower = raw.lower()
    evidence: Dict[str, str] = {}

    pricing_word = next((w for w in _PRICING_LEXEMES if w in lower), None)
    if pricing_word:
        evidence["pricing_discussion"] = f"text '{pricing_word}'"
    elif lead.objection_type == "price":
        evidence["pricing_discussion"] = "objection_type=price"

    detected = {}
    for key, patterns in (
        ("pricing_negotiation", _NEGOTIATION),
        ("commitment_demand", _COMMITMENT),
        ("contract_legal_ask", _CONTRACT_LEGAL),
    ):
        hit = _first_match(patterns, raw)
        detected[key] = hit is not None
        if hit is not None:
            evidence[key] = f"text '{hit}'"

    return {
        "human_request": lead.human_request,
        "pricing_discussion": "pricing_discussion" in evidence,
        "strong_buying_signal": lead.buying_signal,
        "sentiment": lead.sentiment,
        "sentiment_target": lead.sentiment_target,
        "competitor_mention": lead.competitor_mention,
        "stakeholder_approval_needed": lead.stakeholder_signal,
        **detected,
        "_evidence": evidence,
    }
