"""Phase 0: end-to-end run_turn behavior (audit Findings 2-5).

These go through the real orchestrator — not pre-built signal dicts — so they
cover the wiring between extractor, handoff manager, mode machine, delivery
policy and the queue.
"""

import pytest

from src.collaboration.delivery_policy import DeliveryStatus
from src.collaboration.mode_state_machine import CollaborationMode
from src.customer_layer.holding_responses import APPROVED_HOLDING_RESPONSES
from src.domain.session_state import (
    KEY_PENDING_DRAFTS,
    first_open_human_trigger,
    pending_relay_drafts,
    release_relay_draft,
    resolve_interventions,
)
from src.orchestrator import build_default_dependencies, run_turn

HUMAN = "Can I talk to a real person?"
NEUTRAL = "Tell me more about how this works."


@pytest.fixture
def deps():
    store, extractor, engine, rep_engine, manager, machine, queue = build_default_dependencies()
    return dict(
        store=store,
        signal_extractor=extractor,
        customer_engine=engine,
        rep_engine=rep_engine,
        handoff_manager=manager,
        mode_machine=machine,
    ), queue


def turn(deps, message, *, lead="L1", rep_online=False, live_session=False, awaiting_approval=False):
    d, _ = deps
    return run_turn(
        lead_id=lead,
        raw_message=message,
        rep_online=rep_online,
        live_session=live_session,
        awaiting_approval=awaiting_approval,
        **d,
    )


# --- Finding 5: offline rep must not erase the handoff ----------------------

def test_human_request_is_queued_when_rep_offline(deps) -> None:
    _, queue = deps
    r = turn(deps, HUMAN, rep_online=False)
    assert r.collaboration_mode == CollaborationMode.AUTONOMOUS  # mode machine contract unchanged
    assert r.handoff_triggered and r.trigger_type == "human_request"
    assert r.handoff_queued is True
    assert queue.size() == 1
    task = queue.dequeue()
    assert task.payload["trigger_type"] == "human_request"
    assert task.payload["rep_online_at_trigger"] is False
    assert task.payload["alert_brief"]["trigger"] == "human_request"


def test_human_request_offline_gets_holding_not_agent_response(deps) -> None:
    r = turn(deps, HUMAN, rep_online=False)
    assert r.delivery_status == DeliveryStatus.HOLDING.value
    assert r.customer_message in APPROVED_HOLDING_RESPONSES
    assert r.human_intervention_open is True


def test_human_request_online_queues_and_holds(deps) -> None:
    _, queue = deps
    r = turn(deps, HUMAN, rep_online=True)
    assert r.collaboration_mode == CollaborationMode.ALERT
    assert queue.size() == 1
    assert r.customer_message in APPROVED_HOLDING_RESPONSES


def test_handoff_queued_in_every_collaboration_state(deps) -> None:
    for i, (online, live, approval) in enumerate(
        [(False, False, False), (True, False, False), (True, True, False), (True, False, True)]
    ):
        r = turn(deps, HUMAN, lead=f"L-{i}", rep_online=online, live_session=live, awaiting_approval=approval)
        assert r.handoff_queued is True, (online, live, approval)
        assert r.customer_message in APPROVED_HOLDING_RESPONSES, (online, live, approval)
    assert deps[1].size() == 4


def test_human_requirement_persists_after_agent_would_resume(deps) -> None:
    """Turn 2 is innocuous. The unresolved human request must still hold the conversation."""
    turn(deps, HUMAN, rep_online=False)
    r2 = turn(deps, NEUTRAL, rep_online=False)
    assert r2.delivery_status == DeliveryStatus.HOLDING.value
    assert r2.customer_message in APPROVED_HOLDING_RESPONSES
    assert r2.human_intervention_open is True


def test_followup_copy_and_no_duplicate_queueing(deps) -> None:
    _, queue = deps
    r1 = turn(deps, HUMAN)
    r2 = turn(deps, "Hello?? I said I want to speak to a person.")
    assert r1.customer_message != r2.customer_message  # first-contact vs follow-up copy
    assert r2.handoff_triggered is True and r2.handoff_queued is False
    assert queue.size() == 1


def test_rep_going_offline_preserves_pending_intervention(deps) -> None:
    """Online ALERT, then the rep drops: requirement survives, interruption is recorded."""
    r1 = turn(deps, HUMAN, rep_online=True)
    assert r1.collaboration_mode == CollaborationMode.ALERT
    r2 = turn(deps, NEUTRAL, rep_online=False)
    assert r2.collaboration_mode == CollaborationMode.AUTONOMOUS
    assert r2.delivery_status == DeliveryStatus.HOLDING.value
    events = r2.context.handoff_queue
    assert any(e.get("reason") == "rep_went_offline" and e.get("interrupted_mode") == CollaborationMode.ALERT for e in events)
    assert first_open_human_trigger(r2.context.metadata) == "human_request"


def test_mode_stays_alert_while_human_intervention_open_and_rep_online(deps) -> None:
    turn(deps, HUMAN, rep_online=True)
    r2 = turn(deps, NEUTRAL, rep_online=True)
    assert r2.collaboration_mode == CollaborationMode.ALERT
    assert r2.customer_message in APPROVED_HOLDING_RESPONSES


def test_resolving_intervention_lets_agent_resume(deps) -> None:
    r1 = turn(deps, HUMAN, rep_online=True)
    assert resolve_interventions(r1.context.metadata) == 1
    r2 = turn(deps, NEUTRAL, rep_online=True)
    assert r2.collaboration_mode == CollaborationMode.AUTONOMOUS
    assert r2.delivery_status == DeliveryStatus.DELIVERED.value
    assert r2.customer_message not in APPROVED_HOLDING_RESPONSES


# --- Finding 1 end-to-end ---------------------------------------------------

def test_previous_vendor_frustration_does_not_hand_off(deps) -> None:
    _, queue = deps
    r = turn(deps, "I'm so frustrated with our previous vendor, their scoring was a waste of time.", rep_online=True)
    assert r.handoff_triggered is False
    assert queue.size() == 0
    assert r.collaboration_mode == CollaborationMode.AUTONOMOUS
    assert r.delivery_status == DeliveryStatus.DELIVERED.value


def test_agent_directed_frustration_holds_even_when_rep_offline(deps) -> None:
    _, queue = deps
    r = turn(deps, "You keep ignoring my question, this is ridiculous.", rep_online=False)
    assert r.trigger_type == "frustration" and r.handoff_queued
    assert queue.size() == 1
    assert r.customer_message in APPROVED_HOLDING_RESPONSES
    assert r.rep_alert_brief is not None


# --- Finding 3: ALERT is never silent ---------------------------------------

def test_alert_mode_always_returns_holding_response(deps) -> None:
    r = turn(deps, "Can you send a quote for this?", rep_online=True)  # pricing trigger -> ALERT
    assert r.collaboration_mode == CollaborationMode.ALERT
    assert r.customer_message in APPROVED_HOLDING_RESPONSES
    assert r.rep_alert_brief is not None


def test_non_human_trigger_offline_queues_but_agent_continues(deps) -> None:
    """Only human-required triggers hard-stop the agent while the rep is away."""
    _, queue = deps
    r = turn(deps, "We use Salesforce today.", rep_online=False)
    assert r.trigger_type == "competitor_mention"
    assert r.handoff_queued and queue.size() == 1
    assert r.delivery_status == DeliveryStatus.DELIVERED.value
    assert r.human_intervention_open is False


# --- Finding 4: RELAY never leaks a draft ------------------------------------

def test_relay_withholds_draft_from_customer(deps) -> None:
    r = turn(deps, NEUTRAL, rep_online=True, awaiting_approval=True)
    assert r.collaboration_mode == CollaborationMode.RELAY
    assert r.customer_message is None
    assert r.delivery_status == DeliveryStatus.PENDING_APPROVAL.value
    assert r.pending_draft and r.pending_draft_id
    drafts = pending_relay_drafts(r.context.metadata)
    assert [d["draft_id"] for d in drafts] == [r.pending_draft_id]


def test_relay_draft_reaches_customer_only_via_release(deps) -> None:
    r = turn(deps, NEUTRAL, rep_online=True, awaiting_approval=True)
    assert r.context.metadata.get("customer_outbox", []) == []
    text = release_relay_draft(r.context.metadata, r.pending_draft_id)
    assert text == r.pending_draft
    assert r.context.metadata["customer_outbox"] == [{"draft_id": r.pending_draft_id, "message": text}]
    # Cannot be released twice.
    assert release_relay_draft(r.context.metadata, r.pending_draft_id) is None


def test_newer_relay_draft_supersedes_older(deps) -> None:
    r1 = turn(deps, NEUTRAL, rep_online=True, awaiting_approval=True)
    r2 = turn(deps, "What about timelines?", rep_online=True, awaiting_approval=True)
    assert release_relay_draft(r2.context.metadata, r1.pending_draft_id) is None
    assert release_relay_draft(r2.context.metadata, r2.pending_draft_id) is not None


def test_human_request_discards_staged_relay_draft(deps) -> None:
    r1 = turn(deps, NEUTRAL, rep_online=True, awaiting_approval=True)
    assert r1.pending_draft_id
    r2 = turn(deps, HUMAN, rep_online=True, awaiting_approval=True)
    assert r2.customer_message in APPROVED_HOLDING_RESPONSES
    assert r2.context.metadata[KEY_PENDING_DRAFTS] == []
    assert release_relay_draft(r2.context.metadata, r1.pending_draft_id) is None


def test_relay_offline_falls_back_to_autonomous_by_design(deps) -> None:
    """Documents the existing mode-machine contract (offline -> AUTONOMOUS) so a
    change to it is a deliberate decision, not an accident. See Phase 0 notes."""
    r = turn(deps, NEUTRAL, rep_online=False, awaiting_approval=True)
    assert r.collaboration_mode == CollaborationMode.AUTONOMOUS
    assert r.delivery_status == DeliveryStatus.DELIVERED.value


# --- SHADOW -------------------------------------------------------------------

def test_shadow_returns_suggestion_not_customer_message(deps) -> None:
    r = turn(deps, NEUTRAL, rep_online=True, live_session=True)
    assert r.collaboration_mode == CollaborationMode.SHADOW
    assert r.customer_message is None
    assert r.rep_suggestion
    assert r.delivery_status == DeliveryStatus.REP_SUGGESTION.value


# --- Cross-lead isolation -----------------------------------------------------

def test_one_leads_alert_does_not_bleed_into_another(deps) -> None:
    turn(deps, HUMAN, lead="A", rep_online=True)  # leaves the shared machine in ALERT
    r = turn(deps, NEUTRAL, lead="B", rep_online=False)
    assert r.collaboration_mode == CollaborationMode.AUTONOMOUS
    assert r.delivery_status == DeliveryStatus.DELIVERED.value
    assert not any(e.get("reason") == "rep_went_offline" for e in r.context.handoff_queue)


def test_last_trigger_is_persisted_for_brief_endpoint(deps) -> None:
    r = turn(deps, HUMAN)
    assert r.context.metadata["last_trigger_type"] == "human_request"
