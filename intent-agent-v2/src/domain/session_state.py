"""Well-known keys and helpers for persisted session state (avoids metadata typos).

Internal state (trust, mode) is stored on ``LeadContext.metadata`` for serialization
simplicity; helpers keep customer vs system boundaries explicit.
"""

from __future__ import annotations

from typing import Any, Final, Optional

from src.collaboration.mode_state_machine import CollaborationMode, ModeStateMachine
from src.customer_layer.trust_state_machine import TrustState, TrustStateMachine

KEY_PSYCHOLOGICAL_TRUST: Final[str] = "psychological_trust_state"
KEY_COLLABORATION_MODE: Final[str] = "collaboration_mode"
# Reserved for rep-only CRM notes — must never be copied into customer responses.
KEY_REP_INTERNAL_NOTES: Final[str] = "rep_internal_notes"


def hydrate_trust_machine(context_metadata: dict[str, Any]) -> TrustStateMachine:
    """Restore trust FSM from prior turn."""
    machine = TrustStateMachine()
    raw = context_metadata.get(KEY_PSYCHOLOGICAL_TRUST)
    if isinstance(raw, str) and raw:
        try:
            machine.current_state = TrustState[raw]
        except KeyError:
            pass
    return machine


def persist_trust_state(metadata: dict[str, Any], state: TrustState) -> None:
    metadata[KEY_PSYCHOLOGICAL_TRUST] = state.name


def hydrate_mode_machine(machine: ModeStateMachine, stored: Optional[str]) -> None:
    """Restore collaboration mode from persisted context."""
    if not stored:
        return
    try:
        machine.current_mode = CollaborationMode(stored)
    except ValueError:
        pass


def persist_collaboration_mode(metadata: dict[str, Any], mode: CollaborationMode) -> None:
    metadata[KEY_COLLABORATION_MODE] = mode.value
