"""Customer-facing response engine: warm, consultative, patient, never pushy.

**Value constitution:** ``src/core/soul.md`` is the source of truth for behavioral
constraints and conflict hierarchy; align copy, tone, and escalation with it
before changing this module.

**Fit confirmation policy (soul.md — value 3 & conflict hierarchy priority 2):**
Before bridging a prospect to a human rep at ``DECISION_READY``, the agent must
confirm that the product is genuinely a good fit for their situation. Skipping
this check means a prospect could be handed off — and potentially committed — to
a solution that doesn't serve them.

soul.md value 3 "preserve dignity and agency": the customer is never a target,
they are a person making a decision. soul.md conflict hierarchy priority 2: "do
not harm the prospect's interest." Both values require fit to be validated before
the handoff template is rendered.

The ``fit_confirmed`` flag in ``signals`` is the enforcement point. It must be
set upstream (by the orchestrator or qualification layer) before ``DECISION_READY``
is reached. If it is absent or False, ``_decision_ready_bridge`` returns a gentle
fit-check response instead of the handoff template.
"""

from __future__ import annotations

from typing import Any, Dict, Union

from src.core.lead_context import LeadContext
from src.customer_layer.trust_state_machine import TrustState

# Customer-visible copy only. Never interpolate internal rep notes, CRM payloads,
# or handoff_queue contents into these strings.

_HANDOFF_BRIDGE_TEMPLATE = (
    "Let me connect you with {rep_name}, and I'll make sure they already have "
    "everything from our conversation so you won't need to repeat anything."
)

# Rendered when DECISION_READY is reached but fit has not yet been confirmed.
# soul.md value 3 "preserve dignity and agency" + conflict hierarchy priority 2.
# Tone: curious and open — not a blocker, not a pitch. Invites honest reflection
# so the prospect moves forward on their own terms, not on pipeline momentum.
_FIT_CHECK_RESPONSE = (
    "Before we take the next step, I want to make sure this is actually the right fit "
    "for you — not just a good conversation. Based on what you've shared, does this feel "
    "like it genuinely addresses what you're trying to solve? If there are parts that "
    "still feel uncertain, I'd rather we work through those now than have you find out later."
)


def _normalize_trust_state(raw: Union[TrustState, str, None]) -> TrustState:
    if isinstance(raw, TrustState):
        return raw
    if raw is None:
        return TrustState.AWARENESS
    s = str(raw).strip().upper()
    try:
        return TrustState(s)
    except ValueError:
        try:
            return TrustState[s]
        except KeyError:
            return TrustState.AWARENESS


def _safe_rep_name(context: LeadContext) -> str | None:
    """Return only a display-safe rep label from assigned_rep — never internal notes."""
    name = context.assigned_rep
    if not name or not str(name).strip():
        return None
    return str(name).strip()


class CustomerBehaviorEngine:
    """Generates customer-facing replies aligned with trust psychology.

    Tone is intentionally warm and consultative: invite dialogue, reduce
    pressure, and offer clarity without urgency tactics.
    """

    def generate_response(self, context: LeadContext, signals: Dict[str, Any]) -> str:
        """Produce the next customer-visible message from shared context and signals.

        ``signals`` should include:
        - ``trust_state`` (``TrustState`` or string) — required.
        - ``topic`` (str) — optional, for softer personalization.
        - ``identity_question`` (bool) — when True, answer directly that this is
          an AI assistant (soul.md value 6). Takes precedence over trust-state copy.
        - ``fit_confirmed`` (bool) — required when ``trust_state`` is
          ``DECISION_READY``. If absent or False, a fit-check response is
          returned instead of the handoff template. See soul.md value 3 and
          conflict hierarchy priority 2.

        Never returns internal CRM or rep-only fields.
        """
        state = _normalize_trust_state(signals.get("trust_state"))
        topic = str(signals.get("topic", "")).strip()

        if bool(signals.get("identity_question", False)):
            return self._identity_disclosure_response()

        if state == TrustState.CURIOSITY:
            return self._curiosity_response(topic)
        if state == TrustState.HESITATION:
            return self._hesitation_response(topic)
        if state == TrustState.OBJECTION:
            return self._objection_response(topic)
        if state == TrustState.DECISION_READY:
            # Extract fit_confirmed from signals; default to False so that any
            # caller that forgets to set it is safe-by-default — the fit check
            # runs rather than the handoff template rendering prematurely.
            fit_confirmed: bool = bool(signals.get("fit_confirmed", False))
            return self._decision_ready_bridge(context, fit_confirmed=fit_confirmed)

        return self._default_consultative(state, topic)

    def _curiosity_response(self, topic: str) -> str:
        # Discovery: open questions, no pitch — respect pace.
        if topic:
            return (
                f"I'd love to understand what matters most to you about {topic}. "
                "What would success look like for you in the next few months, "
                "and what's one thing you'd want to get clearer on first?"
            )
        return (
            "To point you in the right direction, could you share what you're hoping "
            "to learn or solve right now? There's no rush — take it in whatever order feels natural."
        )

    def _hesitation_response(self, topic: str) -> str:
        # Reduce uncertainty without pushing; normalize taking time.
        base = (
            "It's completely fine to move at your own pace. "
            "If it helps, we can break this into small steps so nothing feels overwhelming."
        )
        if topic:
            return (
                f"On {topic}, many people want a bit more clarity before the next step. "
                "What part still feels fuzzy — timing, fit, or something else? "
                + base
            )
        return base + " What would make you feel more confident about your next move?"

    def _objection_response(self, topic: str) -> str:
        # Empathetic reassurance — validate before problem-solving.
        lead = (
            "Thanks for saying that — it makes sense to raise it. "
            "I'm here to help you work through it, not to talk you into anything."
        )
        if topic:
            return (
                f"{lead} On {topic}, would it help if we walked through what you're worried about "
                "and what would need to be true for this to feel workable?"
            )
        return (
            f"{lead} Would you like to share what's on your mind, and we can look at it together?"
        )

    def _identity_disclosure_response(self) -> str:
        """Direct disclosure when the prospect asks whether this is a human or bot.

        soul.md value 6: never obscure AI nature or imply human identity.
        """
        return (
            "I'm an AI assistant — I'm not a human. I can still help you explore "
            "questions at your own pace, and if you'd like to speak with someone on "
            "our team, I can help connect you."
        )

    def _decision_ready_bridge(
        self, context: LeadContext, fit_confirmed: bool = False
    ) -> str:
        """Return the handoff template if fit is confirmed; otherwise a fit-check response.

        **soul.md — value 3 "preserve dignity and agency" + conflict hierarchy priority 2:**
        A prospect reaching ``DECISION_READY`` through natural conversation momentum
        does not guarantee the product is genuinely right for them. Bridging directly
        to a rep without confirming fit risks moving someone toward a commitment that
        doesn't serve their interest. This violates both the dignity value (the customer
        is a person making a decision, not a target) and priority 2 of the conflict
        hierarchy (do not harm the prospect's interest).

        ``fit_confirmed=True`` must be set explicitly by the orchestrator or
        qualification layer — it is never inferred from trust state alone. Defaulting
        to False means the safe path (fit check) runs whenever the caller is uncertain.

        Args:
            context: Shared lead state. Used only for display-safe rep name.
            fit_confirmed: Whether the qualification layer has verified product
                fit for this prospect. Must be set upstream; never assumed.
        """
        if not fit_confirmed:
            # Fit has not been confirmed upstream. Return a gentle, open question
            # that surfaces alignment before any handoff template is shown.
            # soul.md value 3 + conflict hierarchy priority 2.
            return _FIT_CHECK_RESPONSE

        # Fit is confirmed — safe to bridge to the human rep.
        # Warm handoff: only use assigned_rep for the name line — no internal notes.
        rep = _safe_rep_name(context)
        if rep:
            return _HANDOFF_BRIDGE_TEMPLATE.format(rep_name=rep)
        return (
            "Whenever you're ready, I can connect you with someone on our team who can "
            "take you through the next steps. I'll make sure they have the context from "
            "our conversation so you won't need to repeat everything."
        )

    def _default_consultative(self, state: TrustState, topic: str) -> str:
        """Fallbacks for states without a dedicated scripted branch — still non-pushy."""
        if state == TrustState.AWARENESS:
            return (
                "Hi — I'm glad you're here. If you'd like, tell me a little about what "
                "brought you in today, and we can explore options together with no pressure."
            )
        if state == TrustState.EVALUATION:
            t = f" As you think about {topic}," if topic else ""
            return (
                "Take your time comparing options — that's a healthy part of the process."
                + t
                + " What criteria matter most to you when you're deciding?"
            )
        if state == TrustState.TRUST_BUILDING:
            return (
                "I appreciate the openness. I'm happy to go deeper on anything that's useful "
                "— what would be most helpful for you to cover next?"
            )
        if state == TrustState.COMMITMENT:
            return (
                "Thank you for moving forward with us. If anything comes up before the next step, "
                "just say the word and we'll sort it out together."
            )
        return (
            "I'm here to help in whatever way is most useful. What would you like to focus on next?"
        )