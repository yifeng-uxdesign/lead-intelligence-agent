"""Persona tests: archetypal prospect conversation simulations.

These tests simulate real human variation across six distinct prospect types.
Each persona runs a scripted conversation sequence and asserts that the agent's
responses stay within soul.md constraints throughout.

Personas:
  P1 — The Skeptic          Tests honesty and non-defensiveness under pressure
  P2 — The Eager Buyer      Tests fit validation despite positive momentum
  P3 — The Ghoster          Tests patience when prospect goes silent
  P4 — The Frustrated One   Tests frustration escalation and rep handoff
  P5 — The Poor Fit         Tests honest disqualification without rejection
  P6 — The Human Requester  Tests immediate human handoff on request

Each persona test follows the same structure:
  1. Build a LeadContext representing the prospect's starting state
  2. Run a scripted turn sequence through the behavior engine
  3. Assert soul.md constraints hold at each turn and at end state

How to read failures:
  A failing persona test means a soul.md value is not being upheld under
  a realistic conversation pattern — not just in isolation. Fix the behavior
  layer, then re-run. Do not adjust the persona test to match broken behavior.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import pytest

from src.collaboration.handoff_manager import HandoffManager
from src.collaboration.mode_state_machine import CollaborationMode, ModeStateMachine
from src.core.handoff_queue import HandoffQueue
from src.core.lead_context import LeadContext
from src.customer_layer.behavior_engine import (
    CustomerBehaviorEngine,
    _FIT_CHECK_RESPONSE,
)
from src.customer_layer.trust_state_machine import TrustState, TrustStateMachine
from src.rep_layer.rep_assist_engine import RepAssistEngine, _FRUSTRATION_URGENCY_OVERRIDE


# ---------------------------------------------------------------------------
# Shared test infrastructure
# ---------------------------------------------------------------------------

@dataclass
class ConversationTurn:
    """One turn in a scripted persona conversation."""
    description: str                    # human-readable label for the turn
    signals: Dict[str, Any]             # signals passed to generate_response
    expected_soul_constraints: List[str] = field(default_factory=list)
    # Each constraint is a key checked in _assert_turn_constraints below


@dataclass
class PersonaResult:
    """Collected outputs from running a persona conversation."""
    responses: List[str] = field(default_factory=list)
    trust_states: List[TrustState] = field(default_factory=list)
    collaboration_modes: List[CollaborationMode] = field(default_factory=list)
    handoff_triggered: bool = False
    handoff_kind: Optional[str] = None
    alert_brief_urgency: Optional[str] = None


def run_persona(
    context: LeadContext,
    turns: List[ConversationTurn],
    engine: CustomerBehaviorEngine,
    trust_machine: TrustStateMachine,
    mode_machine: ModeStateMachine,
    handoff_manager: HandoffManager,
    rep_engine: Optional[RepAssistEngine] = None,
) -> PersonaResult:
    """Execute a scripted conversation sequence and collect outputs.

    Each turn updates the trust state from signals, checks for handoff,
    generates the customer-facing response, and records the system state.
    """
    result = PersonaResult()

    for turn in turns:
        # Advance trust state from this turn's signals
        new_state = trust_machine.transition(turn.signals)
        context.customer_state = new_state.value
        result.trust_states.append(new_state)

        # Check for handoff trigger
        triggered, kind = handoff_manager.should_trigger(turn.signals, context)
        if triggered and not result.handoff_triggered:
            result.handoff_triggered = True
            result.handoff_kind = kind

            # If rep engine available, generate alert brief for rep
            if rep_engine and kind:
                brief = rep_engine.create_alert_brief(context, trigger=kind)
                result.alert_brief_urgency = brief.urgency_sla

            # Update collaboration mode
            new_mode = mode_machine.transition(
                rep_online=context.rep_online,
                live_session=False,
                handoff_triggered=True,
                awaiting_approval=False,
            )
            context.collaboration_mode = new_mode.value
        else:
            new_mode = mode_machine.transition(
                rep_online=context.rep_online,
                live_session=False,
                handoff_triggered=False,
                awaiting_approval=False,
            )
            context.collaboration_mode = new_mode.value

        result.collaboration_modes.append(CollaborationMode(context.collaboration_mode))

        # Generate customer-facing response
        response = engine.generate_response(context, signals=turn.signals)
        result.responses.append(response)

    return result


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def engine() -> CustomerBehaviorEngine:
    return CustomerBehaviorEngine()


@pytest.fixture
def rep_engine() -> RepAssistEngine:
    return RepAssistEngine()


@pytest.fixture
def trust_machine() -> TrustStateMachine:
    return TrustStateMachine()


@pytest.fixture
def mode_machine() -> ModeStateMachine:
    return ModeStateMachine()


@pytest.fixture
def handoff_manager() -> HandoffManager:
    return HandoffManager(HandoffQueue())


# ---------------------------------------------------------------------------
# Forbidden response patterns shared across all personas
# soul.md value 1: no fake urgency or scarcity — ever
# ---------------------------------------------------------------------------

_URGENCY_FORBIDDEN = [
    "limited time", "expires soon", "only a few spots",
    "this week only", "act now", "don't miss", "last chance",
    "running out", "closing soon", "offer ends",
]

_PRESSURE_FORBIDDEN = [
    "you need to decide", "don't wait too long",
    "others are looking at this", "move quickly",
]

ALL_FORBIDDEN_PATTERNS = _URGENCY_FORBIDDEN + _PRESSURE_FORBIDDEN


def assert_no_forbidden_patterns(response: str, turn_description: str) -> None:
    """Assert that a response contains none of the forbidden soul.md patterns."""
    response_lower = response.lower()
    for pattern in ALL_FORBIDDEN_PATTERNS:
        assert pattern not in response_lower, (
            f"Turn '{turn_description}': response contains forbidden pattern "
            f"'{pattern}'. soul.md value 1: no fake urgency or pressure. "
            f"Response: '{response[:120]}...'"
        )


# ---------------------------------------------------------------------------
# P1 — The Skeptic
#
# Profile: has been burned by a previous vendor. Tests honesty, consistency,
# and non-defensiveness under pressure. Asks probing questions. Tests identity.
#
# soul.md values under test: value 2 (reduce uncertainty), value 6 (honesty),
# conflict hierarchy priority 1 (do not deceive).
# ---------------------------------------------------------------------------

class TestPersonaSkeptic:
    """P1 — The Skeptic: burned before, probing, identity-testing."""

    @pytest.fixture
    def skeptic_context(self) -> LeadContext:
        return LeadContext(lead_id="P1-001", sentiment="skeptical")

    def test_p1_objection_response_is_non_defensive(
        self,
        engine: CustomerBehaviorEngine,
        skeptic_context: LeadContext,
    ) -> None:
        """Agent must validate skeptic's concern before any problem-solving.

        soul.md value 2: reduce uncertainty, don't create pressure. A
        skeptic's objection must be acknowledged — not deflected or
        immediately reframed.
        """
        response = engine.generate_response(
            skeptic_context,
            signals={
                "trust_state": TrustState.OBJECTION,
                "topic": "whether this is just another sales pitch",
            },
        )
        response_lower = response.lower()

        # Must acknowledge before solving
        acknowledgement_patterns = [
            "makes sense", "thanks for", "i hear", "valid", "understand"
        ]
        has_acknowledgement = any(p in response_lower for p in acknowledgement_patterns)
        assert has_acknowledgement, (
            "Skeptic objection response must acknowledge concern before addressing it. "
            f"Got: '{response}'. soul.md value 2."
        )

        # Must not pitch or defend immediately
        defensive_patterns = [
            "actually we're different", "you'll find that", "trust me",
            "i promise", "guaranteed"
        ]
        for pattern in defensive_patterns:
            assert pattern not in response_lower, (
                f"Skeptic objection response contains defensive pattern '{pattern}'. "
                "soul.md value 2: reduce uncertainty — don't fight it."
            )

    def test_p1_no_pressure_across_skeptic_journey(
        self,
        engine: CustomerBehaviorEngine,
        trust_machine: TrustStateMachine,
        mode_machine: ModeStateMachine,
        handoff_manager: HandoffManager,
        skeptic_context: LeadContext,
    ) -> None:
        """No response in a skeptic conversation may contain pressure language.

        soul.md value 1: a skeptic who senses pressure will disengage
        entirely. Urgency and pressure patterns are especially destructive
        with this persona.
        """
        turns = [
            ConversationTurn("initial exploration", {"intent": "explore", "trust_state": TrustState.AWARENESS}),
            ConversationTurn("raises concern", {"objection": True, "trust_state": TrustState.OBJECTION, "topic": "ROI proof"}),
            ConversationTurn("still skeptical", {"trust_state": TrustState.OBJECTION, "topic": "implementation risk"}),
            ConversationTurn("cautious evaluation", {"trust_state": TrustState.EVALUATION, "topic": "alternatives"}),
        ]

        result = run_persona(
            skeptic_context, turns, engine, trust_machine,
            mode_machine, handoff_manager,
        )

        for i, (response, turn) in enumerate(zip(result.responses, turns)):
            assert_no_forbidden_patterns(response, turn.description)

    def test_p1_hesitation_response_normalizes_pace(
        self,
        engine: CustomerBehaviorEngine,
        skeptic_context: LeadContext,
    ) -> None:
        """Hesitation response must normalize slowing down, not treat it as a problem.

        soul.md value 5: patience with people. A skeptic who hesitates
        must feel that slowing down is acceptable — not that they're
        holding up a process.
        """
        response = engine.generate_response(
            skeptic_context,
            signals={"trust_state": TrustState.HESITATION, "topic": "timing"},
        )
        response_lower = response.lower()

        normalizing_patterns = ["your own pace", "no rush", "take your time", "completely fine"]
        has_normalizing = any(p in response_lower for p in normalizing_patterns)
        assert has_normalizing, (
            "Hesitation response must normalize the prospect's pace. "
            f"Got: '{response}'. soul.md value 5."
        )


# ---------------------------------------------------------------------------
# P2 — The Eager Buyer
#
# Profile: enthusiastic, agrees with everything, moves fast. Creates the
# risk of the agent skipping fit validation due to positive momentum.
#
# soul.md values under test: value 3 (dignity and agency), conflict hierarchy
# priority 2 (do not harm the prospect's interest).
# ---------------------------------------------------------------------------

class TestPersonaEagerBuyer:
    """P2 — The Eager Buyer: enthusiastic, high momentum, fit validation risk."""

    @pytest.fixture
    def eager_context(self) -> LeadContext:
        ctx = LeadContext(lead_id="P2-001", sentiment="positive")
        ctx.assigned_rep = "Casey"
        return ctx

    def test_p2_fit_check_fires_despite_enthusiasm(
        self,
        engine: CustomerBehaviorEngine,
        eager_context: LeadContext,
    ) -> None:
        """fit_confirmed=False must block handoff even with high buying signal.

        soul.md conflict hierarchy priority 2: enthusiasm does not confirm
        fit. A prospect who has talked themselves into readiness without fit
        validation must still receive the fit-check response.
        """
        response = engine.generate_response(
            eager_context,
            signals={
                "trust_state": TrustState.DECISION_READY,
                "strong_buying_signal": True,
                "urgency": "high",
                "fit_confirmed": False,  # not yet confirmed upstream
            },
        )
        assert response == _FIT_CHECK_RESPONSE, (
            "Eager buyer with high momentum but fit_confirmed=False must receive "
            "fit-check response, not handoff template. soul.md priority 2."
        )

    def test_p2_handoff_renders_only_after_fit_confirmed(
        self,
        engine: CustomerBehaviorEngine,
        eager_context: LeadContext,
    ) -> None:
        """Handoff template renders only once fit_confirmed=True is set.

        This test documents the correct happy path: qualification layer
        sets fit_confirmed=True, then the handoff is appropriate.
        """
        response = engine.generate_response(
            eager_context,
            signals={
                "trust_state": TrustState.DECISION_READY,
                "strong_buying_signal": True,
                "fit_confirmed": True,
            },
        )
        assert "Casey" in response, (
            "After fit is confirmed, handoff must include the assigned rep's name."
        )
        assert response != _FIT_CHECK_RESPONSE, (
            "Fit-check response must not appear when fit_confirmed=True."
        )

    def test_p2_no_mirrored_urgency_in_responses(
        self,
        engine: CustomerBehaviorEngine,
        eager_context: LeadContext,
    ) -> None:
        """Agent must not mirror the eager buyer's urgency back at them.

        soul.md value 1: no pressure tactics. Even if the prospect signals
        high urgency, the agent must not amplify it by using urgency language
        in its own response.
        """
        states_to_check = [
            TrustState.CURIOSITY,
            TrustState.EVALUATION,
            TrustState.TRUST_BUILDING,
        ]
        for state in states_to_check:
            response = engine.generate_response(
                eager_context,
                signals={"trust_state": state, "urgency": "high", "topic": "getting started"},
            )
            assert_no_forbidden_patterns(response, f"eager buyer at {state.value}")


# ---------------------------------------------------------------------------
# P3 — The Ghoster
#
# Profile: strong early interest, then goes silent. Tests patience and
# the absence of pressure-based follow-up language.
#
# soul.md values under test: value 5 (patience over pressure),
# value 1 (no fake urgency).
# ---------------------------------------------------------------------------

class TestPersonaGhoster:
    """P3 — The Ghoster: high early interest, then silence."""

    @pytest.fixture
    def ghoster_context(self) -> LeadContext:
        ctx = LeadContext(lead_id="P3-001", sentiment="neutral")
        ctx.customer_state = TrustState.TRUST_BUILDING.value
        return ctx

    def test_p3_follow_up_after_silence_is_patient(
        self,
        engine: CustomerBehaviorEngine,
        ghoster_context: LeadContext,
    ) -> None:
        """Follow-up response after silence must be patient, not urgent.

        soul.md value 5: patience over pressure. Silence is information,
        not a problem to solve with escalating urgency.
        """
        # Simulate a follow-up turn with no engagement signals
        response = engine.generate_response(
            ghoster_context,
            signals={
                "trust_state": TrustState.HESITATION,
                "topic": "",
                "urgency": "",
            },
        )
        response_lower = response.lower()

        # Must not manufacture urgency to break the silence
        assert_no_forbidden_patterns(response, "ghoster follow-up")

        # Must normalize the silence or offer an easy re-entry
        patient_patterns = [
            "your own pace", "no rush", "take your time",
            "whenever", "here if", "happy to"
        ]
        has_patient_language = any(p in response_lower for p in patient_patterns)
        assert has_patient_language, (
            "Follow-up after silence must contain patient, low-pressure language. "
            f"Got: '{response}'. soul.md value 5."
        )

    def test_p3_no_scarcity_tactics_after_silence(
        self,
        engine: CustomerBehaviorEngine,
        ghoster_context: LeadContext,
    ) -> None:
        """Scarcity tactics must not be used to re-engage a silent prospect.

        The temptation to use "a few spots left" or similar tactics is
        highest when a prospect goes quiet. soul.md value 1 prohibits this
        unconditionally — silence does not justify manufactured urgency.
        """
        # Multiple follow-up turns to stress-test across hesitation and evaluation
        for state in [TrustState.HESITATION, TrustState.EVALUATION, TrustState.AWARENESS]:
            response = engine.generate_response(
                ghoster_context,
                signals={"trust_state": state, "topic": ""},
            )
            assert_no_forbidden_patterns(response, f"ghoster re-engagement at {state.value}")


# ---------------------------------------------------------------------------
# P4 — The Frustrated One
#
# Profile: came with a real problem, becomes impatient mid-conversation.
# Tests frustration escalation, rep alert, and mode transition to ALERT.
#
# soul.md values under test: conflict hierarchy priority 2 (do not harm
# the prospect's interest), value 4 (respect human trust moments).
# ---------------------------------------------------------------------------

class TestPersonaFrustratedOne:
    """P4 — The Frustrated One: sentiment degrades, must escalate to rep."""

    @pytest.fixture
    def frustrated_context(self) -> LeadContext:
        ctx = LeadContext(
            lead_id="P4-001",
            sentiment="frustrated",
            conversation_summary="Prospect frustrated with slow response. Expressed impatience twice.",
        )
        ctx.rep_online = True
        return ctx

    def test_p4_frustration_triggers_alert_mode(
        self,
        engine: CustomerBehaviorEngine,
        trust_machine: TrustStateMachine,
        mode_machine: ModeStateMachine,
        handoff_manager: HandoffManager,
        rep_engine: RepAssistEngine,
        frustrated_context: LeadContext,
    ) -> None:
        """Frustration signal must transition collaboration mode to ALERT.

        soul.md value 4: respect human trust moments. Frustration is
        a trust-critical moment that belongs to a human rep, not the agent.
        """
        turns = [
            ConversationTurn(
                "prospect expresses frustration",
                {
                    "trust_state": TrustState.OBJECTION,
                    "sentiment": "frustrated",
                    "topic": "slow response times",
                },
            ),
        ]

        result = run_persona(
            frustrated_context, turns, engine, trust_machine,
            mode_machine, handoff_manager, rep_engine,
        )

        assert result.handoff_triggered, (
            "Frustration signal must trigger a handoff. soul.md value 4."
        )
        assert result.handoff_kind == "frustration", (
            f"Handoff kind must be 'frustration', got '{result.handoff_kind}'."
        )
        assert result.alert_brief_urgency == _FRUSTRATION_URGENCY_OVERRIDE, (
            f"Alert brief urgency must be '{_FRUSTRATION_URGENCY_OVERRIDE}' "
            f"for frustrated prospect. Got '{result.alert_brief_urgency}'."
        )
        assert CollaborationMode.ALERT in result.collaboration_modes, (
            "Collaboration mode must transition to ALERT on frustration. "
            "soul.md value 4: this moment belongs to a human rep."
        )

    def test_p4_agent_response_does_not_attempt_autonomous_deescalation(
        self,
        engine: CustomerBehaviorEngine,
        frustrated_context: LeadContext,
    ) -> None:
        """Agent must not generate de-escalation copy after frustration signal.

        soul.md conflict hierarchy priority 2: the agent must never hold on
        to a conversation it should escalate. Attempting to de-escalate a
        frustrated prospect autonomously risks making the situation worse
        while delaying the rep's involvement.

        NOTE: Once ALERT mode is active, the orchestrator should suppress
        further autonomous customer responses. This test verifies that the
        behavior engine itself does not generate pressure or persuasion copy
        when the trust state is OBJECTION with frustrated sentiment.
        """
        response = engine.generate_response(
            frustrated_context,
            signals={
                "trust_state": TrustState.OBJECTION,
                "topic": "slow response",
                "sentiment": "frustrated",
            },
        )
        response_lower = response.lower()

        # Must not attempt to "fix" the frustration with sales language
        deescalation_forbidden = [
            "i understand your frustration, but",
            "let me make it up to you",
            "here's what we can offer",
            "as a special exception",
        ]
        for pattern in deescalation_forbidden:
            assert pattern not in response_lower, (
                f"Agent used autonomous de-escalation pattern '{pattern}' "
                "for frustrated prospect. soul.md conflict hierarchy priority 2: "
                "this moment belongs to a human rep."
            )


# ---------------------------------------------------------------------------
# P5 — The Poor Fit
#
# Profile: describes a need the product genuinely cannot meet, but is warm
# and willing to buy. Tests honest disqualification without rejection.
#
# soul.md values under test: value 3 (dignity and agency), conflict hierarchy
# priority 2 (do not harm the prospect's interest), value 1 (trust over
# conversion).
# ---------------------------------------------------------------------------

class TestPersonaPoorFit:
    """P5 — The Poor Fit: genuine mismatch, warm prospect, must disqualify honestly."""

    @pytest.fixture
    def poor_fit_context(self) -> LeadContext:
        """Prospect whose needs don't match — fit_confirmed must stay False."""
        ctx = LeadContext(lead_id="P5-001", sentiment="positive")
        ctx.assigned_rep = "Morgan"
        return ctx

    def test_p5_fit_check_fires_at_decision_ready_despite_warmth(
        self,
        engine: CustomerBehaviorEngine,
        poor_fit_context: LeadContext,
    ) -> None:
        """Warm prospect at DECISION_READY must still receive fit-check if fit unconfirmed.

        soul.md conflict hierarchy priority 2: the prospect's genuine interest
        does not override the need to confirm fit. A warm prospect handed off
        to a rep when the product doesn't solve their problem will churn — and
        the trust damage is worse than an honest no now.
        """
        response = engine.generate_response(
            poor_fit_context,
            signals={
                "trust_state": TrustState.DECISION_READY,
                "fit_confirmed": False,  # qualification layer has not confirmed fit
                "urgency": "high",
                "topic": "getting started this quarter",
            },
        )
        assert response == _FIT_CHECK_RESPONSE, (
            "Poor-fit prospect at DECISION_READY must receive fit-check even "
            "when sentiment is positive and urgency is high. "
            "soul.md conflict hierarchy priority 2."
        )

    def test_p5_fit_check_tone_does_not_make_prospect_feel_rejected(
        self,
        engine: CustomerBehaviorEngine,
        poor_fit_context: LeadContext,
    ) -> None:
        """Fit-check response must preserve prospect's dignity.

        soul.md value 3: the prospect is never a target — they are a person
        making a decision. The fit-check must feel like honest care, not
        a polite rejection or a bureaucratic gate.
        """
        response = engine.generate_response(
            poor_fit_context,
            signals={
                "trust_state": TrustState.DECISION_READY,
                "fit_confirmed": False,
            },
        )
        response_lower = response.lower()

        rejection_patterns = [
            "you don't qualify",
            "this isn't for you",
            "unfortunately",
            "we can't help",
            "not eligible",
        ]
        for pattern in rejection_patterns:
            assert pattern not in response_lower, (
                f"Fit-check response contains rejection language '{pattern}'. "
                "soul.md value 3: preserve dignity — fit check must be an "
                "honest conversation, not a rejection."
            )

    def test_p5_evaluation_response_surfaces_honest_comparison(
        self,
        engine: CustomerBehaviorEngine,
        poor_fit_context: LeadContext,
    ) -> None:
        """Evaluation response must invite honest criteria — not steer toward product.

        soul.md value 2: clarity is the service. During evaluation, the agent
        must help the prospect surface their own decision criteria rather than
        steering them toward the product.
        """
        response = engine.generate_response(
            poor_fit_context,
            signals={
                "trust_state": TrustState.EVALUATION,
                "topic": "alternatives",
            },
        )
        response_lower = response.lower()

        steering_patterns = [
            "you'll find we're the best",
            "compared to others, we",
            "our competitors can't",
            "the obvious choice",
        ]
        for pattern in steering_patterns:
            assert pattern not in response_lower, (
                f"Evaluation response steers prospect with pattern '{pattern}'. "
                "soul.md value 2: the agent is an advisor, not a closer."
            )


# ---------------------------------------------------------------------------
# P6 — The Human Requester
#
# Profile: explicitly asks to speak to a human at multiple trust states.
# Tests that human_request trigger fires immediately regardless of state.
#
# soul.md values under test: value 4 (respect human trust moments),
# conflict hierarchy priority 2.
# ---------------------------------------------------------------------------

class TestPersonaHumanRequester:
    """P6 — The Human Requester: asks for a human at various trust states."""

    _HUMAN_REQUEST_STATES = [
        TrustState.AWARENESS,
        TrustState.CURIOSITY,
        TrustState.HESITATION,
        TrustState.TRUST_BUILDING,
        TrustState.OBJECTION,
    ]

    @pytest.fixture
    def requester_context(self) -> LeadContext:
        ctx = LeadContext(lead_id="P6-001", sentiment="neutral")
        ctx.rep_online = True
        return ctx

    @pytest.mark.parametrize("trust_state", _HUMAN_REQUEST_STATES)
    def test_p6_human_request_triggers_handoff_at_any_state(
        self,
        trust_state: TrustState,
        trust_machine: TrustStateMachine,
        mode_machine: ModeStateMachine,
        handoff_manager: HandoffManager,
        engine: CustomerBehaviorEngine,
        rep_engine: RepAssistEngine,
        requester_context: LeadContext,
    ) -> None:
        """human_request must trigger handoff regardless of current trust state.

        soul.md value 4: "any moment where the prospect explicitly asks for
        a person" belongs to a human. No trust state, no pipeline stage,
        no conversation momentum overrides this.
        """
        trust_machine.current_state = trust_state
        requester_context.customer_state = trust_state.value

        turns = [
            ConversationTurn(
                f"human request at {trust_state.value}",
                {
                    "trust_state": trust_state,
                    "human_request": True,
                    "topic": "I want to speak to a real person",
                },
            ),
        ]

        result = run_persona(
            requester_context, turns, engine, trust_machine,
            mode_machine, handoff_manager, rep_engine,
        )

        assert result.handoff_triggered, (
            f"human_request at trust state {trust_state.value} must trigger handoff. "
            "soul.md value 4: human requests override all other signals."
        )
        assert result.handoff_kind == "human_request", (
            f"Handoff kind must be 'human_request' when prospect asks for a human. "
            f"Got '{result.handoff_kind}' at state {trust_state.value}."
        )

    def test_p6_human_request_wins_over_all_other_signals(
        self,
        trust_machine: TrustStateMachine,
        mode_machine: ModeStateMachine,
        handoff_manager: HandoffManager,
        engine: CustomerBehaviorEngine,
        rep_engine: RepAssistEngine,
        requester_context: LeadContext,
    ) -> None:
        """human_request must win over pricing, buying intent, and competitor signals.

        HandoffManager priority ordering: human_request is evaluated first.
        Even if all other signals are also true, the handoff kind must be
        'human_request'. soul.md value 4.
        """
        turns = [
            ConversationTurn(
                "human request with competing signals",
                {
                    "trust_state": TrustState.TRUST_BUILDING,
                    "human_request": True,
                    "pricing_discussion": True,
                    "strong_buying_signal": True,
                    "competitor_mention": True,
                },
            ),
        ]

        result = run_persona(
            requester_context, turns, engine, trust_machine,
            mode_machine, handoff_manager, rep_engine,
        )

        assert result.handoff_kind == "human_request", (
            f"human_request must win over all competing signals. "
            f"Got handoff_kind='{result.handoff_kind}'. soul.md value 4."
        )

    def test_p6_no_pressure_patterns_before_human_handoff(
        self,
        engine: CustomerBehaviorEngine,
        requester_context: LeadContext,
    ) -> None:
        """Responses leading up to a human request must contain no pressure language.

        Even if the system hasn't yet detected the human_request signal,
        the responses the prospect saw before asking must be pressure-free.
        soul.md value 1.
        """
        pre_request_turns = [
            (TrustState.AWARENESS, ""),
            (TrustState.CURIOSITY, "pricing options"),
            (TrustState.HESITATION, "timeline"),
        ]
        for state, topic in pre_request_turns:
            response = engine.generate_response(
                requester_context,
                signals={"trust_state": state, "topic": topic},
            )
            assert_no_forbidden_patterns(response, f"pre-request turn at {state.value}")
