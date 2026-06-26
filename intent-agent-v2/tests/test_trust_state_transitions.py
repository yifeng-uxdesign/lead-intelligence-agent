"""Unit tests: customer psychological trust state machine.

Gap tests added (soul.md alignment):
- OBJECTION -> EVALUATION regression path (soul.md value 5: read where
  prospect IS, not where they WERE)
- HESITATION -> CURIOSITY regression path (same value)
- DECISION_READY auto-commit blocked by objection signal (soul.md conflict
  hierarchy priority 2: do not harm the prospect's interest)
"""

import pytest

from src.customer_layer.trust_state_machine import TrustState, TrustStateMachine


# ---------------------------------------------------------------------------
# Existing tests — unchanged
# ---------------------------------------------------------------------------

def test_awareness_to_curiosity_on_explore_intent() -> None:
    m = TrustStateMachine()
    assert m.get_state() == TrustState.AWARENESS
    out = m.transition({"intent": "explore"})
    assert out == TrustState.CURIOSITY
    assert m.current_state == TrustState.CURIOSITY


def test_curiosity_to_objection_when_objection_flag() -> None:
    m = TrustStateMachine()
    m.current_state = TrustState.CURIOSITY
    out = m.transition({"objection": True})
    assert out == TrustState.OBJECTION


def test_curiosity_objection_wins_over_low_urgency_when_both() -> None:
    m = TrustStateMachine()
    m.current_state = TrustState.CURIOSITY
    out = m.transition({"objection": True, "urgency": "low"})
    assert out == TrustState.OBJECTION


def test_curiosity_to_hesitation_on_low_urgency() -> None:
    m = TrustStateMachine()
    m.current_state = TrustState.CURIOSITY
    out = m.transition({"urgency": "low"})
    assert out == TrustState.HESITATION


def test_evaluation_to_trust_building_on_high_trust_score() -> None:
    m = TrustStateMachine()
    m.current_state = TrustState.EVALUATION
    out = m.transition({"trust_score": 0.76})
    assert out == TrustState.TRUST_BUILDING


def test_trust_building_to_decision_ready_on_buying_signal() -> None:
    m = TrustStateMachine()
    m.current_state = TrustState.TRUST_BUILDING
    out = m.transition({"strong_buying_signal": True})
    assert out == TrustState.DECISION_READY


def test_decision_ready_advances_to_commitment() -> None:
    m = TrustStateMachine()
    m.current_state = TrustState.DECISION_READY
    out = m.transition({})
    assert out == TrustState.COMMITMENT


def test_no_op_transition_when_rules_do_not_apply() -> None:
    m = TrustStateMachine()
    m.current_state = TrustState.CURIOSITY
    out = m.transition({"intent": "buy", "urgency": "high"})
    assert out == TrustState.CURIOSITY


# ---------------------------------------------------------------------------
# Gap 1 — Regression paths (soul.md value 5: patience with people)
#
# A prospect whose objection is resolved must not remain stuck in OBJECTION
# forever. The state machine must support backward transitions so the agent
# reads where the prospect IS, not where they WERE.
#
# These tests will FAIL until regression paths are added to transition().
# The expected fix: add a `resolve` signal check in TrustStateMachine that
# allows OBJECTION -> EVALUATION and HESITATION -> CURIOSITY.
# ---------------------------------------------------------------------------

def test_objection_resolves_back_to_evaluation() -> None:
    """OBJECTION -> EVALUATION when prospect signals resolution.

    soul.md value 5 — patience with people: the agent must track current
    emotional state, not historical state. An objection that has been worked
    through should not keep triggering objection-handling language.
    """
    m = TrustStateMachine()
    m.current_state = TrustState.OBJECTION
    out = m.transition({"resolve": True})
    assert out == TrustState.EVALUATION, (
        "Resolved objection should return to EVALUATION, not stay in OBJECTION. "
        "Add OBJECTION -> EVALUATION regression path to transition()."
    )


def test_hesitation_resolves_back_to_curiosity() -> None:
    """HESITATION -> CURIOSITY when prospect re-engages with clearer intent.

    soul.md value 5 — patience with people: hesitation that lifts should
    allow the agent to return to discovery mode rather than treating the
    prospect as permanently uncertain.
    """
    m = TrustStateMachine()
    m.current_state = TrustState.HESITATION
    out = m.transition({"resolve": True})
    assert out == TrustState.CURIOSITY, (
        "Resolved hesitation should return to CURIOSITY, not stay in HESITATION. "
        "Add HESITATION -> CURIOSITY regression path to transition()."
    )


def test_objection_regression_does_not_fire_without_resolve_signal() -> None:
    """Regression path must not trigger on arbitrary signals.

    Ensures that adding the resolve path doesn't accidentally regress state
    on unrelated signal combinations.
    """
    m = TrustStateMachine()
    m.current_state = TrustState.OBJECTION
    out = m.transition({"intent": "explore", "urgency": "high"})
    assert out == TrustState.OBJECTION, (
        "OBJECTION state must not regress without an explicit resolve signal."
    )


def test_hesitation_regression_does_not_fire_without_resolve_signal() -> None:
    """Regression path must not trigger on arbitrary signals."""
    m = TrustStateMachine()
    m.current_state = TrustState.HESITATION
    out = m.transition({"intent": "explore", "trust_score": 0.5})
    assert out == TrustState.HESITATION, (
        "HESITATION state must not regress without an explicit resolve signal."
    )


# ---------------------------------------------------------------------------
# Gap 2 — DECISION_READY auto-commit blocked by negative signals
# (soul.md conflict hierarchy priority 2: do not harm the prospect's interest)
#
# Currently transition() commits unconditionally from DECISION_READY on any
# call, regardless of incoming signals. If a prospect sends objection=True
# or urgency="low" while in DECISION_READY, the machine should not advance
# to COMMITMENT.
#
# These tests will FAIL until a signal check is added to the DECISION_READY
# branch. The expected fix: mirror the strong_buying_signal check used in
# TRUST_BUILDING -> DECISION_READY — require a positive signal to commit.
# ---------------------------------------------------------------------------

def test_decision_ready_does_not_commit_when_objection_raised() -> None:
    """DECISION_READY must not auto-commit if prospect raises a new objection.

    soul.md conflict hierarchy priority 2: do not harm the prospect's
    interest. A prospect who raises a concern at the last moment must not
    be pushed to COMMITMENT regardless of prior momentum.
    """
    m = TrustStateMachine()
    m.current_state = TrustState.DECISION_READY
    out = m.transition({"objection": True})
    assert out != TrustState.COMMITMENT, (
        "DECISION_READY must not advance to COMMITMENT when objection=True. "
        "Add a signal check to the DECISION_READY branch in transition()."
    )


def test_decision_ready_does_not_commit_on_low_urgency() -> None:
    """DECISION_READY must not auto-commit if prospect signals low urgency.

    A prospect who slows down at the decision stage is signalling uncertainty.
    Committing them automatically violates soul.md priority 2.
    """
    m = TrustStateMachine()
    m.current_state = TrustState.DECISION_READY
    out = m.transition({"urgency": "low"})
    assert out != TrustState.COMMITMENT, (
        "DECISION_READY must not advance to COMMITMENT when urgency=low. "
        "Add urgency check to the DECISION_READY branch in transition()."
    )


def test_decision_ready_commits_on_explicit_strong_buying_signal() -> None:
    """DECISION_READY advances to COMMITMENT only with a positive buying signal.

    Mirrors the check used in TRUST_BUILDING -> DECISION_READY for
    consistency. Commitment requires explicit positive signal, not just
    absence of negative ones.
    """
    m = TrustStateMachine()
    m.current_state = TrustState.DECISION_READY
    out = m.transition({"strong_buying_signal": True})
    assert out == TrustState.COMMITMENT, (
        "DECISION_READY should advance to COMMITMENT when strong_buying_signal=True."
    )
