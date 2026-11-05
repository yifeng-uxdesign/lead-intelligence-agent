"""Roadmap steps 1-2: decision trace and the context / attention / intervention taxonomy."""

import pytest

from src.application.signal_adapters import handoff_signal_dict_from_lead
from src.collaboration.delivery_policy import DeliveryStatus
from src.collaboration.mode_state_machine import CollaborationMode
from src.core.lead_context import LeadContext
from src.customer_layer.holding_responses import APPROVED_HOLDING_RESPONSES, holding_response
from src.domain.session_state import decision_traces, rep_notices
from src.domain.trigger_catalog import (
    HUMAN_REQUIRED_TRIGGERS,
    TRIGGER_CLASS,
    TRIGGER_PRECEDENCE,
    HandoffTriggerType,
    TriggerClass,
    trigger_class,
)
from src.orchestrator import build_default_dependencies, run_turn
from src.signals.extractor import LeadSignals

_SIG = dict(intent="general", urgency="medium", sentiment="neutral", objection_type="none",
            human_request=False, competitor_mention=False, buying_signal=False, stakeholder_signal=False)


@pytest.fixture
def deps():
    store, extractor, engine, rep_engine, manager, machine, queue = build_default_dependencies()
    return dict(store=store, signal_extractor=extractor, customer_engine=engine,
                rep_engine=rep_engine, handoff_manager=manager, mode_machine=machine), queue


def turn(deps, message, *, lead="L1", rep_online=True, **kw):
    d, _ = deps
    return run_turn(lead_id=lead, raw_message=message, rep_online=rep_online, **{**d, **kw})


def payload(message, **signals):
    return handoff_signal_dict_from_lead(LeadSignals(**{**_SIG, **signals}), message)


# --- catalog -----------------------------------------------------------------

def test_every_trigger_has_a_class_and_a_precedence_slot():
    real = {t.value for t in HandoffTriggerType} - {"none"}
    assert set(TRIGGER_CLASS) == real == set(TRIGGER_PRECEDENCE)


def test_precedence_orders_classes_intervention_attention_context():
    rank = {TriggerClass.INTERVENTION: 0, TriggerClass.ATTENTION: 1, TriggerClass.CONTEXT: 2}
    ranks = [rank[TRIGGER_CLASS[t]] for t in TRIGGER_PRECEDENCE]
    assert ranks == sorted(ranks)


def test_d4_class_assignments():
    assert HUMAN_REQUIRED_TRIGGERS == {"human_request", "frustration", "commitment_demand",
                                       "pricing_negotiation", "contract_legal_ask"}
    assert trigger_class("strong_buying_signal") is TriggerClass.ATTENTION
    assert trigger_class("pricing_discussion") is TriggerClass.ATTENTION
    assert trigger_class("competitor_mention") is TriggerClass.CONTEXT
    assert trigger_class("stakeholder_approval_needed") is TriggerClass.CONTEXT


def test_every_intervention_has_specific_holding_copy():
    generic = holding_response("unknown")
    for t in HUMAN_REQUIRED_TRIGGERS:
        text = holding_response(t)
        assert text in APPROVED_HOLDING_RESPONSES and text != generic, t


# --- lexical detection: narrow on purpose ------------------------------------

@pytest.mark.parametrize("msg,key", [
    ("Can you give us a 30% discount if we sign this quarter?", "pricing_negotiation"),
    ("Could you match their price?", "pricing_negotiation"),
    ("Will you commit to that in writing?", "commitment_demand"),
    ("If it doesn't work, do we get a refund?", "commitment_demand"),
    ("Can our legal team redline your contract terms?", "contract_legal_ask"),
    ("Can you send over your MSA and DPA?", "contract_legal_ask"),
])
def test_intervention_lexemes_fire(msg, key):
    p = payload(msg)
    assert p[key] is True and key in p["_evidence"]


@pytest.mark.parametrize("msg", [
    "Who is accountable if the agent qualifies a lead wrong?",   # question, agent answers
    "Can you guarantee a 30% lift in conversion?",               # capability question
    "We use Salesforce and our legal team reviews every vendor we bring in.",
    "We have budget approved. What do we need to sign?",
    "What does it cost to pilot this?",
])
def test_non_interventions_do_not_fire(msg):
    p = payload(msg)
    assert not (p["pricing_negotiation"] or p["commitment_demand"] or p["contract_legal_ask"])


def test_manager_returns_all_hits_primary_first(deps):
    d, _ = deps
    hits = d["handoff_manager"].evaluate(
        payload("what's the price? we use a competitor", buying_signal=True, competitor_mention=True),
        LeadContext(lead_id="x"),
    )
    assert [h.trigger_type for h in hits] == ["strong_buying_signal", "pricing_discussion", "competitor_mention"]
    assert [h.trigger_class for h in hits] == ["attention", "attention", "context"]


# --- orchestration -----------------------------------------------------------

def test_pricing_interest_notifies_rep_and_agent_keeps_answering(deps):
    _, queue = deps
    r = turn(deps, "What does it cost to pilot this?")
    assert r.trigger_type == "pricing_discussion"
    assert r.collaboration_mode == CollaborationMode.AUTONOMOUS
    assert r.delivery_status == DeliveryStatus.DELIVERED.value
    assert r.customer_message not in APPROVED_HOLDING_RESPONSES
    assert r.handoff_queued and not r.human_intervention_open
    assert queue.dequeue().payload["trigger_class"] == "attention"


def test_buying_before_fit_never_announces_a_handoff(deps):
    r = turn(deps, "I'm ready to move forward, let's do this.")
    assert r.delivery_status == DeliveryStatus.DELIVERED.value
    low = r.customer_message.lower()
    assert "connect you" not in low and "follow up with you" not in low


def test_context_notice_is_sent_once_per_lead(deps):
    _, queue = deps
    turn(deps, "We use Salesforce today.")
    turn(deps, "Salesforce is where everything lives.")
    assert queue.size() == 1
    notices = rep_notices(deps[0]["store"].get("L1").metadata)
    assert [n["trigger_type"] for n in notices] == ["competitor_mention"]


def test_intervention_outranks_attention_in_same_turn(deps):
    r = turn(deps, "We're ready to buy if you give us a 20% discount.", rep_online=False)
    assert r.trigger_type == "pricing_negotiation"
    assert r.delivery_status == DeliveryStatus.HOLDING.value and r.human_intervention_open


# --- decision trace ----------------------------------------------------------

def test_trace_explains_a_hold(deps):
    r = turn(deps, "Can I talk to a real person?")
    t = r.decision_trace
    assert t.outcome == "held" and t.intervention_action == "opened"
    assert t.primary_trigger == "human_request" and t.primary_class == "intervention"
    assert t.rep_notified and "human_request" in t.rep_notified_reason
    assert t.response_source == "holding:human_request"
    assert "intervention" in t.delivery_reason


def test_trace_explains_a_follow_up_hold_and_no_renotify(deps):
    turn(deps, "Can I talk to a real person?")
    t = turn(deps, "ok thanks").decision_trace
    assert t.intervention_action == "carried_over" and t.outcome == "held"
    assert not t.rep_notified and t.rep_notified_reason == "no trigger fired"
    assert t.response_source == "holding:follow_up"


def test_trace_explains_an_answer_with_attention_notice(deps):
    t = turn(deps, "What does it cost to pilot this?").decision_trace
    assert t.outcome == "answered" and t.intervention_action == "none"
    assert t.rep_notified and "[attention]" in t.rep_notified_reason
    assert t.mode == "AUTONOMOUS" and t.mode_reason
    assert t.triggers[0].evidence.startswith("text ")


def test_trace_covers_relay_and_shadow(deps):
    assert turn(deps, "hello", awaiting_approval=True).decision_trace.outcome == "drafted_for_rep"
    assert turn(deps, "hello", lead="L2", live_session=True).decision_trace.outcome == "suggested_to_rep"


def test_trace_is_persisted_and_capped(deps):
    for _ in range(55):
        turn(deps, "hello", rep_online=False)
    traces = decision_traces(deps[0]["store"].get("L1").metadata)
    assert len(traces) == 50 and traces[-1]["turn"] == 55
    assert traces[-1]["explanation"][-1].startswith("outcome:")
