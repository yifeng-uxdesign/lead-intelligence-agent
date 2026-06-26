"""Signal extraction from raw customer messages.

Rule-based v1: keyword / phrase matching with small pure helpers.
Replace ``LeadSignalExtractor.extract`` internals with LLM calls later without
changing the public ``LeadSignals`` shape.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import FrozenSet


def _normalize(text: str) -> str:
    """Lowercase and collapse whitespace for matching."""
    return re.sub(r"\s+", " ", text.strip().lower())


def _contains_any(haystack: str, needles: FrozenSet[str]) -> bool:
    return any(n in haystack for n in needles)


# --- Replaceable rule functions (LLM can mirror this contract later) ---


def extract_intent_from_text(text: str) -> str:
    """Coarse intent label from lexical cues."""
    t = _normalize(text)
    if _contains_any(
        t,
        frozenset(
            {
                "ready to buy",
                "purchase",
                "sign up",
                "signup",
                "contract",
                "get started",
                "book a demo",
                "schedule a call",
            }
        ),
    ):
        return "buy"
    if _contains_any(
        t,
        frozenset(
            {
                "cancel",
                "refund",
                "not working",
                "broken",
                "bug",
                "support",
                "help me fix",
            }
        ),
    ):
        return "support"
    if _contains_any(
        t,
        frozenset(
            {
                "compare",
                "vs ",
                "versus",
                "alternative",
                "evaluation",
                "pilot",
                "trial",
            }
        ),
    ):
        return "evaluate"
    if _contains_any(
        t,
        frozenset({"just looking", "curious", "tell me more", "what is", "how does"}),
    ):
        return "explore"
    return "general"


def extract_urgency_from_text(text: str) -> str:
    t = _normalize(text)
    if _contains_any(
        t,
        frozenset(
            {
                "asap",
                "urgent",
                "immediately",
                "today",
                "this week",
                "eod",
                "deadline",
                "critical",
            }
        ),
    ):
        return "high"
    if _contains_any(
        t,
        frozenset({"when you can", "no rush", "next quarter", "eventually", "sometime"}),
    ):
        return "low"
    return "medium"


def extract_sentiment_from_text(text: str) -> str:
    t = _normalize(text)
    if _contains_any(
        t,
        frozenset(
            {
                "frustrated",
                "frustrating",
                "ridiculous",
                "unacceptable",
                "angry",
                "fed up",
                "waste of time",
            }
        ),
    ):
        return "frustration"
    if _contains_any(
        t,
        frozenset({"love", "great", "thanks", "appreciate", "excited", "perfect"}),
    ):
        return "positive"
    if _contains_any(
        t,
        frozenset({"disappointed", "concerned", "worried", "not sure", "unhappy"}),
    ):
        return "negative"
    return "neutral"


def extract_objection_type_from_text(text: str) -> str:
    """Return a coarse objection bucket or ``none``."""
    t = _normalize(text)
    if _contains_any(
        t,
        frozenset(
            {
                "too expensive",
                "over budget",
                "cheaper",
                "discount",
                "price",
                "cost",
                "roi",
            }
        ),
    ):
        return "price"
    if _contains_any(
        t,
        frozenset({"not now", "next year", "timeline", "too soon", "timing", "later"}),
    ):
        return "timing"
    if _contains_any(
        t,
        frozenset({"don't trust", "scam", "security", "privacy"}),
    ) or re.search(r"\bprove\b", t):
        return "trust"
    if _contains_any(
        t,
        frozenset({"missing feature", "doesn't integrate", "need integration", "gap"}),
    ):
        return "capability"
    return "none"


def detect_human_request(text: str) -> bool:
    t = _normalize(text)
    return _contains_any(
        t,
        frozenset(
            {
                "talk to a human",
                "speak to a person",
                "real person",
                "human being",
                "call me",
                "agent",
                "representative",
                "customer service",
            }
        ),
    )


def detect_competitor_mention(text: str) -> bool:
    t = _normalize(text)
    return _contains_any(
        t,
        frozenset(
            {
                "competitor",
                "competition",
                "alternative to",
                "instead of",
                "we use",
                "salesforce",
                "hubspot",
                "gong",
                "zoominfo",
            }
        ),
    )


def detect_buying_signal(text: str) -> bool:
    t = _normalize(text)
    return _contains_any(
        t,
        frozenset(
            {
                "ready to move forward",
                "send the proposal",
                "send a quote",
                "purchase order",
                "po ",
                "sign the",
                "finalize",
                "close the deal",
                "budget approved",
            }
        ),
    )


def detect_stakeholder_signal(text: str) -> bool:
    t = _normalize(text)
    return _contains_any(
        t,
        frozenset(
            {
                "my boss",
                "my manager",
                "approval",
                "approve",
                "legal",
                "procurement",
                "committee",
                "board",
                "cfo",
                "need sign-off",
                "sign off",
            }
        ),
    )


@dataclass(frozen=True)
class LeadSignals:
    """Structured signals extracted from one customer message."""

    intent: str
    urgency: str
    sentiment: str
    objection_type: str
    human_request: bool
    competitor_mention: bool
    buying_signal: bool
    stakeholder_signal: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "intent": self.intent,
            "urgency": self.urgency,
            "sentiment": self.sentiment,
            "objection_type": self.objection_type,
            "human_request": self.human_request,
            "competitor_mention": self.competitor_mention,
            "buying_signal": self.buying_signal,
            "stakeholder_signal": self.stakeholder_signal,
        }


class LeadSignalExtractor:
    """Extracts lead signals from raw customer text (rule-based v1)."""

    def extract(self, message: str) -> LeadSignals:
        if not message or not str(message).strip():
            return LeadSignals(
                intent="general",
                urgency="medium",
                sentiment="neutral",
                objection_type="none",
                human_request=False,
                competitor_mention=False,
                buying_signal=False,
                stakeholder_signal=False,
            )

        text = str(message)
        return LeadSignals(
            intent=extract_intent_from_text(text),
            urgency=extract_urgency_from_text(text),
            sentiment=extract_sentiment_from_text(text),
            objection_type=extract_objection_type_from_text(text),
            human_request=detect_human_request(text),
            competitor_mention=detect_competitor_mention(text),
            buying_signal=detect_buying_signal(text),
            stakeholder_signal=detect_stakeholder_signal(text),
        )
