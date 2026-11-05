"""FastAPI layer — exposes the existing orchestrator over HTTP.

This file adds NO new agent logic. Every endpoint is a thin wrapper
around functions that already exist and are already tested:
    run_turn()                  → src/orchestrator.py
    build_default_dependencies() → src/orchestrator.py
    ModeStateMachine.transition() → src/collaboration/mode_state_machine.py
    RepAssistEngine.create_alert_brief() → src/rep_layer/rep_assist_engine.py

Run with:
    uvicorn src.api:app --reload --port 8000

Then test with:
    curl -X POST http://localhost:8000/chat \
      -H "Content-Type: application/json" \
      -d '{"lead_id": "demo-1", "message": "Tell me about pricing", "rep_online": true}'
"""

from __future__ import annotations

import hmac
import os
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.clients.sierra.fit_criteria import SIERRA_FIT_CRITERIA
from src.collaboration.mode_state_machine import CollaborationMode, ModeStateMachine
from src.core.lead_context import LeadContext
from src.domain.session_state import (
    KEY_APPROVAL_REQUIRED,
    KEY_COLLABORATION_MODE,
    KEY_LIVE_SESSION,
    drain_outbox,
    has_open_human_intervention,
    hydrate_mode_machine,
    decision_traces,
    open_interventions,
    rep_notices,
    pending_relay_drafts,
    persist_collaboration_mode,
    reject_relay_draft,
    release_relay_draft,
    resolve_interventions,
)
from src.orchestrator import build_default_dependencies, run_turn

# ---------------------------------------------------------------------------
# App setup — single shared dependency set for the whole server process.
# This mirrors what main.py and chat.py already do — build once, reuse
# across every request. In-memory MemoryStore means state resets on
# server restart. Fine for a prototype; swap for Redis/Postgres in
# production (see requirements.txt notes on future dependencies).
# ---------------------------------------------------------------------------

app = FastAPI(title="Lead Agent API", version="0.1.0")

# CORS — allows a browser-based frontend (chat widget, rep dashboard)
# running on a different port/origin to call this API during development.
# Tighten allow_origins to your actual frontend domain before any real
# deployment — "*" is prototype-only.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

(
    _store,
    _signal_extractor,
    _customer_engine,
    _rep_engine,
    _handoff_manager,
    _unused_shared_mode_machine,
    _queue,
) = build_default_dependencies()
# NOTE: the ModeStateMachine from build_default_dependencies() is deliberately
# unused here. It is mutable per-conversation state; sharing one instance across
# leads and concurrent requests lets one lead's mode bleed into another's.
# Every request builds a fresh machine hydrated from that lead's stored mode.


def _fresh_mode_machine(ctx: LeadContext) -> ModeStateMachine:
    machine = ModeStateMachine()
    hydrate_mode_machine(machine, ctx.metadata.get(KEY_COLLABORATION_MODE))
    return machine


def _apply_mode(ctx: LeadContext, mode: CollaborationMode) -> None:
    """Write the mode to BOTH places run_turn reads/shows it from."""
    ctx.collaboration_mode = mode.value
    persist_collaboration_mode(ctx.metadata, mode)


# ---------------------------------------------------------------------------
# Rep authentication
# ---------------------------------------------------------------------------

def require_rep(x_rep_token: Optional[str] = Header(default=None)) -> None:
    """Gate rep-only endpoints behind a shared secret. Fails closed."""
    expected = os.environ.get("LEAD_AGENT_REP_TOKEN", "")
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="Rep endpoints are disabled: LEAD_AGENT_REP_TOKEN is not configured.",
        )
    if not x_rep_token or not hmac.compare_digest(x_rep_token, expected):
        raise HTTPException(status_code=403, detail="Invalid or missing rep token.")


# ---------------------------------------------------------------------------
# Request / response schemas
# Pydantic models define the API contract — what the frontend must send
# and what it gets back. This is the "API contract" engineers will ask
# about when reviewing the prototype.
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    """What the browser may send. Nothing here can influence authorization.

    Extra fields (for example a legacy widget still sending ``rep_online`` or
    ``awaiting_approval``) are ignored, never honored.
    """

    lead_id: str
    message: str


class ChatResponse(BaseModel):
    """Customer-safe turn result.

    ``customer_message`` is the only text the widget may display. Rep-only
    material (alert briefs, RELAY drafts, SHADOW suggestions) is deliberately
    absent; reps read it through the token-protected endpoints.
    """

    lead_id: str
    trust_state: str
    collaboration_mode: str
    handoff_triggered: bool
    trigger_type: str
    fit_confirmed: bool
    fit_score: Optional[int]
    customer_message: Optional[str]
    delivery_status: str
    human_intervention_open: bool


class OutboxMessage(BaseModel):
    draft_id: str
    message: str


class OutboxResponse(BaseModel):
    lead_id: str
    messages: List[OutboxMessage]


class RepActionRequest(BaseModel):
    lead_id: str
    # "online" | "offline" | "shadow" | "relay" | "autonomous" | "resolve" | "assign" | "score"
    action: str
    value: Optional[str] = None  # rep name for "assign", score for "score"


class RepApproveRequest(BaseModel):
    lead_id: str
    draft_id: str
    edited_text: Optional[str] = None  # rep's own wording replaces the agent draft


class RepRejectRequest(BaseModel):
    lead_id: str
    draft_id: str


class RepApproveResponse(BaseModel):
    lead_id: str
    draft_id: str
    status: str
    released_message: Optional[str] = None


class RepActionResponse(BaseModel):
    lead_id: str
    collaboration_mode: str
    rep_online: bool
    assigned_rep: Optional[str]
    lead_score: int
    handoff_queue_length: int
    approval_required: bool = False
    live_session: bool = False
    open_interventions: int = 0


class ContextResponse(BaseModel):
    lead_id: str
    customer_state: str
    collaboration_mode: str
    sentiment: str
    lead_score: int
    rep_online: bool
    assigned_rep: Optional[str]
    conversation_summary: str
    handoff_queue: list
    pending_interventions: List[Dict[str, Any]] = []
    pending_relay_drafts: List[Dict[str, Any]] = []
    rep_notices: List[Dict[str, Any]] = []
    # Rep-internal: why each recent turn was answered / held / drafted.
    decision_trace: List[Dict[str, Any]] = []


class BriefResponse(BaseModel):
    lead_id: str
    trigger: str
    lead_score: int
    sentiment: str
    recommended_action: str
    summary: str
    urgency_sla: str


# ---------------------------------------------------------------------------
# POST /chat
# The main turn endpoint — everything the customer chat widget calls.
# Wraps run_turn() exactly as chat.py and main.py already do.
# ---------------------------------------------------------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """Process one customer turn.

    Rep availability, live-session state and the RELAY approval gate are read
    from backend state for this lead — never from the request.
    """
    existing = _store.get(req.lead_id)
    rep_online = bool(existing.rep_online) if existing else False
    live_session = bool(existing.metadata.get(KEY_LIVE_SESSION, False)) if existing else False
    awaiting_approval = (
        bool(existing.metadata.get(KEY_APPROVAL_REQUIRED, False)) if existing else False
    )

    result = run_turn(
        lead_id=req.lead_id,
        raw_message=req.message,
        store=_store,
        signal_extractor=_signal_extractor,
        customer_engine=_customer_engine,
        rep_engine=_rep_engine,
        handoff_manager=_handoff_manager,
        mode_machine=ModeStateMachine(),
        rep_online=rep_online,
        live_session=live_session,
        awaiting_approval=awaiting_approval,
        fit_criteria=SIERRA_FIT_CRITERIA,
    )

    return ChatResponse(
        lead_id=result.context.lead_id,
        trust_state=result.trust_state.value,
        collaboration_mode=result.collaboration_mode.value,
        handoff_triggered=result.handoff_triggered,
        trigger_type=result.trigger_type,
        fit_confirmed=result.fit_confirmed,
        fit_score=result.fit_score,
        customer_message=result.customer_message,
        delivery_status=result.delivery_status,
        human_intervention_open=result.human_intervention_open,
    )


# ---------------------------------------------------------------------------
# GET /outbox/{lead_id}
# Customer pickup for messages a rep approved (RELAY). Returns and clears them.
# Contains only text a human explicitly released.
# ---------------------------------------------------------------------------

@app.get("/outbox/{lead_id}", response_model=OutboxResponse)
def get_outbox(lead_id: str) -> OutboxResponse:
    ctx = _store.get(lead_id)
    if ctx is None:
        return OutboxResponse(lead_id=lead_id, messages=[])
    items = drain_outbox(ctx.metadata)
    _store.save(ctx)
    return OutboxResponse(
        lead_id=lead_id,
        messages=[OutboxMessage(**i) for i in items],
    )


# ---------------------------------------------------------------------------
# GET /context/{lead_id}
# Returns the full LeadContext snapshot — used by the rep dashboard to
# render trust arc, fit score, sentiment, and handoff history.
# ---------------------------------------------------------------------------

@app.get("/context/{lead_id}", response_model=ContextResponse, dependencies=[Depends(require_rep)])
def get_context(lead_id: str) -> ContextResponse:
    """Return the current LeadContext for a lead.

    Direct wrapper around store.get() — the same call chat.py and
    rep_chat.py already make when you type the 'context' command.
    """
    ctx = _store.get(lead_id)
    if ctx is None:
        raise HTTPException(status_code=404, detail=f"No context found for lead_id '{lead_id}'")

    return ContextResponse(
        lead_id=ctx.lead_id,
        customer_state=ctx.customer_state,
        collaboration_mode=ctx.collaboration_mode,
        sentiment=ctx.sentiment,
        lead_score=ctx.lead_score,
        rep_online=ctx.rep_online,
        assigned_rep=ctx.assigned_rep,
        conversation_summary=ctx.conversation_summary,
        handoff_queue=ctx.handoff_queue,
        pending_interventions=open_interventions(ctx.metadata),
        pending_relay_drafts=pending_relay_drafts(ctx.metadata),
        rep_notices=rep_notices(ctx.metadata),
        decision_trace=decision_traces(ctx.metadata),
    )


# ---------------------------------------------------------------------------
# GET /brief/{lead_id}
# Returns the latest alert brief — used by the rep dashboard's alert card.
# Regenerates a brief from current context rather than storing history,
# matching the same pattern rep_chat.py uses with the 'brief' command.
# ---------------------------------------------------------------------------

@app.get("/brief/{lead_id}", response_model=BriefResponse, dependencies=[Depends(require_rep)])
def get_brief(lead_id: str) -> BriefResponse:
    """Return the latest alert brief for a lead, if one applies.

    Uses the lead's current trigger_type stored in metadata (set by the
    last run_turn() call) to regenerate the brief via RepAssistEngine —
    the same engine used inside run_rep_alert_path().
    """
    ctx = _store.get(lead_id)
    if ctx is None:
        raise HTTPException(status_code=404, detail=f"No context found for lead_id '{lead_id}'")

    last_trigger = ctx.metadata.get("last_trigger_type")
    if not last_trigger or last_trigger == "none":
        raise HTTPException(
            status_code=404,
            detail=f"No alert brief available for lead_id '{lead_id}' — no trigger has fired.",
        )

    brief = _rep_engine.create_alert_brief(ctx, trigger=last_trigger)

    return BriefResponse(
        lead_id=brief.lead_id,
        trigger=brief.trigger,
        lead_score=brief.lead_score,
        sentiment=brief.sentiment,
        recommended_action=brief.recommended_action,
        summary=brief.summary,
        urgency_sla=brief.urgency_sla,
    )


# ---------------------------------------------------------------------------
# POST /rep/action
# Handles rep commands from the dashboard: online/offline/shadow/relay/
# assign/score. Mirrors the exact command set already built and tested
# in rep_chat.py — this just exposes the same actions over HTTP.
# ---------------------------------------------------------------------------

def _rep_action_response(ctx: LeadContext) -> RepActionResponse:
    return RepActionResponse(
        lead_id=ctx.lead_id,
        collaboration_mode=ctx.collaboration_mode,
        rep_online=ctx.rep_online,
        assigned_rep=ctx.assigned_rep,
        lead_score=ctx.lead_score,
        handoff_queue_length=len(ctx.handoff_queue),
        approval_required=bool(ctx.metadata.get(KEY_APPROVAL_REQUIRED, False)),
        live_session=bool(ctx.metadata.get(KEY_LIVE_SESSION, False)),
        open_interventions=len(open_interventions(ctx.metadata)),
    )


@app.post("/rep/action", response_model=RepActionResponse, dependencies=[Depends(require_rep)])
def rep_action(req: RepActionRequest) -> RepActionResponse:
    """Apply a rep dashboard action to a lead's backend state.

    Supported actions:
        online     → rep_online = True
        offline    → rep_online = False, live/approval gates off; records an
                     interruption event if a mode was active (soul.md value 4).
                     Open handoffs are NOT cleared.
        shadow     → live session on (rep must be online)
        relay      → approval gate on: agent drafts are held for /rep/approve
        autonomous → live session and approval gate off
        resolve    → clear open handoffs; the agent may resume
        assign     → assigned_rep = value
        score      → lead_score = int(value)
    """
    ctx = _store.get(req.lead_id)
    if ctx is None:
        ctx = LeadContext(lead_id=req.lead_id)

    action = req.action.strip().lower()
    machine = _fresh_mode_machine(ctx)

    def _transition(handoff: bool = False) -> None:
        mode = machine.transition(
            rep_online=ctx.rep_online,
            live_session=bool(ctx.metadata.get(KEY_LIVE_SESSION, False)),
            handoff_triggered=handoff,
            awaiting_approval=bool(ctx.metadata.get(KEY_APPROVAL_REQUIRED, False)),
            context=ctx,
        )
        _apply_mode(ctx, mode)

    if action == "online":
        ctx.rep_online = True

    elif action == "offline":
        ctx.rep_online = False
        ctx.metadata[KEY_LIVE_SESSION] = False
        _transition()

    elif action == "shadow":
        if not ctx.rep_online:
            raise HTTPException(status_code=400, detail="Rep must be online to enter shadow mode.")
        ctx.metadata[KEY_LIVE_SESSION] = True
        ctx.metadata[KEY_APPROVAL_REQUIRED] = False
        _transition(handoff=has_open_human_intervention(ctx.metadata))

    elif action == "relay":
        if not ctx.rep_online:
            raise HTTPException(status_code=400, detail="Rep must be online to enter relay mode.")
        ctx.metadata[KEY_LIVE_SESSION] = False
        ctx.metadata[KEY_APPROVAL_REQUIRED] = True
        _transition(handoff=has_open_human_intervention(ctx.metadata))

    elif action == "autonomous":
        ctx.metadata[KEY_LIVE_SESSION] = False
        ctx.metadata[KEY_APPROVAL_REQUIRED] = False
        _transition(handoff=has_open_human_intervention(ctx.metadata))

    elif action == "resolve":
        resolve_interventions(ctx.metadata)
        _transition()

    elif action == "assign":
        if not req.value:
            raise HTTPException(status_code=400, detail="'assign' requires a value (rep name).")
        ctx.assigned_rep = req.value

    elif action == "score":
        if req.value is None:
            raise HTTPException(status_code=400, detail="'score' requires a value (0-100).")
        try:
            score = int(req.value)
        except ValueError:
            raise HTTPException(status_code=400, detail="'score' value must be an integer.")
        if not (0 <= score <= 100):
            raise HTTPException(status_code=400, detail="'score' must be between 0 and 100.")
        ctx.lead_score = score

    else:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unknown action '{action}'. Valid: online, offline, shadow, relay, "
                "autonomous, resolve, assign, score."
            ),
        )

    _store.save(ctx)
    return _rep_action_response(ctx)


# ---------------------------------------------------------------------------
# POST /rep/approve  and  POST /rep/reject
# The ONLY path by which a RELAY draft can reach the customer. Rep-token
# protected; draft state lives server-side, so the browser cannot self-approve.
# ---------------------------------------------------------------------------

@app.post("/rep/approve", response_model=RepApproveResponse, dependencies=[Depends(require_rep)])
def rep_approve(req: RepApproveRequest) -> RepApproveResponse:
    ctx = _store.get(req.lead_id)
    if ctx is None:
        raise HTTPException(status_code=404, detail=f"No context found for lead_id '{req.lead_id}'")
    text = release_relay_draft(ctx.metadata, req.draft_id, edited_text=req.edited_text)
    if text is None:
        raise HTTPException(
            status_code=404,
            detail="No such pending draft (unknown, already handled, or superseded).",
        )
    _store.save(ctx)
    return RepApproveResponse(
        lead_id=req.lead_id, draft_id=req.draft_id, status="released", released_message=text
    )


@app.post("/rep/reject", response_model=RepApproveResponse, dependencies=[Depends(require_rep)])
def rep_reject(req: RepRejectRequest) -> RepApproveResponse:
    ctx = _store.get(req.lead_id)
    if ctx is None:
        raise HTTPException(status_code=404, detail=f"No context found for lead_id '{req.lead_id}'")
    if not reject_relay_draft(ctx.metadata, req.draft_id):
        raise HTTPException(status_code=404, detail="No such pending draft.")
    _store.save(ctx)
    return RepApproveResponse(lead_id=req.lead_id, draft_id=req.draft_id, status="rejected")


# ---------------------------------------------------------------------------
# Health check — useful for confirming the server is up before wiring
# a frontend to it.
# ---------------------------------------------------------------------------

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "lead-agent-api"}
