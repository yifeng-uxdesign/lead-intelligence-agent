"""Response policy logic for customer communications."""

from __future__ import annotations

from typing import Dict


class ResponsePolicy:
    """Maps trust and intent signals to customer-facing response styles."""

    def choose_style(self, trust_state: str, signals: Dict[str, object]) -> str:
        urgency = str(signals.get("urgency", "medium"))
        if trust_state == "low_trust":
            return "clarify_and_reassure"
        if urgency == "high":
            return "concise_actionable"
        if trust_state == "high_trust":
            return "direct_recommendation"
        # TODO: Support channel-specific styles (email, chat, call notes).
        return "consultative"
