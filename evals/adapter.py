"""Adapter: run the config A behavior layer (rules + templates, no LLM) in-process.

Nothing under intent-agent-v2/ is modified. Everything here only imports the
source and reads values it already exposes (OrchestrationResult, DecisionTrace,
LeadContext.metadata via domain.session_state helpers).

Public API
    run_turn(history, user_message, ...) -> trace dict
        Replays `history` (list of earlier user messages) through a fresh
        session, then runs `user_message`. Deterministic in config A.
    Session  - keeps state across turns (what the runner uses for speed).
"""

from __future__ import annotations

import os
import sys
from dataclasses import replace
from typing import Any, Dict, List, Optional, Sequence

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "intent-agent-v2"))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.customer_layer import behavior_engine as _be  # noqa: E402
from src.domain import session_state as _ss  # noqa: E402
from src.orchestrator import build_default_dependencies, run_turn as _orch_run_turn  # noqa: E402
from src.signals.extractor import LeadSignalExtractor, LeadSignals  # noqa: E402

NEUTRAL = LeadSignals(
    intent="general", urgency="medium", sentiment="neutral", objection_type="none",
    human_request=False, competitor_mention=False, buying_signal=False,
    stakeholder_signal=False, sentiment_target="unspecified", identity_question=False,
)
STRUCTURED_RAW = "[structured input]"  # carries no lexeme the raw-text adapters look for


class _FixedExtractor(LeadSignalExtractor):
    """Structured mode: return injected signals, skipping the real extractor."""

    def __init__(self, sig: LeadSignals) -> None:
        self._sig = sig

    def extract(self, message: str) -> LeadSignals:  # noqa: D401
        return self._sig


def signals_from_overrides(overrides: Dict[str, Any]) -> LeadSignals:
    return replace(NEUTRAL, **overrides)


class Session:
    """One lead's conversation. Fresh dependencies per Session = state reset."""

    def __init__(self, *, rep_online: bool = True, live_session: bool = False,
                 awaiting_approval: bool = False, lead_id: str = "eval-lead") -> None:
        (self.store, self.extractor, self.customer, self.rep, self.handoff,
         self.mode_machine, self.queue) = build_default_dependencies()
        self.lead_id = lead_id
        self.rep_online = rep_online
        self.live_session = live_session
        self.awaiting_approval = awaiting_approval
        self.turn_no = 0
        self.history: List[str] = []

    # ------------------------------------------------------------------
    def turn(self, user_message: str, injected: Optional[LeadSignals] = None) -> Dict[str, Any]:
        extractor = _FixedExtractor(injected) if injected is not None else self.extractor
        raw = STRUCTURED_RAW if injected is not None else user_message
        res = _orch_run_turn(
            lead_id=self.lead_id, raw_message=raw, store=self.store,
            signal_extractor=extractor, customer_engine=self.customer, rep_engine=self.rep,
            handoff_manager=self.handoff, mode_machine=self.mode_machine,
            rep_online=self.rep_online, live_session=self.live_session,
            awaiting_approval=self.awaiting_approval, fit_criteria=None,
        )
        self.turn_no += 1
        self.history.append(user_message)
        return self._trace(user_message, res, structured=injected is not None)

    # ------------------------------------------------------------------
    def _trace(self, user_message: str, res: Any, *, structured: bool) -> Dict[str, Any]:
        dt = res.decision_trace.to_dict() if res.decision_trace else {}
        md = res.context.metadata
        open_trigger = _ss.first_open_human_trigger(md)
        hits = [dict(trigger_type=h["trigger_type"], trigger_class=h["trigger_class"],
                     evidence=h["evidence"]) for h in dt.get("triggers", [])]
        primary = res.trigger_type if res.trigger_type != "none" else None
        reply = res.customer_message
        fit_check_used = reply == _be._FIT_CHECK_RESPONSE
        gates_checked = ["trigger_evaluation", "human_hold", "delivery_policy",
                         "identity_disclosure", "loop_guard"]
        gates_checked.append("fit_gate" if fit_check_used or res.fit_confirmed or res.fit_score is not None
                             else "fit_gate(skipped: no fit_criteria passed)")
        gates_fired = [h["trigger_type"] for h in hits]
        if res.human_intervention_open:
            gates_fired.append("human_hold")
        if dt.get("loop_guard_applied"):
            gates_fired.append("loop_guard")
        if fit_check_used:
            gates_fired.append("fit_check_response")
        if res.lead_signals.identity_question:
            gates_fired.append("identity_disclosure")
        return {
            "turn": self.turn_no,
            "user_message": user_message,
            "input_mode": "structured" if structured else "free_text",
            "extraction": {"status": res.interpretation_status, "signals": res.lead_signals.as_dict()},
            "trust_state": res.trust_state.value,
            "mode": res.collaboration_mode.value,
            "mode_reason": dt.get("mode_reason", ""),
            "handoff": {
                "triggered": bool(res.handoff_triggered),
                "queued": bool(res.handoff_queued),
                "intervention_open": bool(res.human_intervention_open),
                "effective": bool(res.handoff_triggered or res.human_intervention_open),
                # stricter reading: a person TAKES OVER (intervention class), vs merely being notified
                "takeover": bool(res.human_intervention_open or any(h["trigger_class"] == "intervention" for h in hits)),
                "trigger": primary or open_trigger,       # primary this turn, else the open intervention's
                "primary_trigger_this_turn": primary,
                "open_intervention_trigger": open_trigger,
                "hits": hits,
                "rep_notified": dt.get("rep_notified"),
                "rep_notified_reason": dt.get("rep_notified_reason"),
            },
            # No qualification layer exists in code (CLAUDE.md roadmap step 6).
            "qualification": {"status": None, "available": False,
                              "fit_confirmed": res.fit_confirmed, "fit_score": res.fit_score},
            "gates": {"checked": gates_checked, "fired": gates_fired},
            "delivery": {"status": res.delivery_status, "outcome": dt.get("outcome"),
                         "response_source": dt.get("response_source"),
                         "loop_guard_applied": bool(dt.get("loop_guard_applied"))},
            "reply": reply,
            "pending_draft": res.pending_draft,
            "rep_suggestion": res.rep_suggestion,
            "state": {"conversation_summary": res.context.conversation_summary,
                      "metadata_keys": sorted(md.keys()), "turn_count": md.get(_ss.KEY_TURN_COUNT)},
            "decision_trace": dt,
        }


def run_turn(history: Sequence[str], user_message: str, *, rep_online: bool = True,
             live_session: bool = False, awaiting_approval: bool = False) -> Dict[str, Any]:
    """Replay `history` (earlier user messages) then run `user_message`; return its trace."""
    s = Session(rep_online=rep_online, live_session=live_session, awaiting_approval=awaiting_approval)
    for m in history:
        s.turn(m)
    return s.turn(user_message)
