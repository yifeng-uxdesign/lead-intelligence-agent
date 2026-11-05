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
        frozenset(
            {
                "don't trust",
                "scam",
                "security",
                "privacy",
                # Skepticism about the product category. This is an objection to
                # validate (OBJECTION trust state), not frustration to escalate.
                "not convinced",
                "skeptical",
                "sceptical",
                "burned before",
                "i doubt",
            }
        ),
    ) or re.search(r"\bprove\b", t):
        return "trust"
    if _contains_any(
        t,
        frozenset({"missing feature", "doesn't integrate", "need integration", "gap"}),
    ):
        return "capability"
    return "none"


# Phrases that unambiguously ask for a person. Bare "agent" is intentionally NOT
# here: for an AI-agent product, "tell me about your AI agent" is not a request
# for a human. Requests to reach an agent are matched by the patterns below.
_HUMAN_REQUEST_PHRASES: FrozenSet[str] = frozenset(
    {
        "talk to a human",
        "speak to a person",
        "call me",
        "representative",
        "customer service",
    }
)

# "Am I talking to a real person?" is an identity question, not a request for
# one. These only count as a human request when the message is not an identity
# question (soul.md value 6: answer sincere identity questions truthfully).
_AMBIGUOUS_HUMAN_PHRASES: FrozenSet[str] = frozenset({"real person", "human being"})

_HUMAN_REQUEST_PATTERNS = (
    # "talk to an agent", "speak with a real person", "chat with a rep"
    re.compile(
        r"\b(?:talk|speak|chat)\s+(?:to|with)\s+(?:an?\s+|the\s+)?"
        r"(?:real\s+|live\s+|human\s+)?(?:agent|person|human|representative|rep|salesperson|sales\s?rep)\b"
    ),
    # "speak with someone on your sales team" (YOUR side, not "someone in finance")
    re.compile(
        r"\b(?:talk|speak|chat)\s+(?:to|with)\s+(?:someone|somebody)\s+"
        r"(?:on|from|at|in)\s+(?:your|the)\s+(?:sales\s+)?(?:team|company|staff)\b"
    ),
    re.compile(r"\b(?:live|human)\s+agent\b"),
    re.compile(r"\bget\s+me\s+(?:an?\s+)?(?:real\s+|live\s+|human\s+)?(?:agent|human|person|rep|representative)\b"),
    re.compile(
        r"\bconnect\s+me\s+(?:to|with)\s+(?:an?\s+|your\s+|the\s+)?"
        r"(?:agent|human|person|rep|representative|sales\s+team|someone)\b"
    ),
)


_IDENTITY_QUESTION_PATTERNS = (
    re.compile(
        r"\bare you (?:even |actually |really |just )?(?:a |an )?(?:real |actual |live )?"
        r"(?:human|person|bot|robot|ai|chatbot|machine|automated)\b"
    ),
    re.compile(
        r"\b(?:am i|are we)\s+(?:talking|speaking|chatting)\s+(?:to|with)\s+"
        r"(?:a |an )?(?:real |actual |live )?(?:human|person|bot|robot|ai|chatbot|machine)\b"
    ),
    re.compile(
        r"\bis this\s+(?:a |an )?(?:real |live )?"
        r"(?:human|person|bot|robot|ai|chatbot|automated)\b"
    ),
)


def detect_identity_question(text: str) -> bool:
    """Is the prospect asking whether they are talking to a human or an AI?"""
    t = _normalize(text)
    return any(p.search(t) for p in _IDENTITY_QUESTION_PATTERNS)


def detect_human_request(text: str) -> bool:
    t = _normalize(text)
    if _contains_any(t, _HUMAN_REQUEST_PHRASES):
        return True
    if any(p.search(t) for p in _HUMAN_REQUEST_PATTERNS):
        return True
    return _contains_any(t, _AMBIGUOUS_HUMAN_PHRASES) and not detect_identity_question(text)


# --- Who is the negative sentiment aimed at? --------------------------------
#
# soul.md value 4 makes *emotional frustration* a human moment, but frustration
# about a previous vendor or the prospect's own process is discovery material,
# not a signal that this agent is failing them.
#
# Asymmetry (deliberate): agent-directed cues win over everything, and when no
# target can be identified the result is "unspecified", which still escalates.
# Only a *positively identified* non-agent target can suppress an escalation.

_AGENT_DIRECTED_PATTERNS = (
    re.compile(
        r"\byou(?:'re| are| keep| aren't| are not| don't| do not| didn't| did not|"
        r" never| still| just| won't| can't| cannot| haven't| have not)\b"
    ),
    re.compile(r"\byour\s+(?:answers?|responses?|repl(?:y|ies)|bot|chatbot|assistant|ai)\b"),
    re.compile(r"\bthis\s+(?:bot|chatbot|assistant|agent|ai|chat|conversation)\b"),
    re.compile(
        r"\b(?:not listening|going in circles|talking to a wall|useless|"
        r"same question|not helping|not understanding|don't understand me)\b"
    ),
)

_PREVIOUS_VENDOR_PATTERNS = (
    re.compile(
        r"\b(?:previous|prior|last|former|old|earlier|other|another)\s+(?:ai\s+)?"
        r"(?:vendors?|providers?|tools?|solutions?|platforms?|systems?|products?|compan(?:y|ies))\b"
    ),
    re.compile(r"\bwe\s+(?:tried|used|had tried|switched from|dropped|left)\b"),
)

_INTERNAL_PROCESS_PATTERNS = (
    re.compile(
        r"\bour\s+(?:own\s+)?(?:sales\s+|lead\s+|qualification\s+)?"
        r"(?:process(?:es)?|workflows?|reps?|team|pipeline|crm|data|handoffs?)\b"
    ),
    re.compile(r"\b(?:internally|my team)\b"),
)


def detect_sentiment_target(text: str) -> str:
    """Who negative sentiment is aimed at.

    Returns one of ``current_agent``, ``previous_vendor``, ``internal_process``,
    ``unspecified``. Precedence is fixed: current_agent > previous_vendor >
    internal_process > unspecified.
    """
    t = _normalize(text)
    if any(p.search(t) for p in _AGENT_DIRECTED_PATTERNS):
        return "current_agent"
    if any(p.search(t) for p in _PREVIOUS_VENDOR_PATTERNS):
        return "previous_vendor"
    if any(p.search(t) for p in _INTERNAL_PROCESS_PATTERNS):
        return "internal_process"
    return "unspecified"


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
    # Target of negative sentiment. Only meaningful when ``sentiment`` is
    # "frustration"/"negative". Default keeps older call sites constructing
    # LeadSignals(...) positionally/by keyword unchanged.
    sentiment_target: str = "unspecified"
    # Prospect asked whether they're talking to a human or an AI (soul.md value 6).
    identity_question: bool = False

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
            "sentiment_target": self.sentiment_target,
            "identity_question": self.identity_question,
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
            sentiment_target=detect_sentiment_target(text),
            identity_question=detect_identity_question(text),
        )
