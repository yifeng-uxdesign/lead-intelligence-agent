"""Signal-to-alert conversion for rep notifications."""

from __future__ import annotations

from typing import Dict


class AlertManager:
    """Evaluates lead snapshots and emits alert levels for reps."""

    def evaluate(self, lead_snapshot: Dict[str, object]) -> str:
        risk_score = float(lead_snapshot.get("risk_score", 0.0))
        intent_score = float(lead_snapshot.get("intent_score", 0.0))

        if risk_score >= 0.8:
            return "critical"
        if intent_score >= 0.7:
            return "high"
        if intent_score >= 0.4:
            return "medium"
        # TODO: Include inactivity windows and SLA breach checks.
        return "low"
