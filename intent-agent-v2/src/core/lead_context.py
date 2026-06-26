"""Shared memory core for lead-agent state.

This module defines a single, extensible context object that can be passed
between customer, rep, and collaboration layers. The structure is intentionally
simple so it can later be mapped to CRM records or event-store documents.

**Value constitution:** All behavioral constraints and their hierarchy are
governed by ``src/core/soul.md`` — consult it before adding fields or state that
affect customer-facing or rep-facing behavior.

**Layering:** use ``metadata`` only for serializable *system* state (trust FSM,
collaboration mode). Rep-only notes must use ``domain.session_state.KEY_REP_INTERNAL_NOTES``
and must never be fed to ``CustomerBehaviorEngine``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Aligns with ``CollaborationMode`` default until first orchestrated turn.
_DEFAULT_MODE = "AUTONOMOUS"


@dataclass
class LeadContext:
    """Canonical state container for one lead lifecycle.

    The fields represent shared memory used by all behavior layers.
    Keep this object stable and additive to simplify future CRM integration.
    """

    lead_id: str
    customer_state: str = "new"
    collaboration_mode: str = _DEFAULT_MODE
    lead_score: int = 0
    sentiment: str = "neutral"
    rep_online: bool = False
    assigned_rep: Optional[str] = None
    handoff_queue: List[Dict[str, Any]] = field(default_factory=list)
    conversation_summary: str = ""
    crm_record_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def update_summary(self, text: str) -> None:
        """Append text to the conversation summary with safe spacing."""
        normalized = text.strip()
        if not normalized:
            return

        if self.conversation_summary:
            self.conversation_summary = f"{self.conversation_summary} {normalized}"
        else:
            self.conversation_summary = normalized

    def update_sentiment(self, sentiment: str) -> None:
        """Update lead sentiment from classifier or agent inference."""
        self.sentiment = sentiment.strip().lower() if sentiment else "neutral"

    def add_handoff_event(self, event: Dict[str, Any]) -> None:
        """Add a handoff event for inter-layer collaboration.

        Expected event shape is intentionally flexible for future adapters.
        For CRM integration, map this payload to external activity objects.
        """
        self.handoff_queue.append(dict(event))
