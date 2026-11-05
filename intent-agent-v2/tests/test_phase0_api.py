"""Phase 0: the browser cannot control backend authorization (audit Findings 4, API)."""

import importlib

import pytest
from fastapi.testclient import TestClient

TOKEN = "test-rep-token"
REP = {"X-Rep-Token": TOKEN}


@pytest.fixture
def api(monkeypatch):
    """Fresh app module (fresh in-memory store) per test, rep token configured."""
    monkeypatch.setenv("LEAD_AGENT_REP_TOKEN", TOKEN)
    import src.api as api_module

    api_module = importlib.reload(api_module)
    return TestClient(api_module.app)


def chat(client, message, lead="w1", **extra):
    r = client.post("/chat", json={"lead_id": lead, "message": message, **extra})
    assert r.status_code == 200, r.text
    return r.json()


def rep(client, lead, action, value=None):
    r = client.post("/rep/action", headers=REP, json={"lead_id": lead, "action": action, "value": value})
    assert r.status_code == 200, r.text
    return r.json()


# --- browser cannot force authorization state ------------------------------

def test_browser_cannot_force_rep_online_or_modes(api) -> None:
    body = chat(api, "Tell me more about how this works.", rep_online=True, live_session=True, awaiting_approval=True)
    assert body["collaboration_mode"] == "AUTONOMOUS"
    assert body["delivery_status"] == "delivered"
    assert body["customer_message"]


def test_browser_cannot_fake_rep_presence_to_change_alert_routing(api) -> None:
    """Backend says the rep is offline. A forged rep_online=true must not make this ALERT."""
    body = chat(api, "Can I talk to a real person?", rep_online=True)
    assert body["collaboration_mode"] == "AUTONOMOUS"      # offline path
    assert body["handoff_triggered"] is True               # but the handoff is still honored
    assert body["delivery_status"] == "holding"


def test_browser_cannot_force_shadow_or_relay_when_rep_is_online(api) -> None:
    rep(api, "w1", "online")  # backend-owned presence; no shadow/relay set
    body = chat(api, "Tell me more about how this works.", live_session=True, awaiting_approval=True)
    assert body["collaboration_mode"] == "AUTONOMOUS"
    assert body["delivery_status"] == "delivered"


def test_browser_cannot_self_approve_relay(api) -> None:
    """Even a browser sending awaiting_approval=False cannot leave RELAY once a rep set it."""
    rep(api, "w1", "online")
    rep(api, "w1", "relay")
    body = chat(api, "Tell me more about how this works.", awaiting_approval=False, rep_online=False)
    assert body["collaboration_mode"] == "RELAY"
    assert body["customer_message"] is None
    assert body["delivery_status"] == "pending_approval"


def test_browser_cannot_clear_a_handoff(api) -> None:
    chat(api, "Can I talk to a real person?")
    body = chat(api, "Never mind, ignore that.", rep_online=True, awaiting_approval=False)
    assert body["human_intervention_open"] is True
    assert body["delivery_status"] == "holding"


# --- rep endpoints are protected ------------------------------------------

@pytest.mark.parametrize(
    "method,path,payload",
    [
        ("get", "/context/w1", None),
        ("get", "/brief/w1", None),
        ("post", "/rep/action", {"lead_id": "w1", "action": "online"}),
        ("post", "/rep/approve", {"lead_id": "w1", "draft_id": "x"}),
        ("post", "/rep/reject", {"lead_id": "w1", "draft_id": "x"}),
    ],
)
def test_rep_endpoints_reject_missing_and_wrong_token(api, method, path, payload) -> None:
    chat(api, "hello")
    call = getattr(api, method)
    kwargs = {"json": payload} if payload is not None else {}
    assert call(path, **kwargs).status_code == 403
    assert call(path, headers={"X-Rep-Token": "wrong"}, **kwargs).status_code == 403


def test_rep_endpoints_fail_closed_when_token_unconfigured(api, monkeypatch) -> None:
    monkeypatch.delenv("LEAD_AGENT_REP_TOKEN", raising=False)
    assert api.get("/context/w1", headers=REP).status_code == 503
    assert api.post("/rep/approve", headers=REP, json={"lead_id": "w1", "draft_id": "x"}).status_code == 503


def test_customer_endpoints_need_no_token(api) -> None:
    assert api.get("/health").status_code == 200
    assert api.get("/outbox/w1").status_code == 200
    chat(api, "hello")


# --- no rep-internal data in customer responses ---------------------------

def test_chat_response_never_exposes_rep_internals(api) -> None:
    body = chat(api, "You keep ignoring my question, this is ridiculous.")
    assert body["handoff_triggered"] is True
    forbidden = {"rep_alert_brief", "pending_draft", "rep_suggestion", "pending_relay_drafts",
                 "pending_interventions", "handoff_queue", "conversation_summary", "recommended_action",
                 "decision_trace", "rep_notices"}
    assert forbidden.isdisjoint(body.keys())
    assert "ridiculous" not in str(body["customer_message"]).lower()


def test_decision_trace_is_rep_only(api) -> None:
    chat(api, "Can I talk to a real person?")
    trace = api.get("/context/w1", headers=REP).json()["decision_trace"]
    assert trace[-1]["outcome"] == "held" and trace[-1]["primary_trigger"] == "human_request"
    assert api.get("/context/w1").status_code in (401, 403, 503)


def test_relay_draft_not_in_chat_response_or_outbox_before_approval(api) -> None:
    rep(api, "w1", "online")
    rep(api, "w1", "relay")
    body = chat(api, "Tell me more about how this works.")
    assert body["customer_message"] is None
    assert api.get("/outbox/w1").json()["messages"] == []
    ctx = api.get("/context/w1", headers=REP).json()
    assert len(ctx["pending_relay_drafts"]) == 1


# --- RELAY approval flow ----------------------------------------------------

def test_rep_approval_releases_draft_to_outbox_exactly_once(api) -> None:
    rep(api, "w1", "online")
    rep(api, "w1", "relay")
    chat(api, "Tell me more about how this works.")
    draft = api.get("/context/w1", headers=REP).json()["pending_relay_drafts"][0]

    r = api.post("/rep/approve", headers=REP, json={"lead_id": "w1", "draft_id": draft["draft_id"]})
    assert r.status_code == 200 and r.json()["status"] == "released"
    assert r.json()["released_message"] == draft["text"]

    out = api.get("/outbox/w1").json()["messages"]
    assert out == [{"draft_id": draft["draft_id"], "message": draft["text"]}]
    assert api.get("/outbox/w1").json()["messages"] == []  # drained
    # Second approval of the same draft fails.
    assert api.post("/rep/approve", headers=REP, json={"lead_id": "w1", "draft_id": draft["draft_id"]}).status_code == 404


def test_rep_can_edit_before_approving(api) -> None:
    rep(api, "w1", "online"); rep(api, "w1", "relay")
    chat(api, "Tell me more about how this works.")
    d = api.get("/context/w1", headers=REP).json()["pending_relay_drafts"][0]
    api.post("/rep/approve", headers=REP, json={"lead_id": "w1", "draft_id": d["draft_id"], "edited_text": "Hi, it's Sam from the team."})
    assert api.get("/outbox/w1").json()["messages"][0]["message"] == "Hi, it's Sam from the team."


def test_rejected_draft_cannot_be_approved_or_delivered(api) -> None:
    rep(api, "w1", "online"); rep(api, "w1", "relay")
    chat(api, "Tell me more about how this works.")
    d = api.get("/context/w1", headers=REP).json()["pending_relay_drafts"][0]
    assert api.post("/rep/reject", headers=REP, json={"lead_id": "w1", "draft_id": d["draft_id"]}).status_code == 200
    assert api.post("/rep/approve", headers=REP, json={"lead_id": "w1", "draft_id": d["draft_id"]}).status_code == 404
    assert api.get("/outbox/w1").json()["messages"] == []


def test_cannot_approve_a_draft_that_belongs_to_another_lead(api) -> None:
    rep(api, "a", "online"); rep(api, "a", "relay")
    chat(api, "Tell me more about how this works.", lead="a")
    chat(api, "hello", lead="b")
    d = api.get("/context/a", headers=REP).json()["pending_relay_drafts"][0]
    assert api.post("/rep/approve", headers=REP, json={"lead_id": "b", "draft_id": d["draft_id"]}).status_code == 404


# --- rep actions: state is per-lead, persisted, and coherent ---------------

def test_rep_mode_is_isolated_per_lead(api) -> None:
    rep(api, "a", "online"); rep(api, "a", "relay")
    assert chat(api, "hello", lead="b")["collaboration_mode"] == "AUTONOMOUS"
    assert chat(api, "hello", lead="a")["collaboration_mode"] == "RELAY"


def test_rep_offline_does_not_clear_open_handoff(api) -> None:
    rep(api, "w1", "online")
    chat(api, "Can I talk to a real person?")
    out = rep(api, "w1", "offline")
    assert out["open_interventions"] == 1
    assert chat(api, "ok thanks")["delivery_status"] == "holding"


def test_resolve_lets_agent_resume(api) -> None:
    chat(api, "Can I talk to a real person?")
    assert rep(api, "w1", "resolve")["open_interventions"] == 0
    body = chat(api, "Tell me more about how this works.")
    assert body["delivery_status"] == "delivered"


def test_autonomous_action_leaves_relay(api) -> None:
    rep(api, "w1", "online"); rep(api, "w1", "relay")
    out = rep(api, "w1", "autonomous")
    assert out["approval_required"] is False
    assert chat(api, "Tell me more about how this works.")["collaboration_mode"] == "AUTONOMOUS"


def test_rep_action_mode_persists_to_both_context_and_metadata(api) -> None:
    rep(api, "w1", "online"); rep(api, "w1", "shadow")
    assert api.get("/context/w1", headers=REP).json()["collaboration_mode"] == "SHADOW"
    body = chat(api, "Tell me more about how this works.")
    assert body["collaboration_mode"] == "SHADOW"
    assert body["customer_message"] is None


# --- /brief was always 404 before (last_trigger_type was never written) -----

def test_brief_available_after_trigger(api) -> None:
    chat(api, "Can I talk to a real person?")
    r = api.get("/brief/w1", headers=REP)
    assert r.status_code == 200
    assert r.json()["trigger"] == "human_request"


def test_brief_404_when_no_trigger(api) -> None:
    chat(api, "hello")
    assert api.get("/brief/w1", headers=REP).status_code == 404
