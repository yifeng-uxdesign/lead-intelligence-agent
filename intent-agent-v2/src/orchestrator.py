"""Top-level orchestration: customer path, rep path, and mode transitions.

Domain rules (SLA, triggers) live in ``domain.trigger_catalog``.
Signal shaping lives in ``application.signal_adapters``.
Persisted session keys live in ``domain.session_state``.

**Fit evaluation (soul.md — conflict hierarchy priority 2):**
``run_customer_response_path`` calls ``fit_summary()`` before invoking
``CustomerBehaviorEngine.generate_response()``. This ensures ``fit_confirmed``
is always sourced from structured fit evaluation — never assumed from trust
state or buying signal alone. The evaluation result gates the
``_decision_ready_bridge`` in the behavior engine, enforcing soul.md priority 2
("do not harm the prospect's interest") at the orchestration layer.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from src.application.signal_adapters import (
    handoff_signal_dict_from_lead,
    lead_signals_to_trust_signals,
)
from src.clients.sierra.fit_criteria import FitCriteria, fit_summary
from src.collaboration.handoff_manager import HandoffManager
from src.collaboration.mode_state_machine import CollaborationMode, ModeStateMachine
from src.core.handoff_queue import HandoffQueue
from src.core.lead_context import LeadContext
from src.collaboration.delivery_policy import DeliveryStatus, authorize_delivery
from src.core.memory_store import MemoryStore
from src.customer_layer.behavior_engine import CustomerBehaviorEngine
from src.customer_layer.fallback_variants import loop_breaker
from src.customer_layer.holding_responses import holding_copy_id, holding_response
from src.customer_layer.trust_state_machine import TrustState, TrustStateMachine
from src.domain.decision_trace import (
    INTERVENTION_ALREADY_OPEN,
    INTERVENTION_CARRIED_OVER,
    INTERVENTION_NONE,
    INTERVENTION_OPENED,
    DecisionTrace,
    TriggerHit,
    outcome_for_delivery_status,
)
from src.domain.session_state import (
    KEY_COLLABORATION_MODE,
    KEY_LAST_BASE_RESPONSE,
    KEY_REPEAT_STREAK,
    append_decision_trace,
    discard_relay_drafts,
    first_open_human_trigger,
    has_open_human_intervention,
    hydrate_mode_machine,
    hydrate_trust_machine,
    next_turn_number,
    open_intervention,
    persist_collaboration_mode,
    persist_last_trigger,
    persist_trust_state,
    record_rep_notice,
    stage_relay_draft,
)
from src.domain.trigger_catalog import HandoffTriggerType, TriggerClass, rep_brief_key_for_handoff
from src.rep_layer.rep_assist_engine import AlertBrief, RepAssistEngine
from src.signals.extractor import LeadSignalExtractor, LeadSignals


# ---------------------------------------------------------------------------
# Prospect signal mapping
# Converts LeadSignals into the key dict expected by fit_criteria.evaluate_fit.
# Only maps signals that have a corresponding FitSignal.key in fit_criteria.py.
# This is deliberately conservative — unmapped signals return False (safe).
# ---------------------------------------------------------------------------

def _prospect_signals_from_lead(lead: LeadSignals) -> Dict[str, bool]:
    """Map ``LeadSignals`` to the prospect_signals dict used by ``fit_summary``.

    Keys must match ``FitSignal.key`` and ``HardDisqualifier.key`` values
    defined in ``src/clients/sierra/fit_criteria.py``. Add mappings here
    as the extractor gains richer signal detection.

    Current mappings are intentionally conservative — a signal is only set
    True when there is a concrete, unambiguous indicator from the extracted
    fields. Ambiguous signals default to False (safe-by-default for fit_confirmed).
    """
    return {
        # Good fit signals — map from extractor fields
        "high_support_volume": False,           # not yet extractable from text alone
        "repetitive_ticket_types": False,       # requires discovery question answer
        "existing_helpdesk_or_crm": lead.competitor_mention,
        # competitor_mention often surfaces tool names (Zendesk, Salesforce, etc.)
        "wants_autonomous_resolution": lead.buying_signal,
        # buying signal implies they want the product to resolve, not just advise
        "scale_pressure": lead.sentiment in ("negative", "frustration")
                          and lead.urgency == "high",
        "consumer_facing": False,               # not extractable from single message
        "support_team_size_adequate": False,    # requires discovery answer
        "pilot_mindset": lead.intent == "evaluate",
        "budget_signal": lead.objection_type != "price" and lead.buying_signal,

        # Poor fit signals — map from extractor fields
        "very_low_volume": False,               # not extractable from single message
        "purely_complex_cases": False,          # not extractable from single message
        "no_existing_systems": False,           # not extractable from single message
        "enterprise_b2b_only": False,           # not extractable from single message
        "resistant_to_ai_autonomy": lead.objection_type == "capability",
        "budget_concern": lead.objection_type == "price",

        # Hard disqualifiers — map from extractor fields
        "no_api_access": False,                 # not extractable from single message
        "no_knowledge_base": False,             # not extractable from single message
        "crisis_or_sensitive_only": False,      # not extractable from single message
        "regulatory_prohibition": False,        # not extractable from single message
    }


# ---------------------------------------------------------------------------
# Interpretation safety + loop guard
# ---------------------------------------------------------------------------

_log = logging.getLogger(__name__)

# What "we learned nothing" looks like. Used for empty input and total
# interpretation failure; never inferred from a message that actually parsed.
_NO_INFORMATION = LeadSignals(
    intent="general",
    urgency="medium",
    sentiment="neutral",
    objection_type="none",
    human_request=False,
    competitor_mention=False,
    buying_signal=False,
    stakeholder_signal=False,
)

# Trust states whose reply is functionally specific (fit check, thank-you) and
# must not be swapped for generic loop-breaker copy.
_LOOP_GUARD_EXEMPT_STATES = frozenset({TrustState.DECISION_READY, TrustState.COMMITMENT})


def interpret_message(
    extractor: LeadSignalExtractor, raw_message: str
) -> Tuple[LeadSignals, str]:
    """Extract signals without ever letting interpretation failure break a turn.

    Returns ``(signals, status)`` where status is:
    - ``"ok"``       — the configured extractor succeeded.
    - ``"fallback"`` — it raised; the deterministic rule-based extractor was used.
    - ``"empty"``    — blank input; nothing to interpret.
    - ``"failed"``   — everything failed; signals carry no information.

    ``"empty"`` and ``"failed"`` mean *no information*: callers must not advance
    or regress trust on them.
    """
    if not raw_message or not str(raw_message).strip():
        return _NO_INFORMATION, "empty"
    try:
        return extractor.extract(raw_message), "ok"
    except Exception:  # noqa: BLE001 — an interpreter must never take the turn down
        _log.exception("signal extractor failed; falling back to rule-based extraction")
    try:
        return LeadSignalExtractor().extract(raw_message), "fallback"
    except Exception:  # noqa: BLE001
        _log.exception("fallback extractor failed; treating turn as no-information")
        return _NO_INFORMATION, "failed"


def guard_against_repetition(
    metadata: Dict, base_text: str, *, exempt: bool = False
) -> str:
    """Never send the same scripted reply twice in a row.

    Compares the *scripted* text (before substitution) with the previous turn's
    scripted text, so a loop-breaker can't itself become half of an A/B/A loop.
    """
    if exempt:
        metadata[KEY_REPEAT_STREAK] = 0
        metadata[KEY_LAST_BASE_RESPONSE] = base_text
        return base_text
    streak = (
        int(metadata.get(KEY_REPEAT_STREAK, 0)) + 1
        if metadata.get(KEY_LAST_BASE_RESPONSE) == base_text
        else 0
    )
    metadata[KEY_REPEAT_STREAK] = streak
    metadata[KEY_LAST_BASE_RESPONSE] = base_text
    return loop_breaker(streak) if streak > 0 else base_text


# ---------------------------------------------------------------------------
# Orchestration path functions
# ---------------------------------------------------------------------------

def run_mode_transition_path(
    mode_machine: ModeStateMachine,
    *,
    rep_online: bool,
    live_session: bool,
    handoff_triggered: bool,
    awaiting_approval: bool,
    context: Optional[LeadContext] = None,
) -> CollaborationMode:
    """Compute next collaboration mode (autonomous vs rep-assisted variants).

    Passing ``context`` lets the machine record an interruption event when the
    rep drops offline mid-ALERT/RELAY/SHADOW (soul.md value 4).
    """
    return mode_machine.transition(
        rep_online=rep_online,
        live_session=live_session,
        handoff_triggered=handoff_triggered,
        awaiting_approval=awaiting_approval,
        context=context,
    )


def run_customer_trust_path(
    context: LeadContext,
    trust_machine: TrustStateMachine,
    lead_signals: LeadSignals,
) -> TrustState:
    """Update psychological trust from this turn's signals; persist on context."""
    trust_signals = lead_signals_to_trust_signals(lead_signals)
    new_state = trust_machine.transition(trust_signals)
    persist_trust_state(context.metadata, new_state)
    context.customer_state = new_state.value
    return new_state


# Customer-safe phrasing of a context / attention trigger, used as the reply
# topic when the prospect raised no objection: the agent continues *and*
# acknowledges what was raised, instead of repeating its previous template.
# Never interpolate trigger labels themselves into customer text.
_NOTICE_TOPIC: Dict[str, str] = {
    HandoffTriggerType.COMPETITOR_MENTION.value: "how this compares with what you use today",
    HandoffTriggerType.STAKEHOLDER_APPROVAL_NEEDED.value: "getting the right people involved",
    HandoffTriggerType.PRICING_DISCUSSION.value: "pricing",
    HandoffTriggerType.STRONG_BUYING_SIGNAL.value: "the next steps",
}


def run_customer_response_path(
    engine: CustomerBehaviorEngine,
    context: LeadContext,
    trust_state: TrustState,
    lead_signals: LeadSignals,
    fit_criteria: Optional[FitCriteria] = None,
    notice_trigger: Optional[str] = None,
) -> str:
    """Generate the next customer-visible message (warm, non-pushy).

    **Fit evaluation (soul.md — conflict hierarchy priority 2):**
    Before generating a response, this function evaluates product fit using
    ``fit_summary()``. The result sets ``fit_confirmed`` in the signal dict
    passed to ``generate_response()``.

    If ``fit_criteria`` is None, fit evaluation is skipped and
    ``fit_confirmed`` defaults to False — the safe path. This maintains
    backward compatibility with tests that don't supply a client criteria
    object and correctly gates the handoff bridge.

    ``fit_confirmed`` is sourced from structured evaluation only — it is
    never inferred from trust state, buying signal, or urgency alone.
    soul.md priority 2: the qualification layer owns this decision.
    """
    topic = ""
    if lead_signals.objection_type != "none":
        topic = lead_signals.objection_type.replace("_", " ")
    elif notice_trigger:
        topic = _NOTICE_TOPIC.get(notice_trigger, "")

    # Evaluate product fit against client criteria.
    # soul.md conflict hierarchy priority 2: do not harm the prospect's interest.
    # fit_confirmed=False is the safe default — the fit-check response runs
    # unless the evaluation explicitly clears the threshold.
    fit_confirmed: bool = False
    fit_assessment: Optional[Dict] = None

    if fit_criteria is not None:
        prospect_signals = _prospect_signals_from_lead(lead_signals)
        fit_assessment = fit_summary(prospect_signals, fit_criteria)
        fit_confirmed = fit_assessment["fit_confirmed"]

        # Surface mismatch signal is available for future orchestrator use —
        # e.g. logging, rep notification, or proactive fit-check injection
        # before DECISION_READY is reached. Not yet wired to a specific action.
        if fit_assessment.get("should_surface_mismatch"):
            context.metadata["fit_mismatch_detected"] = True

    if fit_confirmed:
        context.metadata.pop("fit_mismatch_detected", None)

    return engine.generate_response(
        context,
        {
            "trust_state": trust_state,
            "topic": topic,
            "fit_confirmed": fit_confirmed,
            "identity_question": lead_signals.identity_question,
        },
    )


def run_rep_alert_path(
    rep_engine: RepAssistEngine,
    handoff_manager: HandoffManager,
    context: LeadContext,
    trigger_type: str,
    rep_online: Optional[bool] = None,
    trigger_class: Optional[str] = None,
    also: Optional[List[str]] = None,
) -> AlertBrief:
    """Build internal rep alert brief and enqueue handoff for rep layer pickup.

    Called for every newly-fired trigger of any class, regardless of
    collaboration mode or rep availability: a human requirement must never
    depend on the rep being online.
    """
    brief_trigger = rep_brief_key_for_handoff(trigger_type)
    brief = rep_engine.create_alert_brief(context, brief_trigger)
    handoff_manager.request_rep_handoff(
        context.lead_id,
        {
            "trigger_type": trigger_type,
            "alert_brief": brief.as_dict(),
            "sla_minutes": handoff_manager.get_sla(trigger_type),
            "rep_online_at_trigger": rep_online,
            "trigger_class": trigger_class,
            "also_triggered": list(also or []),
        },
    )
    return brief


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class OrchestrationResult:
    """One turn outcome: what the customer sees and what ops/rep receive."""

    context: LeadContext
    lead_signals: LeadSignals
    trust_state: TrustState
    handoff_triggered: bool
    trigger_type: str
    collaboration_mode: CollaborationMode
    customer_message: Optional[str]
    rep_alert_brief: Optional[AlertBrief]
    fit_confirmed: bool = False
    fit_score: Optional[int] = None
    # --- delivery contract (see collaboration.delivery_policy) --------------
    # ``customer_message`` is ONLY text that is safe to show the customer now:
    # an agent response (AUTONOMOUS) or an approved holding response. Rep-only
    # output lives in ``pending_draft`` / ``rep_suggestion`` and must never be
    # forwarded to the customer channel.
    delivery_status: str = DeliveryStatus.DELIVERED.value
    handoff_queued: bool = False
    human_intervention_open: bool = False
    pending_draft: Optional[str] = None
    pending_draft_id: Optional[str] = None
    rep_suggestion: Optional[str] = None
    interpretation_status: str = "ok"
    # Why this turn ended the way it did (rep-internal; never send to customer).
    decision_trace: Optional[DecisionTrace] = None


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_turn(
    *,
    lead_id: str,
    raw_message: str,
    store: MemoryStore,
    signal_extractor: LeadSignalExtractor,
    customer_engine: CustomerBehaviorEngine,
    rep_engine: RepAssistEngine,
    handoff_manager: HandoffManager,
    mode_machine: ModeStateMachine,
    rep_online: bool,
    live_session: bool = False,
    awaiting_approval: bool = False,
    fit_criteria: Optional[FitCriteria] = None,
) -> OrchestrationResult:
    """Execute the full workflow for one inbound customer message.

    Args:
        lead_id: Unique identifier for this lead/conversation.
        raw_message: Raw text from the customer this turn.
        store: Persistent memory store for LeadContext across turns.
        signal_extractor: Extracts structured signals from raw text.
        customer_engine: Generates customer-facing responses.
        rep_engine: Generates rep-facing alert briefs.
        handoff_manager: Evaluates handoff trigger conditions.
        mode_machine: Manages collaboration mode transitions.
        rep_online: Whether the assigned rep is currently available.
        live_session: Whether rep is actively in a live session.
        awaiting_approval: Whether a draft is pending rep approval.
        fit_criteria: Optional client-specific fit criteria for product
            fit evaluation. If None, fit_confirmed defaults to False.
            Pass ``SIERRA_FIT_CRITERIA`` from fit_criteria.py for live use.
    """

    # 1) Load or create lead context from memory store.
    #    Reset the (possibly shared) machine first so one lead's mode can never
    #    bleed into another's; hydrate then restores this lead's persisted mode.
    ctx = store.get(lead_id)
    if ctx is None:
        ctx = LeadContext(lead_id=lead_id)
    mode_machine.current_mode = CollaborationMode.AUTONOMOUS
    hydrate_mode_machine(
        mode_machine, ctx.metadata.get(KEY_COLLABORATION_MODE)
    )
    turn_number = next_turn_number(ctx.metadata)

    # 2) Extract structured signals. Failure degrades (fallback extractor, then
    #    "no information") instead of crashing the turn.
    lead_signals, interpretation_status = interpret_message(signal_extractor, raw_message)
    no_information = interpretation_status in ("empty", "failed")
    if not no_information:
        ctx.update_sentiment(lead_signals.sentiment)
    if raw_message and str(raw_message).strip():
        ctx.update_summary(f"User: {raw_message.strip()[:2000]}")

    trust_machine = hydrate_trust_machine(ctx.metadata)

    # 3) Update customer psychological trust state. A turn that taught us
    #    nothing must not move trust in either direction.
    if no_information:
        trust_state = trust_machine.get_state()
        persist_trust_state(ctx.metadata, trust_state)
        ctx.customer_state = trust_state.value
    else:
        trust_state = run_customer_trust_path(ctx, trust_machine, lead_signals)

    # 4) Evaluate triggers (deterministic; the extractor only supplies evidence).
    #    Every trigger has a class (domain.trigger_catalog.TriggerClass):
    #    context / attention notify the rep and let the agent continue;
    #    intervention opens a human moment and holds the conversation.
    handoff_payload = handoff_signal_dict_from_lead(lead_signals, raw_message)
    hits = handoff_manager.evaluate(handoff_payload, ctx)
    handoff_triggered = bool(hits)
    trigger_type = hits[0].trigger_type if hits else HandoffTriggerType.NONE.value
    intervention_hits = [h for h in hits if h.trigger_class == TriggerClass.INTERVENTION.value]
    notice_hits = [h for h in hits if h.trigger_class != TriggerClass.INTERVENTION.value]
    intervention_trigger = intervention_hits[0].trigger_type if intervention_hits else None

    # A human requirement is state, not a one-turn event: an unresolved
    # intervention from an earlier turn still holds the conversation.
    earlier_human_trigger = first_open_human_trigger(ctx.metadata)
    human_hold = intervention_trigger is not None or earlier_human_trigger is not None

    # 5) Transition collaboration mode. Only an intervention puts an online rep
    #    in ALERT; context / attention never take the conversation away.
    collaboration_mode = run_mode_transition_path(
        mode_machine,
        rep_online=rep_online,
        live_session=live_session,
        handoff_triggered=human_hold,
        awaiting_approval=awaiting_approval,
        context=ctx,
    )
    ctx.collaboration_mode = collaboration_mode.value
    persist_collaboration_mode(ctx.metadata, collaboration_mode)
    ctx.rep_online = rep_online

    customer_message: Optional[str] = None
    rep_brief: Optional[AlertBrief] = None
    fit_confirmed: bool = False
    fit_score: Optional[int] = None
    handoff_queued = False
    pending_draft: Optional[str] = None
    pending_draft_id: Optional[str] = None
    rep_suggestion: Optional[str] = None

    # 6) Notify the rep whenever something new fired — online, offline, any
    #    mode. Interventions open (once per trigger until resolved); context /
    #    attention are recorded once per lead. One queue task per turn, keyed
    #    on the highest-precedence newly-notified trigger.
    if handoff_triggered:
        persist_last_trigger(ctx.metadata, trigger_type)
    newly_opened = False
    notified: list = []
    for h in intervention_hits:
        if open_intervention(ctx.metadata, h.trigger_type, human_required=True, turn=turn_number):
            newly_opened = newly_opened or h.trigger_type == intervention_trigger
            notified.append(h)
    if intervention_hits:
        # Anything staged for approval was written before the human moment.
        discard_relay_drafts(ctx.metadata)
    for h in notice_hits:
        if record_rep_notice(
            ctx.metadata, h.trigger_type, trigger_class=h.trigger_class, turn=turn_number
        ):
            notified.append(h)
    if notified:
        lead_hit = notified[0]
        rep_brief = run_rep_alert_path(
            rep_engine,
            handoff_manager,
            ctx,
            lead_hit.trigger_type,
            rep_online=rep_online,
            trigger_class=lead_hit.trigger_class,
            also=[h.trigger_type for h in notified[1:]],
        )
        ctx.add_handoff_event(
            {
                "trigger_type": lead_hit.trigger_type,
                "trigger_class": lead_hit.trigger_class,
                "reason": "handoff_triggered",
                "rep_online": rep_online,
                "turn": turn_number,
            }
        )
        handoff_queued = True

    # 7) Authorize delivery, then produce only what the policy allows.
    decision = authorize_delivery(collaboration_mode, human_hold=human_hold)
    loop_guard_applied = False

    if decision.customer_gets_holding_text:
        # soul.md value 4: this moment belongs to a human. Approved static copy
        # only — never unrestricted generation, never silence.
        holding_trigger = intervention_trigger or earlier_human_trigger or trigger_type
        customer_message = holding_response(
            holding_trigger,
            follow_up=not newly_opened,
            identity_question=lead_signals.identity_question,
        )
        response_source = "holding:" + holding_copy_id(holding_trigger, follow_up=not newly_opened)
    else:
        base_text = run_customer_response_path(
            customer_engine,
            ctx,
            trust_state,
            lead_signals,
            fit_criteria=fit_criteria,
            notice_trigger=notice_hits[0].trigger_type if notice_hits else None,
        )
        agent_text = guard_against_repetition(
            ctx.metadata,
            base_text,
            exempt=(
                lead_signals.identity_question
                or trust_state in _LOOP_GUARD_EXEMPT_STATES
            ),
        )
        loop_guard_applied = agent_text != base_text

        # Expose fit assessment in result for logging and test assertions
        if fit_criteria is not None:
            prospect_signals = _prospect_signals_from_lead(lead_signals)
            assessment = fit_summary(prospect_signals, fit_criteria)
            fit_confirmed = assessment["fit_confirmed"]
            fit_score = assessment["score"]

        if decision.customer_gets_agent_text:
            customer_message = agent_text
            response_source = "agent"
        elif decision.status == DeliveryStatus.PENDING_APPROVAL:
            # RELAY: the draft goes to the rep, never to the customer.
            pending_draft = agent_text
            pending_draft_id = stage_relay_draft(
                ctx.metadata, agent_text, turn=turn_number
            )
            response_source = "rep_draft"
        else:
            # SHADOW: suggestion for the rep, who owns the conversation.
            rep_suggestion = agent_text
            response_source = "rep_suggestion"

    # 8) Record why, then persist.
    trace = _build_trace(
        turn=turn_number,
        interpretation_status=interpretation_status,
        lead_signals=lead_signals,
        hits=hits,
        intervention_trigger=intervention_trigger,
        newly_opened=newly_opened,
        earlier_human_trigger=earlier_human_trigger,
        notified=notified,
        mode=collaboration_mode,
        mode_reason=mode_machine.last_reason,
        decision=decision,
        response_source=response_source,
        fit_confirmed=fit_confirmed,
        loop_guard_applied=loop_guard_applied,
    )
    append_decision_trace(ctx.metadata, trace.to_dict())
    store.save(ctx)

    return OrchestrationResult(
        context=ctx,
        lead_signals=lead_signals,
        trust_state=trust_state,
        handoff_triggered=handoff_triggered,
        trigger_type=trigger_type,
        collaboration_mode=collaboration_mode,
        customer_message=customer_message,
        rep_alert_brief=rep_brief,
        fit_confirmed=fit_confirmed,
        fit_score=fit_score,
        delivery_status=decision.status.value,
        handoff_queued=handoff_queued,
        human_intervention_open=has_open_human_intervention(ctx.metadata),
        pending_draft=pending_draft,
        pending_draft_id=pending_draft_id,
        rep_suggestion=rep_suggestion,
        interpretation_status=interpretation_status,
        decision_trace=trace,
    )


def _build_trace(
    *,
    turn: int,
    interpretation_status: str,
    lead_signals: LeadSignals,
    hits: List[TriggerHit],
    intervention_trigger: Optional[str],
    newly_opened: bool,
    earlier_human_trigger: Optional[str],
    notified: List[TriggerHit],
    mode: CollaborationMode,
    mode_reason: str,
    decision,
    response_source: str,
    fit_confirmed: bool,
    loop_guard_applied: bool,
) -> DecisionTrace:
    if intervention_trigger and newly_opened:
        action, which = INTERVENTION_OPENED, intervention_trigger
    elif intervention_trigger:
        action, which = INTERVENTION_ALREADY_OPEN, intervention_trigger
    elif earlier_human_trigger:
        action, which = INTERVENTION_CARRIED_OVER, earlier_human_trigger
    else:
        action, which = INTERVENTION_NONE, None

    if notified:
        lead = notified[0]
        why = f"queued {lead.trigger_type} [{lead.trigger_class}]"
        if len(notified) > 1:
            why += "; also " + ", ".join(h.trigger_type for h in notified[1:])
    elif hits:
        why = "already notified / open: " + ", ".join(h.trigger_type for h in hits)
    else:
        why = "no trigger fired"

    return DecisionTrace(
        turn=turn,
        interpretation_status=interpretation_status,
        signals=lead_signals.as_dict(),
        triggers=list(hits),
        primary_trigger=hits[0].trigger_type if hits else HandoffTriggerType.NONE.value,
        primary_class=hits[0].trigger_class if hits else None,
        intervention_action=action,
        intervention_trigger=which,
        rep_notified=bool(notified),
        rep_notified_reason=why,
        mode=mode.value,
        mode_reason=mode_reason,
        delivery_status=decision.status.value,
        delivery_reason=decision.reason,
        response_source=response_source,
        outcome=outcome_for_delivery_status(decision.status.value),
        fit_confirmed=fit_confirmed,
        loop_guard_applied=loop_guard_applied,
    )


# ---------------------------------------------------------------------------
# Dependency wiring
# ---------------------------------------------------------------------------

def build_default_dependencies() -> tuple[
    MemoryStore,
    LeadSignalExtractor,
    CustomerBehaviorEngine,
    RepAssistEngine,
    HandoffManager,
    ModeStateMachine,
    HandoffQueue,
]:
    """Wire default in-memory dependencies for CLI or tests.

    Does not include fit_criteria — pass ``SIERRA_FIT_CRITERIA`` explicitly
    to ``run_turn()`` for live use. Tests that don't need fit evaluation
    can omit it; fit_confirmed will default to False (safe path).
    """
    store = MemoryStore()
    queue = HandoffQueue()
    return (
        store,
        LeadSignalExtractor(),
        CustomerBehaviorEngine(),
        RepAssistEngine(),
        HandoffManager(queue),
        ModeStateMachine(),
        queue,
    )
