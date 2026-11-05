"""Observe the Python backend. Policy cases use hand-labeled signals (StubExtractor);
understanding cases use the real extractor on raw text."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.collaboration.delivery_policy import DeliveryStatus  # noqa: E402
from src.customer_layer.fallback_variants import LOOP_BREAKERS  # noqa: E402
from src.domain.trigger_catalog import HandoffTriggerType  # noqa: E402
from src.orchestrator import build_default_dependencies, run_turn  # noqa: E402
from src.signals.extractor import LeadSignalExtractor, LeadSignals  # noqa: E402

from conformance.scoring import cases_hash, load_cases  # noqa: E402

_FACING = {DeliveryStatus.DELIVERED.value: "answer", DeliveryStatus.HOLDING.value: "holding",
           DeliveryStatus.PENDING_APPROVAL.value: "draft_for_rep",
           DeliveryStatus.REP_SUGGESTION.value: "rep_suggestion"}
_DEFAULTS = dict(intent="general", urgency="medium", sentiment="neutral", objection_type="none",
                 human_request=False, competitor_mention=False, buying_signal=False,
                 stakeholder_signal=False, sentiment_target="unspecified", identity_question=False)


class StubExtractor:
    """Returns the hand-labeled signals for the current turn; '__raise' simulates failure."""

    def __init__(self):
        self.next: dict | None = None

    def extract(self, message: str) -> LeadSignals:
        s = self.next
        if s is not None and s.get("__raise"):
            raise RuntimeError("simulated interpreter failure")
        if s is None:
            return LeadSignalExtractor().extract(message)
        return LeadSignals(**{**_DEFAULTS, **s})


def _rep_flags(state: str, cur: dict) -> dict:
    if state == "online":
        return {**cur, "rep_online": True}
    if state == "offline":   # gates deliberately kept: an offline rep must not silently drop the approval gate
        return {**cur, "rep_online": False}
    if state == "shadow":
        return dict(rep_online=True, live_session=True, awaiting_approval=False)
    if state == "relay":
        return dict(rep_online=True, live_session=False, awaiting_approval=True)
    raise ValueError(state)


def derive_route(result, signals: LeadSignals) -> str:
    t = result.trigger_type
    if t == HandoffTriggerType.HUMAN_REQUEST.value:
        return "human"
    if signals.identity_question:
        return "identity"
    if t == HandoffTriggerType.FRUSTRATION.value:
        return "frustration_agent"
    if signals.sentiment == "frustration":
        return "frustration_other"
    if t == HandoffTriggerType.PRICING_DISCUSSION.value:
        return "pricing"
    if t == HandoffTriggerType.STRONG_BUYING_SIGNAL.value:
        return "buying"
    if t == HandoffTriggerType.COMPETITOR_MENTION.value:
        return "compare"
    if t == HandoffTriggerType.STAKEHOLDER_APPROVAL_NEEDED.value:
        return "stakeholder"
    if signals.objection_type in ("trust", "skepticism"):
        return "skeptical"
    return "none"


def observe_case(case: dict) -> list[dict]:
    store, _, engine, rep_engine, manager, _, _ = build_default_dependencies()
    stub = StubExtractor()
    flags = _rep_flags(case["rep"], dict(rep_online=False, live_session=False, awaiting_approval=False))
    if case["rep"] == "offline":
        flags = dict(rep_online=False, live_session=False, awaiting_approval=False)
    rows = []
    for turn in case["turns"]:
        if turn.get("rep"):
            flags = _rep_flags(turn["rep"], flags)
        stub.next = turn.get("signals") if case["layer"] == "policy" else None
        from src.collaboration.mode_state_machine import ModeStateMachine
        res = run_turn(lead_id=case["id"], raw_message=turn["u"], store=store, signal_extractor=stub,
                       customer_engine=engine, rep_engine=rep_engine, handoff_manager=manager,
                       mode_machine=ModeStateMachine(), fit_criteria=None, **flags)
        reply = res.customer_message or ""
        queued = bool(res.handoff_queued)
        status = res.delivery_status
        # human_path means the *customer* is offered a person (taxonomy.json), not
        # that the rep was notified: context/attention notices reach the rep
        # silently while the agent keeps answering. Only an intervention opened
        # this turn without a hold would offer a person.
        tr = res.decision_trace
        offers_person = tr is not None and tr.intervention_action == "opened"
        esc = "hold" if status == DeliveryStatus.HOLDING.value else ("human_path" if offers_person else "none")
        rows.append({
            "reply": reply, "route": derive_route(res, res.lead_signals), "escalation": esc,
            "rep_notified": queued, "customer_facing": _FACING.get(status),
            "intervention_open": bool(res.human_intervention_open),
            "trust_state": res.trust_state.value,
            "fallback_used": reply in LOOP_BREAKERS or res.interpretation_status in ("fallback", "failed", "empty"),
        })
    return rows


def main(out: str) -> None:
    doc = load_cases()
    obs = {c["id"]: observe_case(c) for c in doc["cases"]}
    Path(out).write_text(json.dumps({"engine": "backend", "cases_hash": cases_hash(), "observations": obs}, indent=1))
    print(f"backend: observed {len(obs)} cases -> {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent / "results" / "backend.json"))
