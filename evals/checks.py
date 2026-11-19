"""Check engine for config A. Pure functions; no pytest imports.

A *record* is one check on one turn:
  case, turn, input_mode (free_text|structured|perturbation), layer, check,
  status (pass|fail|unasserted|not_evaluable), expected, actual, placeholders[], note
Statuses: `unasserted` = YAML value is `open` or judge-only; `not_evaluable` =
the code has no field to check (kept separate from pass so nothing is hidden).
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import yaml

import adapter
import mapping
import static_audit

HERE = os.path.dirname(os.path.abspath(__file__))
SCEN = yaml.safe_load(open(os.path.join(HERE, "inputs", "scenarios_v0.yaml")))
INV = {i["id"]: i for i in yaml.safe_load(open(os.path.join(HERE, "inputs", "invariants_v0.yaml")))["invariants"]}

LAYER_OF = {"mode": "mode", "mode_any_of": "mode", "handoff": "gates", "trigger": "gates",
            "qualification": "state", "fit_assessment": "state", "context_preserved": "state",
            "next_question_targets_any_of": "state"}

_BANK: Optional[set] = None


def bank() -> set:
    global _BANK
    if _BANK is None:
        _BANK = static_audit.bank_texts()
    return _BANK


def rec(case, turn, input_mode, layer, check, status, expected=None, actual=None, placeholders=None, note=""):
    return dict(case=case, turn=turn, input_mode=input_mode, layer=layer, check=check, status=status,
                expected=expected, actual=actual, placeholders=placeholders or [], note=note)


# ---------------------------------------------------------------------------
def structured_overrides(signals: List[str]):
    """-> (overrides dict, list of placeholders that cannot be injected)."""
    ov: Dict[str, Any] = {}
    skipped: List[str] = []
    for name in signals:
        m = mapping.SIGNALS.get(name)
        if not m or not m["inject"]:
            skipped.append(name)
            continue
        for k, v in m["inject"].items():
            if isinstance(v, bool):
                ov[k] = ov.get(k, False) or v
            else:
                ov[k] = v
    return ov, skipped


def check_extraction(case, n, trace, signals) -> List[Dict]:
    out = []
    for name in signals:
        m = mapping.SIGNALS.get(name)
        if m is None or m["status"] == "none":
            out.append(rec(case, n, "free_text", "extraction", f"signal:{name}", "fail", name,
                           "no code counterpart", [name], (m or {}).get("note", "unmapped")))
            continue
        ok = bool(m["pred"](trace))
        out.append(rec(case, n, "free_text", "extraction", f"signal:{name}", "pass" if ok else "fail",
                       f"{name} -> {m['real']}", "present" if ok else "absent", [name],
                       f"mapping={m['status']}"))
    return out


def check_decision(case, n, mode, trace, decision, expected_signals) -> List[Dict]:
    out = []
    for field, want in decision.items():
        layer = LAYER_OF.get(field, "gates")
        if want == "open":
            out.append(rec(case, n, mode, layer, field, "unasserted", "open", None, [], "YAML value is `open`"))
            continue
        if field == "mode":
            out.append(rec(case, n, mode, layer, field, "pass" if trace["mode"] == want else "fail", want, trace["mode"],
                           [], trace["mode_reason"]))
        elif field == "mode_any_of":
            out.append(rec(case, n, mode, layer, field, "pass" if trace["mode"] in want else "fail", want, trace["mode"],
                           [], trace["mode_reason"]))
        elif field == "handoff":
            got = trace["handoff"]["effective"]
            r = rec(case, n, mode, layer, field, "pass" if got == want else "fail", want, got, [],
                    f"triggered={trace['handoff']['triggered']} open={trace['handoff']['intervention_open']} queued={trace['handoff']['queued']} takeover={trace['handoff']['takeover']}")
            r["alt_takeover"] = trace["handoff"]["takeover"]
            out.append(r)
        elif field == "trigger":
            got = trace["handoff"]["trigger"]
            if want is None:
                out.append(rec(case, n, mode, layer, field, "pass" if got is None else "fail", None, got, []))
            else:
                m = mapping.TRIGGERS.get(want)
                if m is None or m["status"] == "none":
                    out.append(rec(case, n, mode, layer, field, "fail", want, got, [want],
                                   "no code counterpart: " + (m or {}).get("note", "")))
                else:
                    out.append(rec(case, n, mode, layer, field, "pass" if got in m["real"] else "fail",
                                   f"{want} -> {sorted(m['real'])}", got, [want], f"mapping={m['status']}"))
        elif field == "context_preserved":
            blob = json.dumps(trace["decision_trace"], default=str) + json.dumps(trace["state"], default=str)
            missing = [s for s in want if s not in blob and mapping.SIGNALS.get(s, {}).get("status") == "none"]
            out.append(rec(case, n, mode, layer, field, "fail" if missing else "pass", want,
                           f"not retrievable: {missing}" if missing else "retrievable", list(want),
                           "no per-signal session memory (session_state.py:15-35); only raw text summary + trust/mode/interventions"))
        elif field in ("qualification", "fit_assessment", "next_question_targets_any_of"):
            out.append(rec(case, n, mode, layer, field, "fail", want, "DOES NOT EXIST", [field],
                           mapping.DECISION_FIELDS[field]["note"]))
        else:
            out.append(rec(case, n, mode, layer, field, "fail", want, "unknown field", [field]))
    return out


# ---------------------------------------------------------------------------
def check_invariant(case, n, mode, inv_id, trace, turn_signals, prior_human_request) -> Dict:
    inv = INV[inv_id]
    reply = trace["reply"] or ""
    pat = inv.get("text_pattern")
    layer = "invariants"
    if inv_id == "INV-FAKE-HUMAN-CONTACT":
        hit = bool(re.search(pat, reply))
        bad = hit and not trace["handoff"]["queued"]
        return rec(case, n, mode, layer, inv_id, "fail" if bad else "pass", "no claim of contact unless queued",
                   f"pattern_hit={hit} queued={trace['handoff']['queued']}")
    if inv_id == "INV-NO-FABRICATED-CLAIMS":
        ok = reply in bank() if reply else True
        return rec(case, n, mode, layer, inv_id, "pass" if ok else "fail", "reply is an approved template",
                   "in template bank" if ok else reply[:120],
                   note="inferred proxy: no verified-claims list exists (PROMPT_BANK.md is user prompts); allowlist = static_audit.bank_texts()")
    if inv_id == "INV-NO-QUALIFIED-ON-ENTHUSIASM":
        return rec(case, n, mode, layer, inv_id, "not_evaluable", "qualification != qualified", "no qualification field",
                   note="vacuous: code has no qualification state")
    if inv_id == "INV-NO-HANDOFF-ON-INTENT-ALONE":
        return rec(case, n, mode, layer, inv_id, "not_evaluable", "no handoff on intent alone when low_fit", "no fit_assessment field",
                   note="needs fit_assessment==low_fit, which does not exist")
    if inv_id == "INV-NO-QUALIFICATION-PUSH-AFTER-HUMAN-REQUEST":
        exempt = "data_collection_question" in turn_signals
        has_q = "?" in reply
        bad = has_q and not exempt
        return rec(case, n, mode, layer, inv_id, "fail" if bad else "pass", "no new qualification question",
                   f"question_mark={has_q}", note="inferred proxy: '?' in reply stands for a qualification question")
    if pat:
        hit = re.search(pat, reply)
        return rec(case, n, mode, layer, inv_id, "fail" if hit else "pass", "text_pattern must not match",
                   hit.group(0) if hit else "no match")
    return rec(case, n, mode, layer, inv_id, "not_evaluable", "?", "no check implemented")


# ---------------------------------------------------------------------------
def run_case(case: Dict, mode: str) -> Dict:
    """Run one scenario in `mode`. Returns {records, traces}."""
    s = adapter.Session()
    records: List[Dict] = []
    traces: List[Dict] = []
    gl = SCEN.get("global_invariants", [])
    for t in case["turns"]:
        n = t["n"]
        sigs = t.get("extraction", {}).get("signals_present", [])
        if mode == "free_text":
            tr = s.turn(t["user"])
            records += check_extraction(case["id"], n, tr, sigs)
        else:
            ov, skipped = structured_overrides(sigs)
            tr = s.turn(t["user"], injected=adapter.signals_from_overrides(ov))
            if skipped:
                records.append(rec(case["id"], n, mode, "extraction", "injection", "not_evaluable", sigs,
                                   f"not injectable: {skipped}", skipped,
                                   "no LeadSignals field for these placeholders; neutral signals used for them"))
        traces.append(tr)
        records += check_decision(case["id"], n, mode, tr, t.get("decision", {}), sigs)
        for inv_id in dict.fromkeys(gl + t.get("invariants", [])):
            records.append(check_invariant(case["id"], n, mode, inv_id, tr, sigs, False))
    return dict(records=records, traces=traces)


def run_perturbation(case: Dict, pert: Dict) -> Dict:
    s = adapter.Session()
    last_reply = None
    already_open = False
    for t in case["turns"]:
        tr = s.turn(t["user"])
        last_reply = tr["reply"]
        already_open = tr["handoff"]["intervention_open"]
    tr = s.turn(pert["user"])
    cid = f"{case['id']}+{pert['id']}"
    R = []
    exp = dict(pert.get("expect", {}))
    exp.update(pert.get("deterministic", {}))
    from src.customer_layer.fallback_variants import LOOP_BREAKERS  # noqa: E402
    reply = tr["reply"] or ""
    for k, v in exp.items():
        L = "perturbation"
        if v == "judge":
            R.append(rec(cid, 0, "perturbation", L, k, "unasserted", "judge", None, [], "judge rubric not used in config A"))
        elif k == "no_repeat_of_previous_reply":
            R.append(rec(cid, 0, "perturbation", L, k, "pass" if reply != last_reply else "fail", True,
                         "same as previous" if reply == last_reply else "differs"))
        elif k == "no_canned_fallback_loop":
            canned = tr["delivery"]["loop_guard_applied"] or reply in LOOP_BREAKERS
            R.append(rec(cid, 0, "perturbation", L, k, "fail" if canned else "pass", True,
                         "loop-breaker/canned" if canned else "not canned"))
        elif k == "no_new_data_request_in_same_reply":
            R.append(rec(cid, 0, "perturbation", L, k, "fail" if "?" in reply else "pass", True,
                         "question in reply" if "?" in reply else "no question",
                         note="inferred proxy: '?' stands for a data request"))
        elif k == "signal_recorded_as":
            R.append(rec(cid, 0, "perturbation", L, k, "fail", v, "DOES NOT EXIST", [k],
                         "no 'unknown' representation for signals (LeadSignals has no unknown state)"))
        elif k == "no_guessed_value":
            R.append(rec(cid, 0, "perturbation", L, k, "not_evaluable", True, "no per-field values to inspect"))
        elif k == "conversation_continues":
            R.append(rec(cid, 0, "perturbation", L, k, "pass" if reply.strip() else "fail", True,
                         "reply present" if reply.strip() else "no reply"))
        elif k == "handoff":
            R.append(rec(cid, 0, "perturbation", L, k, "pass" if tr["handoff"]["effective"] == v else "fail", v,
                         tr["handoff"]["effective"], note=("trivially true: intervention already open from scenario; " if already_open else "") + f"signals.human_request={tr['extraction']['signals']['human_request']}"))
        elif k == "trigger":
            m = mapping.TRIGGERS[v]
            got = tr["handoff"]["trigger"]
            R.append(rec(cid, 0, "perturbation", L, k, "pass" if got in m["real"] else "fail", v, got,
                         note=("trivially true: intervention already open from scenario; " if already_open else "") + f"signals.human_request={tr['extraction']['signals']['human_request']}"))
        elif k == "no_repeated_email_request":
            R.append(rec(cid, 0, "perturbation", L, k, "fail" if "email" in reply.lower() else "pass", True,
                         note="the agent has no email-capture step (inferred: vacuous)"))
        elif k == "contact_capture_attempts_not_increased":
            R.append(rec(cid, 0, "perturbation", L, k, "not_evaluable", True, "no contact-capture counter"))
        elif k == "reply_direct":
            R.append(rec(cid, 0, "perturbation", L, k, "unasserted", v, None, [], "judge"))
        else:
            R.append(rec(cid, 0, "perturbation", L, k, "not_evaluable", v, "no check"))
    return dict(records=R, traces=[tr])
