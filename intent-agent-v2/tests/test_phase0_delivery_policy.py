"""Phase 0: delivery authorization matrix (audit Findings 3 and 4).

The matrix is the contract; if a row here changes, the policy changed.
"""

import pytest

from src.collaboration.delivery_policy import DeliveryStatus, authorize_delivery
from src.collaboration.mode_state_machine import CollaborationMode
from src.customer_layer.holding_responses import (
    APPROVED_HOLDING_RESPONSES,
    holding_response,
)


@pytest.mark.parametrize(
    "mode,human_hold,expected",
    [
        (CollaborationMode.AUTONOMOUS, False, DeliveryStatus.DELIVERED),
        (CollaborationMode.ALERT, False, DeliveryStatus.HOLDING),
        (CollaborationMode.SHADOW, False, DeliveryStatus.REP_SUGGESTION),
        (CollaborationMode.RELAY, False, DeliveryStatus.PENDING_APPROVAL),
        # An open human requirement overrides every mode, including AUTONOMOUS
        # (which is what the mode machine returns when the rep is offline).
        (CollaborationMode.AUTONOMOUS, True, DeliveryStatus.HOLDING),
        (CollaborationMode.SHADOW, True, DeliveryStatus.HOLDING),
        (CollaborationMode.RELAY, True, DeliveryStatus.HOLDING),
        (CollaborationMode.ALERT, True, DeliveryStatus.HOLDING),
    ],
)
def test_delivery_matrix(mode, human_hold, expected) -> None:
    assert authorize_delivery(mode, human_hold=human_hold).status == expected


def test_unknown_mode_fails_closed() -> None:
    assert authorize_delivery("BOGUS", human_hold=False).status == DeliveryStatus.HOLDING


def test_only_delivered_status_releases_agent_text_to_customer() -> None:
    for status in DeliveryStatus:
        from src.collaboration.delivery_policy import DeliveryDecision

        d = DeliveryDecision(status)
        assert d.customer_gets_agent_text == (status == DeliveryStatus.DELIVERED)


# --- Holding copy is honest and static -------------------------------------

@pytest.mark.parametrize("trigger", ["human_request", "frustration", "pricing_discussion", "none"])
@pytest.mark.parametrize("follow_up", [False, True])
def test_holding_responses_are_approved_copy(trigger: str, follow_up: bool) -> None:
    assert holding_response(trigger, follow_up=follow_up) in APPROVED_HOLDING_RESPONSES


def test_holding_copy_never_promises_immediacy_or_asks_questions() -> None:
    """The rep may be offline: promise a follow-up, never an instant connection or a time."""
    banned = ["right now", "immediately", "connecting you", "joining", "in a few minutes",
              "within", "shortly", "momentarily", "i'm a human", "i am a person"]
    for text in APPROVED_HOLDING_RESPONSES:
        low = text.lower()
        assert not any(b in low for b in banned), text
        assert "?" not in text, "holding copy must not ask a discovery question"
        assert "follow up" in low
