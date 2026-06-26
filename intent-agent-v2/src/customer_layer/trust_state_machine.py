"""Trust state machine grounded in sales psychology.

This module models how a lead's mindset evolves from early exploration to
purchase commitment. Transitions are intentionally interpretable so teams can
audit why the agent changed communication strategy.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict


class TrustState(str, Enum):
    """Psychological trust states used by the customer behavior layer."""

    AWARENESS = "AWARENESS"
    CURIOSITY = "CURIOSITY"
    EVALUATION = "EVALUATION"
    HESITATION = "HESITATION"
    OBJECTION = "OBJECTION"
    TRUST_BUILDING = "TRUST_BUILDING"
    DECISION_READY = "DECISION_READY"
    COMMITMENT = "COMMITMENT"


class TrustStateMachine:
    """Tracks and transitions customer trust through the sales lifecycle."""

    def __init__(self) -> None:
        self.current_state: TrustState = TrustState.AWARENESS

    def get_state(self) -> TrustState:
        """Return the current psychological state."""
        return self.current_state

    def transition(self, signals: Dict[str, object]) -> TrustState:
        """Advance trust state from observed conversation signals.

        Expected signal keys (all optional):
        - ``intent``: high-level intent label (for example ``"explore"``).
        - ``objection``: whether customer expressed a concrete objection.
        - ``urgency``: urgency label (``"low"``, ``"medium"``, ``"high"``).
        - ``trust_score``: numeric confidence signal in [0, 1].
        - ``strong_buying_signal``: explicit buying momentum flag.
        - ``resolve``: prospect signals that hesitation or objection has cleared.
        """
        intent = str(signals.get("intent", "")).strip().lower()
        objection = bool(signals.get("objection", False))
        urgency = str(signals.get("urgency", "")).strip().lower()
        trust_score = float(signals.get("trust_score", 0.0))
        strong_buying_signal = bool(signals.get("strong_buying_signal", False))
        resolve = bool(signals.get("resolve", False))

        # Final stage: commitment unless the prospect signals pullback.
        if self.current_state == TrustState.DECISION_READY:
            if objection or urgency == "low":
                return self.current_state
            self.current_state = TrustState.COMMITMENT
            return self.current_state

        # Regression: resolved objection or hesitation — read where they are now.
        if self.current_state == TrustState.OBJECTION and resolve:
            self.current_state = TrustState.EVALUATION
            return self.current_state

        if self.current_state == TrustState.HESITATION and resolve:
            self.current_state = TrustState.CURIOSITY
            return self.current_state

        # Awareness -> Curiosity:
        # Early attention turns into discovery when the lead starts exploring.
        if self.current_state == TrustState.AWARENESS and intent == "explore":
            self.current_state = TrustState.CURIOSITY
            return self.current_state

        # Curiosity -> Objection (evaluated before hesitation):
        # If both objection and low urgency apply, objection wins—surface the
        # blocker first; hesitation handling can follow on a later turn.
        if self.current_state == TrustState.CURIOSITY and objection:
            self.current_state = TrustState.OBJECTION
            return self.current_state

        # Curiosity -> Hesitation:
        # Low urgency often means interest exists, but action confidence is low.
        if self.current_state == TrustState.CURIOSITY and urgency == "low":
            self.current_state = TrustState.HESITATION
            return self.current_state

        # Evaluation -> Trust Building:
        # During comparison/evaluation, strong trust unlocks deeper guidance.
        if self.current_state == TrustState.EVALUATION and trust_score >= 0.75:
            self.current_state = TrustState.TRUST_BUILDING
            return self.current_state

        # Trust Building -> Decision Ready:
        # Clear buying signals indicate readiness for commitment discussions.
        if self.current_state == TrustState.TRUST_BUILDING and strong_buying_signal:
            self.current_state = TrustState.DECISION_READY
            return self.current_state

        return self.current_state
