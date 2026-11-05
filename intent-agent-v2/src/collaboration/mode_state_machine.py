"""Collaboration mode state machine for sales lifecycle orchestration."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.core.lead_context import LeadContext


class CollaborationMode(str, Enum):
    """System collaboration modes between autonomous agent and sales rep."""

    AUTONOMOUS = "AUTONOMOUS"
    ALERT = "ALERT"
    SHADOW = "SHADOW"
    RELAY = "RELAY"


class ModeStateMachine:
    """Controls mode transitions for customer-rep collaboration.

    Transition priority is intentional: operational safety states (offline,
    handoff) are evaluated before interaction optimization states.
    """

    def __init__(self) -> None:
        self.current_mode: CollaborationMode = CollaborationMode.AUTONOMOUS

    def get_mode(self) -> CollaborationMode:
        """Return the current collaboration mode."""
        return self.current_mode

    def transition(
        self,
        rep_online: bool,
        live_session: bool,
        handoff_triggered: bool,
        awaiting_approval: bool,
        context: Optional["LeadContext"] = None,
    ) -> CollaborationMode:
        """Transition to the next mode based on current sales conditions.

        Rules map to common sales lifecycle phases:
        - Offline coverage keeps automation active so leads are never dropped.
        - Handoff triggers escalate attention when autonomous flow detects risk.
        - Live sessions with reps enable "shadow" assistance in real time.
        - Awaiting approval routes messages through rep confirmation before send.

        **Edge case:** If both ``handoff_triggered`` and ``awaiting_approval`` are
        true, **ALERT** wins (escalation before approval gating). If the rep is
        **offline**, mode is **AUTONOMOUS** regardless of other flags.

        **AUTONOMOUS-when-offline describes who can respond, not whether a human
        is required.** This machine only models rep availability. Whether a
        handoff is open, and what the customer may be sent while it is, is owned
        by the orchestrator (``domain.session_state`` pending interventions) and
        ``collaboration.delivery_policy``. Callers must queue the handoff and
        apply the delivery policy independently of the mode returned here.
        """
        # Rep unavailable: keep system autonomous to maintain lead continuity.
        if not rep_online:
            prior_mode = self.current_mode
            self.current_mode = CollaborationMode.AUTONOMOUS
            if context is not None and prior_mode in (
                CollaborationMode.ALERT,
                CollaborationMode.RELAY,
                CollaborationMode.SHADOW,
            ):
                context.add_handoff_event(
                    {
                        "interrupted_mode": prior_mode,
                        "reason": "rep_went_offline",
                    }
                )
            return self.current_mode

        # Explicit handoff signal indicates urgent context shift needing attention.
        if handoff_triggered:
            self.current_mode = CollaborationMode.ALERT
            return self.current_mode

        # Approval gate means rep must relay/approve before customer delivery.
        if awaiting_approval:
            self.current_mode = CollaborationMode.RELAY
            return self.current_mode

        # Rep in an active live touchpoint: assistant should support in shadow mode.
        if rep_online and live_session:
            self.current_mode = CollaborationMode.SHADOW
            return self.current_mode

        # Rep online but not in a live session defaults to autonomous handling.
        self.current_mode = CollaborationMode.AUTONOMOUS
        return self.current_mode
