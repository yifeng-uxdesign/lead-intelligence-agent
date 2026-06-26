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

from dataclasses import dataclass
from typing import Dict, Optional

from src.application.signal_adapters import (
    handoff_signal_dict_from_lead,
    lead_signals_to_trust_signals,
)
from src.clients.sierra.fit_criteria import FitCriteria, fit_summary
from src.collaboration.handoff_manager import HandoffManager
from src.collaboration.mode_state_machine import CollaborationMode, ModeStateMachine
from src.core.handoff_queue import HandoffQueue
from src.core.lead_context import LeadContext
from src.core.memory_store import MemoryStore
from src.customer_layer.behavior_engine import CustomerBehaviorEngine
from src.customer_layer.trust_state_machine import TrustState, TrustStateMachine
from src.domain.session_state import (
    KEY_COLLABORATION_MODE,
    hydrate_mode_machine,
    hydrate_trust_machine,
    persist_collaboration_mode,
    persist_trust_state,
)
from src.domain.trigger_catalog import rep_brief_key_for_handoff
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
# Orchestration path functions
# ---------------------------------------------------------------------------

def run_mode_transition_path(
    mode_machine: ModeStateMachine,
    *,
    rep_online: bool,
    live_session: bool,
    handoff_triggered: bool,
    awaiting_approval: bool,
) -> CollaborationMode:
    """Compute next collaboration mode (autonomous vs rep-assisted variants)."""
    return mode_machine.transition(
        rep_online=rep_online,
        live_session=live_session,
        handoff_triggered=handoff_triggered,
        awaiting_approval=awaiting_approval,
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


def run_customer_response_path(
    engine: CustomerBehaviorEngine,
    context: LeadContext,
    trust_state: TrustState,
    lead_signals: LeadSignals,
    fit_criteria: Optional[FitCriteria] = None,
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
        },
    )


def run_rep_alert_path(
    rep_engine: RepAssistEngine,
    handoff_manager: HandoffManager,
    context: LeadContext,
    trigger_type: str,
) -> AlertBrief:
    """Build internal rep alert brief and enqueue handoff for rep layer pickup."""
    brief_trigger = rep_brief_key_for_handoff(trigger_type)
    brief = rep_engine.create_alert_brief(context, brief_trigger)
    handoff_manager.request_rep_handoff(
        context.lead_id,
        {
            "trigger_type": trigger_type,
            "alert_brief": brief.as_dict(),
            "sla_minutes": handoff_manager.get_sla(trigger_type),
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

    # 1) Load or create lead context from memory store
    ctx = store.get(lead_id)
    if ctx is None:
        ctx = LeadContext(lead_id=lead_id)
    hydrate_mode_machine(
        mode_machine, ctx.metadata.get(KEY_COLLABORATION_MODE)
    )

    # 2) Extract structured signals from raw customer message
    lead_signals = signal_extractor.extract(raw_message)
    ctx.update_sentiment(lead_signals.sentiment)
    ctx.update_summary(f"User: {raw_message.strip()[:2000]}")

    trust_machine = hydrate_trust_machine(ctx.metadata)

    # 3) Update customer psychological trust state
    trust_state = run_customer_trust_path(ctx, trust_machine, lead_signals)

    # 4) Evaluate handoff trigger conditions
    handoff_payload = handoff_signal_dict_from_lead(lead_signals, raw_message)
    handoff_triggered, trigger_type = handoff_manager.should_trigger(
        handoff_payload, ctx
    )

    # 5) Transition collaboration mode
    collaboration_mode = run_mode_transition_path(
        mode_machine,
        rep_online=rep_online,
        live_session=live_session,
        handoff_triggered=handoff_triggered,
        awaiting_approval=awaiting_approval,
    )
    ctx.collaboration_mode = collaboration_mode.value
    persist_collaboration_mode(ctx.metadata, collaboration_mode)
    ctx.rep_online = rep_online

    customer_message: Optional[str] = None
    rep_brief: Optional[AlertBrief] = None
    fit_confirmed: bool = False
    fit_score: Optional[int] = None

    # 6-7) Branch: rep alert path or customer response path
    if collaboration_mode == CollaborationMode.ALERT:
        # Trust-critical moment — route to rep, suppress customer response.
        # soul.md value 4: this moment belongs to a human rep.
        rep_brief = run_rep_alert_path(
            rep_engine, handoff_manager, ctx, trigger_type
        )
    else:
        # Autonomous or shadow path — generate customer-facing response.
        # fit_criteria drives fit_confirmed inside run_customer_response_path.
        customer_message = run_customer_response_path(
            customer_engine,
            ctx,
            trust_state,
            lead_signals,
            fit_criteria=fit_criteria,
        )

        # Expose fit assessment in result for logging and test assertions
        if fit_criteria is not None:
            prospect_signals = _prospect_signals_from_lead(lead_signals)
            assessment = fit_summary(prospect_signals, fit_criteria)
            fit_confirmed = assessment["fit_confirmed"]
            fit_score = assessment["score"]

    # 8) Persist updated context
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
