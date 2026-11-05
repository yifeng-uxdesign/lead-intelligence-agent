"""Approved holding responses for moments that belong to a human.

When the agent must not continue the conversation itself (an open handoff, ALERT
mode), the customer still needs an honest message — silence reads as being
ignored. These strings are the ONLY text the system may send in that state.

Rules (soul.md values 4 and 6):
- Never promise an immediate connection or a response time: the rep may be
  offline, so the copy says a person *will follow up*, not that one is joining.
- Never interpolate rep names, rep notes, CRM fields, scores, or trigger labels.
- Never claim to be human.
- Never ask the prospect another discovery question — that is the agent
  "holding on to a conversation it should have escalated".

Deliberately static: no LLM generation. A future response generator may
rephrase *other* responses but must not touch these (audit Finding 3).
"""

from __future__ import annotations

from typing import Final

from src.domain.trigger_catalog import HandoffTriggerType

# States AI nature up front: the moment someone asks for a person is exactly when
# they most need to know what they have been talking to (soul.md value 6).
_HUMAN_REQUEST: Final[str] = (
    "Of course. I'm an AI assistant, so I've passed your request to our team. "
    "A person will follow up with you, and I've shared our conversation so you "
    "won't need to repeat yourself."
)

_FRUSTRATION: Final[str] = (
    "I hear that this hasn't been going well, and I want it to get the right "
    "attention. I'm asking someone from our team to follow up with you, and "
    "they'll have the context from our conversation."
)

_GENERIC: Final[str] = (
    "I want to make sure this gets the right attention. I'm asking someone from "
    "our team to follow up with you, and they'll have the context from our "
    "conversation."
)

# Used when the customer writes again while a handoff is still open.
_FOLLOW_UP: Final[str] = (
    "Your request is already with our team, and they have the context from our "
    "conversation. A person will follow up with you, so I'll hold off on "
    "anything that should come from them."
)

_BY_TRIGGER: Final[dict[str, str]] = {
    HandoffTriggerType.HUMAN_REQUEST.value: _HUMAN_REQUEST,
    HandoffTriggerType.FRUSTRATION.value: _FRUSTRATION,
}

# Prepended when the prospect also sincerely asked whether they're talking to an
# AI and the holding copy itself doesn't already say so.
AI_DISCLOSURE_PREFIX: Final[str] = "I'm an AI assistant, not a person. "

APPROVED_HOLDING_RESPONSES: Final[frozenset[str]] = frozenset(
    {_HUMAN_REQUEST, _FRUSTRATION, _GENERIC, _FOLLOW_UP}
)


def holding_response(
    trigger_type: str, *, follow_up: bool = False, identity_question: bool = False
) -> str:
    """Return the approved holding copy for a trigger.

    ``follow_up=True`` means a handoff for this customer is already open and
    they have written again; the first-contact copy would be misleading.
    """
    text = _FOLLOW_UP if follow_up else _BY_TRIGGER.get(trigger_type, _GENERIC)
    if identity_question and "AI assistant" not in text:
        return AI_DISCLOSURE_PREFIX + text
    return text
