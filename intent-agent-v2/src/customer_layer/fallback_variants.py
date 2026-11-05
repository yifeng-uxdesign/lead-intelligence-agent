"""Approved loop-breaker copy for when the agent would repeat itself.

If the scripted response for this turn is identical to the one just sent, the
prospect is not giving the agent what it asked for (or the agent is not asking
the right thing). Repeating a question verbatim is pressure by persistence and
reads as a broken bot. These replies change the approach, hand the choice back
to the prospect (soul.md value 3), and make the human option explicit and
actionable (soul.md behavior guardrails: offer handoff proactively).

Each one:
- offers choices, never an ultimatum; no urgency or scarcity;
- includes the literal invitation "talk to a person", which the extractor
  recognizes, so accepting the offer actually triggers a handoff;
- is distinct from every scripted response and from its neighbors.
"""

from __future__ import annotations

from typing import Final, Tuple

LOOP_BREAKERS: Final[Tuple[str, ...]] = (
    "I want to make sure I'm being useful rather than asking you the same thing "
    "twice. We can go a few ways: tell me about what you're trying to solve, "
    "ask me anything about how this works, or say \"talk to a person\" and I'll "
    "arrange for someone on our team to reach out. Which would you prefer?",
    "Let me try this a different way. If it's easier, share just one thing about "
    "how you handle this today, or ask me whatever is on your mind. And if you'd "
    "rather talk to a person, just say so and I'll set that up.",
    "I may not be getting this right, and that's on me, not you. There's no "
    "pressure to answer anything. You can ask a question, pause here, or say "
    "\"talk to a person\" and I'll bring in someone from our team.",
)


def loop_breaker(repeat_streak: int) -> str:
    """Pick the loop-breaker for the Nth consecutive repeat (1-based).

    Consecutive streak values always map to different strings.
    """
    return LOOP_BREAKERS[(max(repeat_streak, 1) - 1) % len(LOOP_BREAKERS)]
