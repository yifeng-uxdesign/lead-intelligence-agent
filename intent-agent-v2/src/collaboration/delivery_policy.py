"""Delivery authorization: what may reach the customer in each collaboration mode.

This is the single, pure, testable policy contract for customer delivery. The
orchestrator asks it what is allowed; it never inspects message text.

| Mode        | Customer receives                  | Agent text goes to        |
|-------------|------------------------------------|---------------------------|
| AUTONOMOUS  | agent response                     | (delivered)               |
| AUTONOMOUS* | approved holding response          | nowhere (not generated)   |
| ALERT       | approved holding response          | nowhere (not generated)   |
| SHADOW      | nothing                            | rep as a suggestion       |
| RELAY       | nothing until a rep approves       | rep as a pending draft    |

* AUTONOMOUS with ``human_hold=True``: the rep is offline (or otherwise not in
  ALERT) but an open handoff still requires a human. Availability is not
  clearance — soul.md value 4.

Unknown modes fail closed to the holding response.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Union

from src.collaboration.mode_state_machine import CollaborationMode


class DeliveryStatus(str, Enum):
    DELIVERED = "delivered"
    HOLDING = "holding"
    PENDING_APPROVAL = "pending_approval"
    REP_SUGGESTION = "rep_suggestion"


@dataclass(frozen=True)
class DeliveryDecision:
    status: DeliveryStatus

    @property
    def generate_agent_text(self) -> bool:
        """Should the behavior engine produce a response this turn at all?"""
        return self.status in (
            DeliveryStatus.DELIVERED,
            DeliveryStatus.PENDING_APPROVAL,
            DeliveryStatus.REP_SUGGESTION,
        )

    @property
    def customer_gets_agent_text(self) -> bool:
        return self.status == DeliveryStatus.DELIVERED

    @property
    def customer_gets_holding_text(self) -> bool:
        return self.status == DeliveryStatus.HOLDING


def authorize_delivery(
    mode: Union[CollaborationMode, str],
    *,
    human_hold: bool,
) -> DeliveryDecision:
    """Decide what the customer may receive this turn.

    Args:
        mode: Collaboration mode computed for this turn.
        human_hold: A handoff that requires a human is open (this turn or an
            earlier unresolved one). Overrides every mode.
    """
    if human_hold:
        return DeliveryDecision(DeliveryStatus.HOLDING)

    try:
        resolved = CollaborationMode(mode)
    except ValueError:
        return DeliveryDecision(DeliveryStatus.HOLDING)

    if resolved == CollaborationMode.AUTONOMOUS:
        return DeliveryDecision(DeliveryStatus.DELIVERED)
    if resolved == CollaborationMode.RELAY:
        return DeliveryDecision(DeliveryStatus.PENDING_APPROVAL)
    if resolved == CollaborationMode.SHADOW:
        return DeliveryDecision(DeliveryStatus.REP_SUGGESTION)
    # ALERT
    return DeliveryDecision(DeliveryStatus.HOLDING)
