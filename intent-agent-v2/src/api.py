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

from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.clients.sierra.fit_criteria import SIERRA_FIT_CRITERIA
from src.collaboration.mode_state_machine import CollaborationMode
from src.core.lead_context import LeadContext
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
    _mode_machine,
    _queue,
) = build_default_dependencies()


# ---------------------------------------------------------------------------
# Request / response schemas
# Pydantic models define the API contract — what the frontend must send
# and what it gets back. This is the "API contract" engineers will ask
# about when reviewing the prototype.
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    lead_id: str
    message: str
    rep_online: bool = False
    live_session: bool = False
    awaiting_approval: bool = False


class ChatResponse(BaseModel):
    lead_id: str
    trust_state: str
    collaboration_mode: str
    handoff_triggered: bool
    trigger_type: str
    fit_confirmed: bool
    fit_score: Optional[int]
    customer_message: Optional[str]
    rep_alert_brief: Optional[Dict[str, Any]]


class RepActionRequest(BaseModel):
    lead_id: str
    action: str  # "online" | "offline" | "shadow" | "relay" | "assign" | "score"
    value: Optional[str] = None  # rep name for "assign", score for "score"


class RepActionResponse(BaseModel):
    lead_id: str
    collaboration_mode: str
    rep_online: bool
    assigned_rep: Optional[str]
    lead_score: int
    handoff_queue_length: int


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
    """Process one customer turn and return the full orchestration result.

    This is a direct call to run_turn() — no new logic. The only job here
    is unwrapping the HTTP request into function arguments and wrapping
    the OrchestrationResult back into JSON.
    """
    result = run_turn(
        lead_id=req.lead_id,
        raw_message=req.message,
        store=_store,
        signal_extractor=_signal_extractor,
        customer_engine=_customer_engine,
        rep_engine=_rep_engine,
        handoff_manager=_handoff_manager,
        mode_machine=_mode_machine,
        rep_online=req.rep_online,
        live_session=req.live_session,
        awaiting_approval=req.awaiting_approval,
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
        rep_alert_brief=(
            result.rep_alert_brief.as_dict() if result.rep_alert_brief else None
        ),
    )


# ---------------------------------------------------------------------------
# GET /context/{lead_id}
# Returns the full LeadContext snapshot — used by the rep dashboard to
# render trust arc, fit score, sentiment, and handoff history.
# ---------------------------------------------------------------------------

@app.get("/context/{lead_id}", response_model=ContextResponse)
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
    )


# ---------------------------------------------------------------------------
# GET /brief/{lead_id}
# Returns the latest alert brief — used by the rep dashboard's alert card.
# Regenerates a brief from current context rather than storing history,
# matching the same pattern rep_chat.py uses with the 'brief' command.
# ---------------------------------------------------------------------------

@app.get("/brief/{lead_id}", response_model=BriefResponse)
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

@app.post("/rep/action", response_model=RepActionResponse)
def rep_action(req: RepActionRequest) -> RepActionResponse:
    """Apply a rep dashboard action to a lead's context and mode machine.

    Supported actions:
        online   → sets rep_online = True
        offline  → sets rep_online = False, triggers offline-drop event
                   if a mode was interrupted (soul.md value 4)
        shadow   → transitions mode to SHADOW (rep must be online)
        relay    → transitions mode to RELAY (rep must be online)
        assign   → sets assigned_rep to req.value
        score    → sets lead_score to int(req.value)
    """
    ctx = _store.get(req.lead_id)
    if ctx is None:
        ctx = LeadContext(lead_id=req.lead_id)

    action = req.action.strip().lower()

    if action == "online":
        ctx.rep_online = True

    elif action == "offline":
        ctx.rep_online = False
        # Same offline-drop logic rep_chat.py already exercises —
        # preserves interrupted mode into handoff_queue (soul.md value 4).
        _mode_machine.transition(
            rep_online=False,
            live_session=False,
            handoff_triggered=False,
            awaiting_approval=False,
            context=ctx,
        )
        ctx.collaboration_mode = _mode_machine.get_mode().value

    elif action == "shadow":
        if not ctx.rep_online:
            raise HTTPException(status_code=400, detail="Rep must be online to enter shadow mode.")
        new_mode = _mode_machine.transition(
            rep_online=True, live_session=True,
            handoff_triggered=False, awaiting_approval=False,
        )
        ctx.collaboration_mode = new_mode.value

    elif action == "relay":
        if not ctx.rep_online:
            raise HTTPException(status_code=400, detail="Rep must be online to enter relay mode.")
        new_mode = _mode_machine.transition(
            rep_online=True, live_session=False,
            handoff_triggered=False, awaiting_approval=True,
        )
        ctx.collaboration_mode = new_mode.value

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
            detail=f"Unknown action '{action}'. Valid: online, offline, shadow, relay, assign, score.",
        )

    _store.save(ctx)

    return RepActionResponse(
        lead_id=ctx.lead_id,
        collaboration_mode=ctx.collaboration_mode,
        rep_online=ctx.rep_online,
        assigned_rep=ctx.assigned_rep,
        lead_score=ctx.lead_score,
        handoff_queue_length=len(ctx.handoff_queue),
    )


# ---------------------------------------------------------------------------
# Health check — useful for confirming the server is up before wiring
# a frontend to it.
# ---------------------------------------------------------------------------

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "lead-agent-api"}
