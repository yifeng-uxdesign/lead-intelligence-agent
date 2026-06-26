"""Draft generation helpers for rep handoff."""

from __future__ import annotations

from typing import Dict


class DraftRelay:
    """Builds draft messages for reps based on lead context."""

    def build_draft(self, lead_snapshot: Dict[str, object], alert_level: str) -> str:
        lead_name = str(lead_snapshot.get("contact_name", "there"))
        topic = str(lead_snapshot.get("top_topic", "your goals"))
        # TODO: Replace with templating engine and personalization slots.
        return (
            f"Hi {lead_name}, I wanted to follow up quickly on {topic}. "
            f"Our current priority level is {alert_level}, and I can share next best steps."
        )
