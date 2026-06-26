"""Unit tests: collaboration mode state machine.

Gap tests added (soul.md alignment):
- Silent offline drop must emit a handoff_queue event so the rep has full
  context when they return (soul.md value 4: no information loss at handoff).
"""

import pytest

from src.collaboration.mode_state_machine import CollaborationMode, ModeStateMachine
from src.core.lead_context import LeadContext


# ---------------------------------------------------------------------------
# Existing tests — unchanged
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "rep_online,live_session,handoff_triggered,awaiting_approval,expected",
    [
        # Rep offline always autonomous (continuity over escalation).
        (False, True, True, False, CollaborationMode.AUTONOMOUS),
        # Handoff while rep online -> alert.
        (True, False, True, False, CollaborationMode.ALERT),
        # Both handoff and approval: ALERT wins over RELAY.
        (True, False, True, True, CollaborationMode.ALERT),
        # Approval gate -> relay before shadow/autonomous fallthrough.
        (True, True, False, True, CollaborationMode.RELAY),
        # Live session with rep, no handoff/approval -> shadow.
        (True, True, False, False, CollaborationMode.SHADOW),
        # Rep online, idle -> autonomous.
        (True, False, False, False, CollaborationMode.AUTONOMOUS),
    ],
)
def test_mode_transition_matrix(
    rep_online: bool,
    live_session: bool,
    handoff_triggered: bool,
    awaiting_approval: bool,
    expected: CollaborationMode,
) -> None:
    machine = ModeStateMachine()
    out = machine.transition(
        rep_online=rep_online,
        live_session=live_session,
        handoff_triggered=handoff_triggered,
        awaiting_approval=awaiting_approval,
    )
    assert out == expected
    assert machine.get_mode() == expected


# ---------------------------------------------------------------------------
# Gap — Silent offline drop loses handoff context
# (soul.md value 4: no information loss at handoff)
#
# When the rep goes offline mid-ALERT or mid-RELAY, ModeStateMachine
# currently resets to AUTONOMOUS silently. LeadContext.handoff_queue
# receives no event, so the rep returns to mode=AUTONOMOUS with no record
# that an alert was in flight.
#
# soul.md value 4: "always brief the human rep with full context — no
# information loss at handoff." A dropped alert is a form of information loss.
#
# The expected fix: when transition() resets to AUTONOMOUS due to
# rep_online=False, it should call context.add_handoff_event() with the
# interrupted mode so the queue preserves what was dropped.
#
# These tests will FAIL until ModeStateMachine.transition() accepts an
# optional LeadContext and emits the interruption event on offline drop.
# ---------------------------------------------------------------------------

@pytest.fixture
def alert_context() -> LeadContext:
    """A lead context mid-ALERT when the rep goes offline."""
    ctx = LeadContext(lead_id="L-alert-1", sentiment="neutral")
    ctx.collaboration_mode = CollaborationMode.ALERT
    return ctx


@pytest.fixture
def relay_context() -> LeadContext:
    """A lead context mid-RELAY when the rep goes offline."""
    ctx = LeadContext(lead_id="L-relay-1", sentiment="neutral")
    ctx.collaboration_mode = CollaborationMode.RELAY
    return ctx


def test_offline_drop_from_alert_emits_handoff_queue_event(
    alert_context: LeadContext,
) -> None:
    """Going offline mid-ALERT must record an interruption event in handoff_queue.

    soul.md value 4 — no information loss at handoff: the rep who comes back
    online must be able to see that an ALERT was in progress when they went
    offline. Without this event, the queue shows nothing and the rep has no
    context.
    """
    machine = ModeStateMachine()
    machine.current_mode = CollaborationMode.ALERT

    machine.transition(
        rep_online=False,
        live_session=False,
        handoff_triggered=False,
        awaiting_approval=False,
        context=alert_context,  # expected new parameter
    )

    assert machine.get_mode() == CollaborationMode.AUTONOMOUS, (
        "Mode must reset to AUTONOMOUS when rep goes offline."
    )
    assert len(alert_context.handoff_queue) > 0, (
        "handoff_queue must contain an interruption event when offline drop "
        "occurs mid-ALERT. soul.md value 4: no information loss at handoff."
    )
    event = alert_context.handoff_queue[-1]
    assert event.get("interrupted_mode") == CollaborationMode.ALERT, (
        "Interruption event must record the mode that was dropped (ALERT)."
    )
    assert "reason" in event, (
        "Interruption event must include a reason field explaining the drop."
    )


def test_offline_drop_from_relay_emits_handoff_queue_event(
    relay_context: LeadContext,
) -> None:
    """Going offline mid-RELAY must record an interruption event in handoff_queue.

    Same soul.md constraint as ALERT — RELAY represents a draft awaiting rep
    approval. If the rep goes offline before approving, the pending draft
    must not disappear silently from the queue.
    """
    machine = ModeStateMachine()
    machine.current_mode = CollaborationMode.RELAY

    machine.transition(
        rep_online=False,
        live_session=False,
        handoff_triggered=False,
        awaiting_approval=False,
        context=relay_context,
    )

    assert machine.get_mode() == CollaborationMode.AUTONOMOUS
    assert len(relay_context.handoff_queue) > 0, (
        "handoff_queue must contain an interruption event when offline drop "
        "occurs mid-RELAY. soul.md value 4: no information loss at handoff."
    )
    event = relay_context.handoff_queue[-1]
    assert event.get("interrupted_mode") == CollaborationMode.RELAY


def test_offline_drop_from_autonomous_does_not_emit_event() -> None:
    """Going offline while already AUTONOMOUS must not emit a spurious event.

    Only interrupted active modes (ALERT, RELAY, SHADOW) warrant a queue
    event. Dropping from AUTONOMOUS to AUTONOMOUS is not an interruption —
    no information is lost.
    """
    ctx = LeadContext(lead_id="L-auto-1", sentiment="neutral")
    ctx.collaboration_mode = CollaborationMode.AUTONOMOUS

    machine = ModeStateMachine()
    machine.current_mode = CollaborationMode.AUTONOMOUS

    machine.transition(
        rep_online=False,
        live_session=False,
        handoff_triggered=False,
        awaiting_approval=False,
        context=ctx,
    )

    assert len(ctx.handoff_queue) == 0, (
        "No interruption event should be emitted when dropping from "
        "AUTONOMOUS — no active mode was interrupted."
    )


def test_offline_drop_from_shadow_emits_handoff_queue_event() -> None:
    """Going offline mid-SHADOW must also record an interruption event.

    SHADOW mode means the rep is live and the agent is supporting them.
    If the rep drops offline, the shadow context should be preserved so
    the rep can resume with full conversation awareness.
    """
    ctx = LeadContext(lead_id="L-shadow-1", sentiment="neutral")
    ctx.collaboration_mode = CollaborationMode.SHADOW

    machine = ModeStateMachine()
    machine.current_mode = CollaborationMode.SHADOW

    machine.transition(
        rep_online=False,
        live_session=False,
        handoff_triggered=False,
        awaiting_approval=False,
        context=ctx,
    )

    assert machine.get_mode() == CollaborationMode.AUTONOMOUS
    assert len(ctx.handoff_queue) > 0, (
        "handoff_queue must contain an interruption event when offline drop "
        "occurs mid-SHADOW."
    )
    event = ctx.handoff_queue[-1]
    assert event.get("interrupted_mode") == CollaborationMode.SHADOW
