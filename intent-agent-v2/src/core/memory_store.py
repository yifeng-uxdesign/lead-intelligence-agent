"""In-memory persistence abstraction for lead state."""

from __future__ import annotations

from typing import Dict, Optional

from .lead_context import LeadContext


class MemoryStore:
    """Simple repository for storing and retrieving lead contexts."""

    def __init__(self) -> None:
        self._store: Dict[str, LeadContext] = {}

    def save(self, context: LeadContext) -> None:
        """Persist the current state for a lead."""
        self._store[context.lead_id] = context

    def get(self, lead_id: str) -> Optional[LeadContext]:
        """Return lead context by ID when present."""
        return self._store.get(lead_id)

    def delete(self, lead_id: str) -> None:
        """Remove lead context from store."""
        self._store.pop(lead_id, None)
        # TODO: Emit persistence metrics and audit logging hooks.
