"""Fit criteria for Sierra AI agentic customer service platform.

This module provides structured fit evaluation data used by the orchestrator
to set ``fit_confirmed`` in signals before ``DECISION_READY`` is reached.

**Relationship to product_context.md:**
``product_context.md`` is the human-readable, LLM-readable signal vocabulary
injected into the system prompt. This file is the machine-readable version
used for programmatic fit scoring in the qualification layer.

**Relationship to soul.md:**
soul.md conflict hierarchy priority 2: "do not harm the prospect's interest."
The hard disqualifiers in this file enforce that value at the data layer —
if any hard disqualifier matches, fit_confirmed must never be set to True
regardless of other positive signals or pipeline pressure.

**Usage:**
    from src.clients.sierra.fit_criteria import SIERRA_FIT_CRITERIA, evaluate_fit

    score, reasons = evaluate_fit(prospect_signals, SIERRA_FIT_CRITERIA)
    fit_confirmed = score >= SIERRA_FIT_CRITERIA.confirmation_threshold
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class FitSignalWeight(int, Enum):
    """Relative weight of a fit signal in the overall score.

    STRONG    — alone is meaningful evidence of fit or misfit
    MODERATE  — contributes but not conclusive alone
    WEAK      — directional but requires corroboration
    """
    STRONG = 3
    MODERATE = 2
    WEAK = 1


@dataclass(frozen=True)
class FitSignal:
    """A single observable signal that indicates good or poor fit."""
    key: str                        # signal key matched against prospect_signals dict
    description: str                # human-readable label for logging and rep briefs
    weight: FitSignalWeight         # contribution to fit score
    example_phrases: List[str]      # what a prospect might say — used for LLM extraction
    counter_signals: List[str] = field(default_factory=list)
    # Keys of signals that partially cancel this one if also present


@dataclass(frozen=True)
class HardDisqualifier:
    """A signal that blocks fit_confirmed regardless of positive signals.

    soul.md conflict hierarchy priority 2: if any hard disqualifier matches,
    the prospect must never be handed off with fit implied. The agent must
    surface the mismatch honestly before any handoff template is rendered.
    """
    key: str
    description: str
    honest_response_hint: str       # what the agent should say if this fires
    example_phrases: List[str]


@dataclass
class FitCriteria:
    """Complete fit evaluation specification for one client product.

    The orchestrator uses this to score a prospect's signals and determine
    whether fit_confirmed can be set to True before DECISION_READY.
    """
    client_id: str
    product_name: str
    good_fit_signals: List[FitSignal]
    poor_fit_signals: List[FitSignal]
    hard_disqualifiers: List[HardDisqualifier]
    confirmation_threshold: int     # minimum score required to set fit_confirmed=True
    disqualification_threshold: int # score at or below which agent should surface mismatch


# ---------------------------------------------------------------------------
# Sierra AI — good fit signals
# ---------------------------------------------------------------------------

_SIERRA_GOOD_FIT_SIGNALS: List[FitSignal] = [

    FitSignal(
        key="high_support_volume",
        description="Support volume exceeds 1,000 contacts per month",
        weight=FitSignalWeight.STRONG,
        example_phrases=[
            "we handle thousands of tickets",
            "our volume is really high",
            "we're getting overwhelmed with contacts",
            "we have over a thousand support requests a month",
            "our queue never empties",
        ],
    ),

    FitSignal(
        key="repetitive_ticket_types",
        description="Significant portion of tickets are repetitive and low-complexity",
        weight=FitSignalWeight.STRONG,
        example_phrases=[
            "most tickets are returns",
            "we get the same questions over and over",
            "order status questions take up half our day",
            "billing questions are constant",
            "password resets, account changes — that's most of what we do",
        ],
    ),

    FitSignal(
        key="existing_helpdesk_or_crm",
        description="Uses an existing CRM or helpdesk (Salesforce, Zendesk, Intercom, etc.)",
        weight=FitSignalWeight.STRONG,
        example_phrases=[
            "we use zendesk",
            "we're on salesforce",
            "our team uses intercom",
            "freshdesk is our ticketing system",
            "we have hubspot for support",
        ],
    ),

    FitSignal(
        key="wants_autonomous_resolution",
        description="Prospect wants AI to resolve issues, not just triage or answer",
        weight=FitSignalWeight.STRONG,
        example_phrases=[
            "we want it to actually solve the problem",
            "not just a chatbot that routes tickets",
            "we need it to process refunds automatically",
            "close the ticket without a human",
            "handle the whole interaction end to end",
        ],
    ),

    FitSignal(
        key="scale_pressure",
        description="Support costs growing, CSAT declining, or wait times increasing",
        weight=FitSignalWeight.MODERATE,
        example_phrases=[
            "our support costs are out of control",
            "customers are complaining about wait times",
            "CSAT has been dropping",
            "we can't hire fast enough",
            "the team is burning out",
            "we're spending too much on support headcount",
        ],
    ),

    FitSignal(
        key="consumer_facing",
        description="Sells directly to end consumers (B2C or B2B2C)",
        weight=FitSignalWeight.MODERATE,
        example_phrases=[
            "we sell direct to consumers",
            "our customers are everyday people",
            "we're a consumer brand",
            "retail customers",
            "end users reaching out directly",
        ],
    ),

    FitSignal(
        key="support_team_size_adequate",
        description="Support team of 10 or more, or smaller team overwhelmed by volume",
        weight=FitSignalWeight.MODERATE,
        example_phrases=[
            "we have a team of fifteen agents",
            "only five people handling way too much",
            "our support org is growing fast",
            "small team but huge volume",
        ],
    ),

    FitSignal(
        key="pilot_mindset",
        description="Prospect is open to a defined pilot before full commitment",
        weight=FitSignalWeight.WEAK,
        example_phrases=[
            "we'd want to test it first",
            "a pilot sounds reasonable",
            "can we start with one ticket category",
            "we'd need to see results before rolling out",
        ],
    ),

    FitSignal(
        key="budget_signal",
        description="Prospect references support cost reduction as a goal or board priority",
        weight=FitSignalWeight.WEAK,
        example_phrases=[
            "we have budget for this",
            "support efficiency is a board priority",
            "we're actively trying to reduce headcount costs",
            "there's budget allocated for tooling",
        ],
        counter_signals=["budget_concern"],
    ),
]


# ---------------------------------------------------------------------------
# Sierra AI — poor fit signals (negative score contribution)
# ---------------------------------------------------------------------------

_SIERRA_POOR_FIT_SIGNALS: List[FitSignal] = [

    FitSignal(
        key="very_low_volume",
        description="Fewer than 500 contacts per month — automation ROI not justified",
        weight=FitSignalWeight.STRONG,
        example_phrases=[
            "we only get a few hundred tickets a month",
            "volume is pretty low",
            "maybe fifty tickets a week",
            "our team can handle it manually",
        ],
    ),

    FitSignal(
        key="purely_complex_cases",
        description="Every issue requires deep human judgment or regulatory expertise",
        weight=FitSignalWeight.STRONG,
        example_phrases=[
            "every case is unique",
            "our issues are too complex for automation",
            "we deal with legal disputes",
            "medical questions that need a professional",
            "highly regulated and everything needs a human review",
        ],
    ),

    FitSignal(
        key="no_existing_systems",
        description="No CRM, helpdesk, or ticketing system — no integration surface",
        weight=FitSignalWeight.STRONG,
        example_phrases=[
            "we don't have a CRM yet",
            "we use spreadsheets for tracking",
            "no ticketing system in place",
            "email inbox is all we have",
        ],
    ),

    FitSignal(
        key="enterprise_b2b_only",
        description="All customers are large enterprises with bespoke contracts",
        weight=FitSignalWeight.MODERATE,
        example_phrases=[
            "all our clients are Fortune 500",
            "we only work with enterprise accounts",
            "every customer has a dedicated account manager",
            "purely B2B, no consumer side",
        ],
    ),

    FitSignal(
        key="resistant_to_ai_autonomy",
        description="Prospect only wants triage or Q&A, not autonomous resolution",
        weight=FitSignalWeight.MODERATE,
        example_phrases=[
            "we don't want it making decisions",
            "just route to the right agent",
            "human should always approve",
            "we're not ready to let AI take action",
            "chatbot that answers FAQs is enough",
        ],
    ),

    FitSignal(
        key="budget_concern",
        description="Prospect signals budget is not available or premature",
        weight=FitSignalWeight.WEAK,
        example_phrases=[
            "we don't have budget for this right now",
            "too early stage to invest",
            "we're bootstrapped, can't afford enterprise tools",
        ],
        counter_signals=["budget_signal"],
    ),
]


# ---------------------------------------------------------------------------
# Sierra AI — hard disqualifiers
# soul.md conflict hierarchy priority 2: these block fit_confirmed entirely.
# ---------------------------------------------------------------------------

_SIERRA_HARD_DISQUALIFIERS: List[HardDisqualifier] = [

    HardDisqualifier(
        key="no_api_access",
        description="Company systems have no API access — integration is impossible",
        honest_response_hint=(
            "Sierra integrates with your existing systems via API. If your current "
            "tools don't support API access, we wouldn't be able to connect the agent "
            "to take actions on your behalf — which is core to how it works. "
            "It might be worth exploring whether your systems can be upgraded first."
        ),
        example_phrases=[
            "our system has no API",
            "completely closed system",
            "no way to integrate externally",
            "legacy software with no API access",
        ],
    ),

    HardDisqualifier(
        key="no_knowledge_base",
        description="No documented policies or processes exist to train the agent on",
        honest_response_hint=(
            "Sierra learns from your existing knowledge base, policies, and documented "
            "processes. If those don't exist yet, the agent won't have anything to "
            "work from — and building that foundation typically takes time. It might "
            "be worth focusing on documenting your support processes first."
        ),
        example_phrases=[
            "nothing is written down",
            "all knowledge is in people's heads",
            "no documentation at all",
            "we've never documented our processes",
        ],
    ),

    HardDisqualifier(
        key="crisis_or_sensitive_only",
        description="Use case is entirely crisis, medical, or emotionally sensitive cases",
        honest_response_hint=(
            "Sierra isn't designed for cases that are primarily emotionally sensitive "
            "or crisis-level — those require human judgment and care that an AI agent "
            "shouldn't replicate. If that's the core of your support work, we're "
            "probably not the right fit."
        ),
        example_phrases=[
            "we handle crisis calls",
            "mental health support line",
            "medical emergency triage",
            "domestic abuse cases",
            "grief counseling",
        ],
    ),

    HardDisqualifier(
        key="regulatory_prohibition",
        description="Industry regulation prohibits AI-driven autonomous customer actions",
        honest_response_hint=(
            "Some regulated industries have specific rules about AI making autonomous "
            "decisions in customer interactions. If your legal or compliance team has "
            "flagged this as a prohibition rather than a hurdle, that's something we "
            "can't work around — and I'd rather be upfront about that now."
        ),
        example_phrases=[
            "our compliance team has prohibited AI agents",
            "regulator has told us no automated decisions",
            "legally we can't use AI for customer actions",
            "FCA rules out autonomous AI for our use case",
        ],
    ),
]


# ---------------------------------------------------------------------------
# Sierra fit criteria — assembled instance
# ---------------------------------------------------------------------------

SIERRA_FIT_CRITERIA = FitCriteria(
    client_id="sierra-ai",
    product_name="Sierra AI — agentic customer service platform",
    good_fit_signals=_SIERRA_GOOD_FIT_SIGNALS,
    poor_fit_signals=_SIERRA_POOR_FIT_SIGNALS,
    hard_disqualifiers=_SIERRA_HARD_DISQUALIFIERS,
    # Score threshold rationale:
    # Max possible good-fit score = 3+3+3+3+2+2+2+1+1 = 20
    # confirmation_threshold=8 requires at least two STRONG signals or one
    # STRONG + two MODERATE — meaningful evidence, not a single data point.
    confirmation_threshold=8,
    # disqualification_threshold=-4 means two STRONG poor-fit signals, or
    # one STRONG + one MODERATE, triggers honest mismatch surfacing.
    disqualification_threshold=-4,
)


# ---------------------------------------------------------------------------
# Fit evaluation function — used by orchestrator to set fit_confirmed
# ---------------------------------------------------------------------------

def evaluate_fit(
    prospect_signals: Dict[str, bool],
    criteria: FitCriteria = SIERRA_FIT_CRITERIA,
) -> Tuple[int, List[str]]:
    """Score prospect signals against fit criteria and return score + reasons.

    Args:
        prospect_signals: Dict of signal keys to bool. True = signal present.
            Keys must match FitSignal.key or HardDisqualifier.key values.
        criteria: FitCriteria instance to evaluate against.
            Defaults to SIERRA_FIT_CRITERIA.

    Returns:
        Tuple of (score: int, reasons: List[str]) where:
        - score > criteria.confirmation_threshold → fit_confirmed = True
        - score <= criteria.disqualification_threshold → surface mismatch
        - Any hard disqualifier present → fit_confirmed = False unconditionally

    Example:
        signals = {
            "high_support_volume": True,
            "repetitive_ticket_types": True,
            "existing_helpdesk_or_crm": True,
        }
        score, reasons = evaluate_fit(signals)
        fit_confirmed = score >= SIERRA_FIT_CRITERIA.confirmation_threshold
        # score = 9 (3+3+3), fit_confirmed = True
    """
    reasons: List[str] = []
    score: int = 0

    # Hard disqualifiers checked first — any match blocks fit entirely.
    # soul.md conflict hierarchy priority 2: prospect interest before pipeline.
    for disqualifier in criteria.hard_disqualifiers:
        if prospect_signals.get(disqualifier.key, False):
            reasons.append(
                f"HARD DISQUALIFIER: {disqualifier.description} — "
                f"fit_confirmed must be False. "
                f"Suggested response: {disqualifier.honest_response_hint}"
            )
            return -999, reasons  # unconditional block regardless of positive signals

    # Score good fit signals
    for signal in criteria.good_fit_signals:
        if prospect_signals.get(signal.key, False):
            contribution = signal.weight.value
            # Reduce contribution if counter-signals are also present
            for counter_key in signal.counter_signals:
                if prospect_signals.get(counter_key, False):
                    contribution = max(0, contribution - 1)
            score += contribution
            reasons.append(f"GOOD FIT (+{contribution}): {signal.description}")

    # Score poor fit signals (negative contribution)
    for signal in criteria.poor_fit_signals:
        if prospect_signals.get(signal.key, False):
            contribution = signal.weight.value
            for counter_key in signal.counter_signals:
                if prospect_signals.get(counter_key, False):
                    contribution = max(0, contribution - 1)
            score -= contribution
            reasons.append(f"POOR FIT (-{contribution}): {signal.description}")

    return score, reasons


def fit_summary(
    prospect_signals: Dict[str, bool],
    criteria: FitCriteria = SIERRA_FIT_CRITERIA,
) -> Dict[str, object]:
    """Return a structured fit assessment for orchestrator or rep brief use.

    Returns a dict with:
    - fit_confirmed (bool): whether score clears confirmation threshold
    - should_surface_mismatch (bool): whether agent should raise poor fit
    - score (int): raw fit score
    - reasons (List[str]): human-readable signal breakdown
    - hard_blocked (bool): True if a hard disqualifier fired
    """
    score, reasons = evaluate_fit(prospect_signals, criteria)
    hard_blocked = score == -999

    return {
        "fit_confirmed": (not hard_blocked) and (score >= criteria.confirmation_threshold),
        "should_surface_mismatch": hard_blocked or (score <= criteria.disqualification_threshold),
        "score": score,
        "reasons": reasons,
        "hard_blocked": hard_blocked,
    }
