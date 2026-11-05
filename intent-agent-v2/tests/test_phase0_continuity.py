"""Phase 0 milestone: conversation continuity and trust-philosophy regressions.

Groups (from the Phase 0 completion checklist):
  A. Fallback loops: no verbatim repeats, loops are escapable, state survives.
  B. Trust progression: skepticism is validated, never escalated.
  C. Interpretation failure: trust state and pending interventions survive it.
  D. Soul value 6: honesty about being an AI, including inside holding copy.
"""

import pytest

from src.collaboration.delivery_policy import DeliveryStatus
from src.collaboration.mode_state_machine import CollaborationMode
from src.customer_layer.behavior_engine import CustomerBehaviorEngine
from src.customer_layer.fallback_variants import LOOP_BREAKERS, loop_breaker
from src.customer_layer.holding_responses import APPROVED_HOLDING_RESPONSES
from src.customer_layer.trust_state_machine import TrustState
from src.domain.session_state import KEY_LAST_BASE_RESPONSE, KEY_REPEAT_STREAK
from src.orchestrator import build_default_dependencies, interpret_message, run_turn
from src.signals.extractor import LeadSignalExtractor, detect_human_request, detect_identity_question

VAGUE = ["ok", "hmm", "maybe", "not sure", "what else", "sure", "go on"]


def make():
    store, ex, eng, rep, mgr, mm, q = build_default_dependencies()
    return dict(store=store, signal_extractor=ex, customer_engine=eng,
                rep_engine=rep, handoff_manager=mgr, mode_machine=mm), q


def turn(deps, msg, lead="c1", online=False, **kw):
    d, _ = deps
    return run_turn(lead_id=lead, raw_message=msg, rep_online=online, **{**d, **kw})


@pytest.fixture
def deps():
    return make()


# ===========================================================================
# A. Fallback loops
# ===========================================================================

def test_vague_replies_never_get_identical_consecutive_responses(deps) -> None:
    msgs = [turn(deps, m).customer_message for m in VAGUE]
    assert all(msgs)
    for prev, cur in zip(msgs, msgs[1:]):
        assert prev != cur, f"verbatim repeat: {cur[:60]!r}"


def test_first_response_is_the_normal_script_and_loop_starts_on_first_repeat(deps) -> None:
    r1 = turn(deps, "ok")
    r2 = turn(deps, "hmm")
    assert r1.customer_message not in LOOP_BREAKERS
    assert r2.customer_message == LOOP_BREAKERS[0]
    assert r2.context.metadata[KEY_REPEAT_STREAK] == 1


def test_no_aba_loop_between_script_and_loop_breaker(deps) -> None:
    """The guard compares scripted text, so breaker substitution can't alternate with the script."""
    msgs = [turn(deps, m).customer_message for m in VAGUE]
    script = msgs[0]
    assert script not in msgs[1:], "scripted question must not reappear while the loop continues"


def test_loop_breaker_offers_a_human_and_accepting_it_triggers_handoff(deps) -> None:
    """The escape hatch must work: the invitation wording is something the extractor honors."""
    turn(deps, "ok"); r = turn(deps, "hmm")
    assert "talk to a person" in r.customer_message
    accept = turn(deps, "talk to a person")
    assert accept.trigger_type == "human_request" and accept.handoff_queued


def test_loop_breakers_are_pressure_free_and_distinct() -> None:
    assert len(set(LOOP_BREAKERS)) == len(LOOP_BREAKERS)
    banned = ["limited time", "act now", "hurry", "last chance", "before it's too late", "deadline", "only today"]
    for text in LOOP_BREAKERS:
        assert not any(b in text.lower() for b in banned)
        assert "talk to a person" in text or "talk to a person" in text.replace("\"", "")
    streaks = [loop_breaker(i) for i in range(1, 8)]
    for a, b in zip(streaks, streaks[1:]):
        assert a != b


def test_streak_resets_when_scripted_response_changes(deps) -> None:
    turn(deps, "ok"); turn(deps, "hmm")
    r = turn(deps, "I'm not sure about the price, it seems too expensive.")  # moves to OBJECTION script
    assert r.context.metadata[KEY_REPEAT_STREAK] == 0
    assert r.customer_message not in LOOP_BREAKERS


def test_last_prompt_stays_in_context_across_turns(deps) -> None:
    r1 = turn(deps, "ok")
    r2 = turn(deps, "hmm")
    assert r1.context.metadata[KEY_LAST_BASE_RESPONSE] == r2.context.metadata[KEY_LAST_BASE_RESPONSE]
    assert r2.context.metadata[KEY_LAST_BASE_RESPONSE]  # remembered, not dropped


def test_loop_guard_does_not_replace_fit_check_at_decision_ready() -> None:
    """The fit check is functionally specific; a generic breaker would be a soul.md priority-2 regression."""
    from src.core.lead_context import LeadContext
    from src.domain.session_state import persist_trust_state
    from src.orchestrator import guard_against_repetition

    meta: dict = {}
    fit = CustomerBehaviorEngine().generate_response(
        LeadContext(lead_id="x"), {"trust_state": TrustState.DECISION_READY, "fit_confirmed": False}
    )
    assert guard_against_repetition(meta, fit, exempt=True) == fit
    assert guard_against_repetition(meta, fit, exempt=True) == fit


def test_holding_conversation_does_not_corrupt_loop_memory(deps) -> None:
    turn(deps, "ok")
    turn(deps, "Can I talk to a real person?")  # holding turn: no scripted text generated
    after = turn(deps, "hmm")                    # still holding
    assert after.customer_message in APPROVED_HOLDING_RESPONSES


# ===========================================================================
# B. Trust progression: skepticism is not an escalation
# ===========================================================================

SKEPTICAL = [
    "I'm not convinced another AI tool will work for us.",
    "Honestly I'm skeptical, we've been burned before.",
    "I doubt AI can qualify our leads the way our reps do.",
]


@pytest.mark.parametrize("message", SKEPTICAL)
@pytest.mark.parametrize("online,live,approval", [(True, False, False), (False, False, False)])
def test_skepticism_never_triggers_alert_relay_or_handoff(deps, message, online, live, approval) -> None:
    turn(deps, "Tell me more about how this works.", online=online)  # reach CURIOSITY
    r = turn(deps, message, online=online, live_session=live, awaiting_approval=approval)
    assert r.handoff_triggered is False
    assert r.collaboration_mode == CollaborationMode.AUTONOMOUS
    assert r.delivery_status == DeliveryStatus.DELIVERED.value


@pytest.mark.parametrize("message", SKEPTICAL)
def test_skepticism_moves_trust_to_objection_and_gets_validating_reply(deps, message) -> None:
    turn(deps, "Tell me more about how this works.")
    r = turn(deps, message)
    assert r.trust_state == TrustState.OBJECTION
    assert "not to talk you into anything" in r.customer_message  # validate before problem-solving


def test_skepticism_and_agent_frustration_are_distinguished(deps) -> None:
    skeptic = turn(deps, "I'm not convinced another AI tool will work.", lead="s")
    angry = turn(deps, "You keep ignoring my question, this is ridiculous.", lead="a")
    assert skeptic.handoff_triggered is False
    assert angry.handoff_triggered is True and angry.trigger_type == "frustration"


# ===========================================================================
# C. Interpretation failure
# ===========================================================================

class Boom:
    def extract(self, message):
        raise RuntimeError("interpreter down")


@pytest.mark.parametrize("blank", ["", "   ", "\n\t"])
def test_blank_message_does_not_advance_trust(deps, blank) -> None:
    r = turn(deps, blank)
    assert r.interpretation_status == "empty"
    assert r.trust_state == TrustState.AWARENESS
    assert r.customer_message  # still answered, never a crash or silence


def test_blank_message_does_not_regress_established_trust(deps) -> None:
    turn(deps, "Tell me more about how this works.")
    before = turn(deps, "What does it cost to pilot?").trust_state
    after = turn(deps, "   ").trust_state
    assert after == before


def test_extractor_exception_falls_back_to_rule_based_and_still_honors_human_request(deps) -> None:
    d, queue = deps
    d["signal_extractor"] = Boom()
    r = turn(deps, "Can I talk to a real person?")
    assert r.interpretation_status == "fallback"
    assert r.handoff_queued and queue.size() == 1
    assert r.customer_message in APPROVED_HOLDING_RESPONSES


def test_total_interpretation_failure_preserves_trust_and_pending_handoff(monkeypatch) -> None:
    deps = make()
    r1 = turn(deps, "Tell me more about how this works.", lead="f")
    turn(deps, "Can I talk to a real person?", lead="f")

    import src.orchestrator as orch
    monkeypatch.setattr(orch, "LeadSignalExtractor", Boom)  # fallback fails too
    deps[0]["signal_extractor"] = Boom()
    r3 = turn(deps, "anything", lead="f")
    assert r3.interpretation_status == "failed"
    assert r3.trust_state == r1.trust_state
    assert r3.human_intervention_open is True
    assert r3.customer_message in APPROVED_HOLDING_RESPONSES


def test_interpret_message_contract() -> None:
    ex = LeadSignalExtractor()
    assert interpret_message(ex, "hello")[1] == "ok"
    assert interpret_message(ex, "")[1] == "empty"
    assert interpret_message(Boom(), "hello")[1] == "fallback"


# ===========================================================================
# D. Soul value 6: honesty about being an AI
# ===========================================================================

@pytest.mark.parametrize(
    "message",
    ["Are you a bot or an AI?", "Am I talking to a real person?", "Is this a bot?", "Are you a human?"],
)
def test_identity_questions_are_detected_and_not_treated_as_handoff_requests(deps, message) -> None:
    assert detect_identity_question(message) is True
    assert detect_human_request(message) is False
    r = turn(deps, message, online=True)
    assert r.handoff_triggered is False
    assert "AI assistant" in r.customer_message and "not a human" in r.customer_message


def test_identity_disclosure_is_not_replaced_by_loop_breaker(deps) -> None:
    for _ in range(3):
        r = turn(deps, "Are you a bot?")
        assert "AI assistant" in r.customer_message


def test_identity_question_plus_explicit_request_hands_off_and_still_discloses(deps) -> None:
    r = turn(deps, "Are you a bot? I want to talk to a real person.")
    assert r.trigger_type == "human_request" and r.handoff_queued
    assert "AI assistant" in r.customer_message


def test_human_request_holding_copy_states_ai_nature(deps) -> None:
    r = turn(deps, "Can I talk to a real person?")
    assert "AI assistant" in r.customer_message


def test_identity_question_during_frustration_hold_still_discloses(deps) -> None:
    r = turn(deps, "You're useless, this is ridiculous. Are you even a person?")
    assert r.trigger_type == "frustration"
    assert "AI assistant" in r.customer_message


def test_ai_agent_product_questions_are_still_not_human_requests() -> None:
    assert detect_human_request("Tell me about your AI agent.") is False
