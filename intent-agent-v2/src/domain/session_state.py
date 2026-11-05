"""Well-known keys and helpers for persisted session state (avoids metadata typos).

Internal state (trust, mode) is stored on ``LeadContext.metadata`` for serialization
simplicity; helpers keep customer vs system boundaries explicit.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, Final, List, Optional

from src.collaboration.mode_state_machine import CollaborationMode, ModeStateMachine
from src.customer_layer.trust_state_machine import TrustState, TrustStateMachine

KEY_PSYCHOLOGICAL_TRUST: Final[str] = "psychological_trust_state"
KEY_COLLABORATION_MODE: Final[str] = "collaboration_mode"
# Reserved for rep-only CRM notes — must never be copied into customer responses.
KEY_REP_INTERNAL_NOTES: Final[str] = "rep_internal_notes"

# --- Backend-owned authorization state (never accepted from the browser) -----
KEY_TURN_COUNT: Final[str] = "turn_count"
KEY_LAST_TRIGGER: Final[str] = "last_trigger_type"
KEY_LIVE_SESSION: Final[str] = "live_session"
KEY_APPROVAL_REQUIRED: Final[str] = "approval_required"
KEY_PENDING_INTERVENTIONS: Final[str] = "pending_interventions"
KEY_PENDING_DRAFTS: Final[str] = "pending_relay_drafts"
KEY_OUTBOX: Final[str] = "customer_outbox"
# Anti-loop memory: the last *scripted* agent response (before any loop-breaker
# substitution) and how many times in a row it would have repeated.
KEY_LAST_BASE_RESPONSE: Final[str] = "last_base_response"
KEY_REPEAT_STREAK: Final[str] = "repeat_streak"


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


# ---------------------------------------------------------------------------
# Turn counter / last trigger
# ---------------------------------------------------------------------------

def next_turn_number(metadata: dict[str, Any]) -> int:
    """Increment and return the 1-based turn counter."""
    n = int(metadata.get(KEY_TURN_COUNT, 0)) + 1
    metadata[KEY_TURN_COUNT] = n
    return n


def persist_last_trigger(metadata: dict[str, Any], trigger_type: str) -> None:
    metadata[KEY_LAST_TRIGGER] = trigger_type


# ---------------------------------------------------------------------------
# Pending human interventions
#
# An intervention is a handoff the rep has not resolved yet. It lives in
# metadata, NOT in the collaboration mode, so that a mode change (for example
# the rep going offline, which resets the mode to AUTONOMOUS) can never erase
# the fact that a human is required.
# ---------------------------------------------------------------------------

def open_intervention(
    metadata: dict[str, Any],
    trigger_type: str,
    *,
    human_required: bool,
    turn: int,
) -> bool:
    """Record an unresolved handoff. Returns False if this trigger is already open."""
    items: List[Dict[str, Any]] = metadata.setdefault(KEY_PENDING_INTERVENTIONS, [])
    if any(i.get("trigger_type") == trigger_type for i in items):
        return False
    items.append(
        {
            "trigger_type": trigger_type,
            "human_required": bool(human_required),
            "opened_turn": turn,
        }
    )
    return True


def open_interventions(metadata: dict[str, Any]) -> List[Dict[str, Any]]:
    return [dict(i) for i in metadata.get(KEY_PENDING_INTERVENTIONS, [])]


def first_open_human_trigger(metadata: dict[str, Any]) -> Optional[str]:
    """Oldest unresolved trigger that requires a human, if any."""
    for item in metadata.get(KEY_PENDING_INTERVENTIONS, []):
        if item.get("human_required"):
            return str(item.get("trigger_type"))
    return None


def has_open_human_intervention(metadata: dict[str, Any]) -> bool:
    return first_open_human_trigger(metadata) is not None


def resolve_interventions(metadata: dict[str, Any]) -> int:
    """Rep action: clear all pending interventions. Returns how many were cleared."""
    n = len(metadata.get(KEY_PENDING_INTERVENTIONS, []))
    metadata[KEY_PENDING_INTERVENTIONS] = []
    return n


# ---------------------------------------------------------------------------
# RELAY drafts and the customer outbox
#
# Drafts are rep-only. A draft reaches the customer outbox only through
# ``release_relay_draft``, which the API exposes solely behind rep auth.
# ---------------------------------------------------------------------------

def stage_relay_draft(metadata: dict[str, Any], text: str, *, turn: int) -> str:
    """Store a draft awaiting approval. A newer draft supersedes any older one."""
    draft_id = f"draft-{uuid.uuid4().hex[:12]}"
    metadata[KEY_PENDING_DRAFTS] = [
        {"draft_id": draft_id, "text": text, "created_turn": turn}
    ]
    return draft_id


def pending_relay_drafts(metadata: dict[str, Any]) -> List[Dict[str, Any]]:
    return [dict(d) for d in metadata.get(KEY_PENDING_DRAFTS, [])]


def discard_relay_drafts(metadata: dict[str, Any]) -> int:
    n = len(metadata.get(KEY_PENDING_DRAFTS, []))
    metadata[KEY_PENDING_DRAFTS] = []
    return n


def release_relay_draft(
    metadata: dict[str, Any],
    draft_id: str,
    *,
    edited_text: Optional[str] = None,
) -> Optional[str]:
    """Approve a pending draft: move it to the outbox and return the released text.

    Returns None when ``draft_id`` is not currently pending (unknown, already
    released, rejected, or superseded). A non-empty ``edited_text`` is the
    rep's own wording and replaces the agent draft.
    """
    drafts = metadata.get(KEY_PENDING_DRAFTS, [])
    match = next((d for d in drafts if d.get("draft_id") == draft_id), None)
    if match is None:
        return None
    text = (edited_text or "").strip() or str(match["text"])
    metadata[KEY_PENDING_DRAFTS] = [d for d in drafts if d is not match]
    metadata.setdefault(KEY_OUTBOX, []).append({"draft_id": draft_id, "message": text})
    return text


def reject_relay_draft(metadata: dict[str, Any], draft_id: str) -> bool:
    drafts = metadata.get(KEY_PENDING_DRAFTS, [])
    kept = [d for d in drafts if d.get("draft_id") != draft_id]
    metadata[KEY_PENDING_DRAFTS] = kept
    return len(kept) != len(drafts)


def drain_outbox(metadata: dict[str, Any]) -> List[Dict[str, Any]]:
    """Return and clear rep-approved messages waiting for the customer."""
    items = list(metadata.get(KEY_OUTBOX, []))
    metadata[KEY_OUTBOX] = []
    return items
