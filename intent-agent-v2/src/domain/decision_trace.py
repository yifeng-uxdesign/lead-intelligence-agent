"""Decision trace: why a turn was answered, held, drafted or suggested, and why
the rep was (or was not) notified.

Every customer turn produces exactly one ``DecisionTrace``. It is assembled by
the orchestrator from values it already computed on the way to its decision;
it never feeds back into a decision. Reading a trace answers, without
re-running the turn:

- **outcome** — answered / held / drafted for rep / suggested to rep, and the
  delivery rule that produced it;
- **rep notification** — whether a handoff was queued this turn, and why not
  when it was not (no trigger, already open, ...);
- **evidence** — the interpreted signals and every trigger that fired, with
  the one that drove the decision.

Traces are **rep-internal**: they name trigger labels and signals and must never
be sent on the customer channel (soul.md value 7; see the API leak tests).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

# Outcomes, from the customer's point of view.
OUTCOME_ANSWERED = "answered"          # agent text delivered
OUTCOME_HELD = "held"                  # approved holding copy delivered
OUTCOME_DRAFTED = "drafted_for_rep"    # nothing to customer; RELAY draft staged
OUTCOME_SUGGESTED = "suggested_to_rep" # nothing to customer; SHADOW suggestion

# Intervention bookkeeping for this turn.
INTERVENTION_NONE = "none"
INTERVENTION_OPENED = "opened"
INTERVENTION_ALREADY_OPEN = "already_open"   # same trigger re-fired while open
INTERVENTION_CARRIED_OVER = "carried_over"   # open from an earlier turn, no new trigger


@dataclass(frozen=True)
class TriggerHit:
    """One trigger that fired this turn."""

    trigger_type: str
    trigger_class: str
    evidence: str


@dataclass
class DecisionTrace:
    turn: int
    interpretation_status: str
    signals: Dict[str, Any]
    triggers: List[TriggerHit] = field(default_factory=list)
    primary_trigger: str = "none"
    primary_class: Optional[str] = None
    intervention_action: str = INTERVENTION_NONE
    intervention_trigger: Optional[str] = None
    rep_notified: bool = False
    rep_notified_reason: str = ""
    mode: str = ""
    mode_reason: str = ""
    delivery_status: str = ""
    delivery_reason: str = ""
    response_source: str = ""
    outcome: str = ""
    fit_confirmed: bool = False
    loop_guard_applied: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["explanation"] = self.explain()
        return d

    def explain(self) -> List[str]:
        """Ordered, human-readable account of the turn (for the rep and for tests)."""
        lines = [f"interpretation: {self.interpretation_status}"]
        if self.triggers:
            fired = ", ".join(
                f"{t.trigger_type} [{t.trigger_class}] ({t.evidence})" for t in self.triggers
            )
            lines.append(f"triggers: {fired}; primary={self.primary_trigger}")
        else:
            lines.append("triggers: none fired")
        if self.intervention_action != INTERVENTION_NONE:
            lines.append(f"intervention: {self.intervention_action} ({self.intervention_trigger})")
        lines.append(
            f"rep notified: {'yes' if self.rep_notified else 'no'} — {self.rep_notified_reason}"
        )
        lines.append(f"mode: {self.mode} — {self.mode_reason}")
        lines.append(f"delivery: {self.delivery_status} — {self.delivery_reason}")
        lines.append(f"response: {self.response_source}" + (" (loop guard)" if self.loop_guard_applied else ""))
        lines.append(f"outcome: {self.outcome}")
        return lines


def outcome_for_delivery_status(status: str) -> str:
    return {
        "delivered": OUTCOME_ANSWERED,
        "holding": OUTCOME_HELD,
        "pending_approval": OUTCOME_DRAFTED,
        "rep_suggestion": OUTCOME_SUGGESTED,
    }.get(status, OUTCOME_HELD)
