"""Unit tests: handoff decision order and SLA minutes.

Gap tests added (soul.md alignment):
- fit_confirmed=False must block DECISION_READY from rendering the handoff
  template (soul.md value 3 and conflict hierarchy priority 2).
- fit_confirmed=True must allow handoff template to render.
- fit_confirmed defaults to False — safe-by-default when caller omits it.
"""

import pytest

from src.collaboration.handoff_manager import HandoffManager
from src.core.handoff_queue import HandoffQueue
from src.core.lead_context import LeadContext
from src.customer_layer.behavior_engine import CustomerBehaviorEngine, _FIT_CHECK_RESPONSE
from src.customer_layer.trust_state_machine import TrustState


# ---------------------------------------------------------------------------
# Existing tests — unchanged
# ---------------------------------------------------------------------------

@pytest.fixture
def manager() -> HandoffManager:
    return HandoffManager(HandoffQueue())


@pytest.fixture
def base_context() -> LeadContext:
    return LeadContext(lead_id="L-1", sentiment="neutral")


def test_human_request_wins_over_later_rules(manager: HandoffManager, base_context: LeadContext) -> None:
    triggered, kind = manager.should_trigger(
        {
            "human_request": True,
            "pricing_discussion": True,
            "strong_buying_signal": True,
        },
        base_context,
    )
    assert triggered is True
    assert kind == "human_request"


def test_pricing_discussion_when_no_human(manager: HandoffManager, base_context: LeadContext) -> None:
    triggered, kind = manager.should_trigger(
        {"human_request": False, "pricing_discussion": True},
        base_context,
    )
    assert triggered is True
    assert kind == "pricing_discussion"


def test_frustration_from_signal_overrides_context_sentiment(
    manager: HandoffManager, base_context: LeadContext
) -> None:
    base_context.sentiment = "neutral"
    triggered, kind = manager.should_trigger({"sentiment": "frustration"}, base_context)
    assert triggered is True
    assert kind == "frustration"


def test_frustration_from_context_when_absent_in_signals(
    manager: HandoffManager, base_context: LeadContext
) -> None:
    base_context.sentiment = "frustrated"
    triggered, kind = manager.should_trigger({}, base_context)
    assert triggered is True
    assert kind == "frustration"


def test_no_trigger_when_signals_clear(manager: HandoffManager, base_context: LeadContext) -> None:
    triggered, kind = manager.should_trigger(
        {
            "human_request": False,
            "pricing_discussion": False,
            "strong_buying_signal": False,
            "competitor_mention": False,
            "stakeholder_approval_needed": False,
            "sentiment": "neutral",
        },
        base_context,
    )
    assert triggered is False
    assert kind == "none"


@pytest.mark.parametrize(
    "trigger_type,expected_minutes",
    [
        ("human_request", 15),
        ("pricing_discussion", 120),
        ("strong_buying_signal", 60),
        ("frustration", 30),
        ("competitor_mention", 60),
        ("stakeholder_approval_needed", 120),
        ("none", 0),
        ("unknown_future_trigger", 60),
    ],
)
def test_sla_minutes_by_trigger_type(
    manager: HandoffManager, trigger_type: str, expected_minutes: int
) -> None:
    assert manager.get_sla(trigger_type) == expected_minutes


# ---------------------------------------------------------------------------
# Gap — fit_confirmed=False blocks DECISION_READY handoff bridge
# (soul.md value 3 "preserve dignity and agency" + conflict hierarchy priority 2)
#
# A prospect reaching DECISION_READY through conversation momentum does not
# guarantee the product is right for them. CustomerBehaviorEngine must not
# render the handoff template unless fit_confirmed=True is explicitly set
# upstream by the orchestrator or qualification layer.
#
# These tests verify the blocking behavior in CustomerBehaviorEngine directly,
# since that is where the fit_confirmed guard lives. The HandoffManager tests
# above verify trigger priority; these tests verify what happens at the
# customer-visible response level when DECISION_READY is reached.
# ---------------------------------------------------------------------------

@pytest.fixture
def engine() -> CustomerBehaviorEngine:
    return CustomerBehaviorEngine()


@pytest.fixture
def decision_ready_context() -> LeadContext:
    """Lead context at DECISION_READY with a named rep assigned."""
    ctx = LeadContext(
        lead_id="L-dr-1",
        sentiment="positive",
        assigned_rep="Sarah",
    )
    ctx.customer_state = TrustState.DECISION_READY
    return ctx


@pytest.fixture
def decision_ready_context_no_rep() -> LeadContext:
    """Lead context at DECISION_READY with no rep assigned."""
    ctx = LeadContext(lead_id="L-dr-2", sentiment="positive")
    ctx.customer_state = TrustState.DECISION_READY
    return ctx


def test_decision_ready_without_fit_confirmed_returns_fit_check(
    engine: CustomerBehaviorEngine,
    decision_ready_context: LeadContext,
) -> None:
    """fit_confirmed=False must return the fit-check response, not the handoff template.

    soul.md value 3 "preserve dignity and agency" + conflict hierarchy
    priority 2: a prospect must not be handed off to a rep before product
    fit is confirmed. The agent must surface a fit-check question first.
    """
    response = engine.generate_response(
        decision_ready_context,
        signals={"trust_state": TrustState.DECISION_READY, "fit_confirmed": False},
    )
    assert response == _FIT_CHECK_RESPONSE, (
        "DECISION_READY with fit_confirmed=False must return _FIT_CHECK_RESPONSE. "
        f"Got: '{response[:80]}...'"
    )


def test_decision_ready_with_fit_confirmed_true_renders_handoff_template(
    engine: CustomerBehaviorEngine,
    decision_ready_context: LeadContext,
) -> None:
    """fit_confirmed=True must render the handoff bridge template.

    Once fit is confirmed upstream, the agent is safe to bridge to the rep.
    The response must include the rep's name from assigned_rep.
    """
    response = engine.generate_response(
        decision_ready_context,
        signals={"trust_state": TrustState.DECISION_READY, "fit_confirmed": True},
    )
    assert "Sarah" in response, (
        "Handoff bridge must include the assigned rep's name when fit_confirmed=True."
    )
    assert _FIT_CHECK_RESPONSE not in response, (
        "Fit-check response must not appear when fit_confirmed=True."
    )


def test_decision_ready_fit_confirmed_absent_defaults_to_false(
    engine: CustomerBehaviorEngine,
    decision_ready_context: LeadContext,
) -> None:
    """Omitting fit_confirmed from signals must behave identically to fit_confirmed=False.

    Safe-by-default: any caller that forgets to pass fit_confirmed must get
    the fit-check response, not the handoff template. The risky path requires
    explicit intent.
    """
    response = engine.generate_response(
        decision_ready_context,
        signals={"trust_state": TrustState.DECISION_READY},
        # fit_confirmed intentionally omitted
    )
    assert response == _FIT_CHECK_RESPONSE, (
        "Omitting fit_confirmed must default to False and return _FIT_CHECK_RESPONSE. "
        "The safe path must not require explicit opt-in."
    )


def test_decision_ready_fit_confirmed_false_with_no_rep_assigned(
    engine: CustomerBehaviorEngine,
    decision_ready_context_no_rep: LeadContext,
) -> None:
    """fit-check response must fire even when no rep is assigned.

    The fit check is not conditional on rep availability — it is a
    prospect-protection constraint that fires regardless of system state.
    """
    response = engine.generate_response(
        decision_ready_context_no_rep,
        signals={"trust_state": TrustState.DECISION_READY, "fit_confirmed": False},
    )
    assert response == _FIT_CHECK_RESPONSE, (
        "fit-check response must fire regardless of whether a rep is assigned."
    )


def test_decision_ready_fit_confirmed_true_with_no_rep_uses_generic_handoff(
    engine: CustomerBehaviorEngine,
    decision_ready_context_no_rep: LeadContext,
) -> None:
    """fit_confirmed=True with no assigned rep must use the generic handoff copy.

    When fit is confirmed but no specific rep is assigned, the agent must
    still bridge — using the generic handoff template rather than a named rep.
    """
    response = engine.generate_response(
        decision_ready_context_no_rep,
        signals={"trust_state": TrustState.DECISION_READY, "fit_confirmed": True},
    )
    assert _FIT_CHECK_RESPONSE not in response, (
        "Fit-check response must not appear when fit_confirmed=True."
    )
    assert "team" in response.lower() or "connect" in response.lower(), (
        "Generic handoff copy must reference connecting the prospect to the team."
    )
