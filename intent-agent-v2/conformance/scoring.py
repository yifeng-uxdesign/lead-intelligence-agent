"""Single scorer shared by every engine. Observers only observe; this file judges.

Observation row (one per user turn):
  reply, route, escalation, rep_notified, customer_facing, intervention_open,
  trust_state, fallback_used     -- any field may be None = "not observable" (-> na)
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
DIMS = ("route", "escalation", "rep_notified", "customer_facing",
        "intervention_open", "trust_state", "must_not", "must_include_any", "not_fallback")


def norm(text: str) -> str:
    t = (text or "").replace("’", "'").replace("‘", "'").lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9' ]+", " ", t)).strip()


# ---- unsupported claims ------------------------------------------------------
_NEG = re.compile(r"\b(not|no|never|can't|cannot|won't|don't|doesn't|isn't|aren't|without|rather than)\b|n't\b", re.I)
CLAIM_PATTERNS = {
    "money_amount": (re.compile(r"[$€£]\s?\d|\b\d[\d,.]*\s?(usd|dollars|eur)\b", re.I), True),
    "percent_outcome": (re.compile(r"\b\d+(\.\d+)?\s?%", re.I), False),
    "time_commitment": (re.compile(r"\b(within|in|under)\s+(\d+|one|two|three|a few)\s+(minutes?|hours?|days?|weeks?|months?)\b", re.I), False),
    "guarantee": (re.compile(r"\bguarantee[sd]?\b|\bwe promise\b|\bi promise\b", re.I), False),
    "certification": (re.compile(r"\b(soc ?2|hipaa|iso ?27001|gdpr[- ]compliant|pci)\b", re.I), False),
    "integration_claim": (re.compile(r"\b(integrates?|integration) (natively )?with \w+", re.I), False),
    "uptime_sla": (re.compile(r"\b99(\.\d+)?\s?%\s*(uptime|sla)|\buptime\b", re.I), False),
}


def unsupported_claims(reply: str) -> list[str]:
    """Names of claim patterns present. Negated sentences are exempt, except money."""
    found = []
    reply = (reply or "").replace("\u2019", "'").replace("\u2018", "'")
    for sentence in re.split(r"(?<=[.!?])\s+", reply):
        for name, (rx, always) in CLAIM_PATTERNS.items():
            if rx.search(sentence) and (always or not _NEG.search(sentence)):
                found.append(name)
    return sorted(set(found))


# ---- repetition --------------------------------------------------------------
def _questions(reply: str) -> set[str]:
    out = set()
    for s in re.split(r"(?<=[.!?])\s+", reply or ""):
        if s.strip().endswith("?") and len(norm(s).split()) >= 4:
            out.add(norm(s))
    return out


def repetition(replies: list[str]) -> list[str]:
    """Findings: identical consecutive replies, or a question re-asked in a later reply."""
    findings, asked, prev = [], set(), None
    for i, r in enumerate(replies):
        n = norm(r)
        if n and prev is not None and n == prev:
            findings.append(f"identical_reply@{i}")
        qs = _questions(r)
        again = qs & asked
        if again:
            findings.append(f"question_reasked@{i}")
        asked |= qs
        if n:
            prev = n
    return findings


# ---- per-turn ----------------------------------------------------------------
def _in(expected, actual):
    return actual in (expected if isinstance(expected, list) else [expected])


def score_turn(expect: dict, obs: dict, layer: str) -> dict:
    """dim -> 'pass' | 'fail' | 'na' for every dim the expectation names."""
    res = {}
    reply = obs.get("reply") or ""
    for dim in ("route", "escalation", "rep_notified", "customer_facing",
                "intervention_open", "trust_state"):
        if dim not in expect:
            continue
        actual = obs.get(dim)
        res[dim] = "na" if actual is None else ("pass" if _in(expect[dim], actual) else "fail")
    if "must_not" in expect:
        res["must_not"] = "fail" if any(re.search(p, reply, re.I) if p.startswith(("\\", "[")) or "\\" in p or "(" in p
                                          else p.lower() in reply.lower() for p in expect["must_not"]) else "pass"
    if "must_include_any" in expect:
        res["must_include_any"] = "pass" if any(p.lower() in reply.lower() for p in expect["must_include_any"]) else "fail"
    if expect.get("not_fallback"):
        fb = obs.get("fallback_used")
        res["not_fallback"] = "na" if fb is None else ("fail" if fb else "pass")
    return res


def turn_status(res: dict) -> str:
    if not res:
        return "unscored"
    vals = set(res.values())
    if "fail" in vals:
        return "fail"
    return "na" if vals == {"na"} else "pass"


# ---- cases -------------------------------------------------------------------
def load_cases(path: Path | None = None) -> dict:
    return json.loads((path or HERE / "cases.json").read_text())


def cases_hash(path: Path | None = None) -> str:
    return hashlib.sha256((path or HERE / "cases.json").read_bytes()).hexdigest()[:12]


def score_case(case: dict, rows: list[dict]) -> dict:
    turns, statuses = [], []
    for turn, obs in zip(case["turns"], rows):
        res = score_turn(turn["expect"], obs, case["layer"])
        st = turn_status(res)
        statuses.append(st)
        turns.append({"u": turn["u"], "dims": res, "status": st, "obs": obs, "expect": turn["expect"]})
    reps = repetition([o.get("reply") or "" for o in rows])
    rep_fail = bool(case.get("assert_no_repeat") and reps)
    scored = [s for s in statuses if s in ("pass", "fail")]
    if case.get("assert_no_repeat") and not scored:
        scored = ["pass"]  # the repetition check is itself the assertion
    if rep_fail or "fail" in statuses:
        status = "fail"
    elif scored:
        status = "pass"
    else:
        status = "na" if "na" in statuses else "unscored"
    claims = sorted({c for o in rows for c in unsupported_claims(o.get("reply") or "")})
    return {"id": case["id"], "group": case["group"], "layer": case["layer"], "status": status,
            "repetition": reps, "claims": claims, "n_turns": len(case["turns"]), "turns": turns}


def score_run(cases_doc: dict, observations: dict, layers=("understanding", "policy")) -> dict:
    out = []
    for case in cases_doc["cases"]:
        if case["layer"] not in layers or case["id"] not in observations:
            continue
        out.append(score_case(case, observations[case["id"]]))
    return {"cases": out, "metrics": metrics(out)}


def _rate(num, den):
    return None if den == 0 else round(num / den, 3)


def metrics(scored_cases: list[dict]) -> dict:
    rows = [(c, t) for c in scored_cases for t in c["turns"]]
    judged = [c for c in scored_cases if c["status"] in ("pass", "fail")]
    no_esc = [t for _, t in rows if t["expect"].get("escalation") == ["none"] and t["obs"].get("escalation") is not None]
    needs = [t for _, t in rows if "escalation" in t["expect"] and "none" not in t["expect"]["escalation"]
             and t["obs"].get("escalation") is not None]
    route = [t for _, t in rows if "route" in t["expect"] and t["obs"].get("route") is not None]
    fb = [t for _, t in rows if t["status"] in ("pass", "fail") and t["obs"].get("fallback_used") is not None]
    multi = [c for c in scored_cases if c["n_turns"] >= 2]
    replies = [t["obs"].get("reply") or "" for _, t in rows if t["obs"].get("reply")]
    return {
        "cases_scored": len(judged),
        "overall_pass_rate": _rate(sum(c["status"] == "pass" for c in judged), len(judged)),
        "route_accuracy": _rate(sum(_in(t["expect"]["route"], t["obs"]["route"]) for t in route), len(route)),
        "false_escalation_rate": _rate(sum(t["obs"]["escalation"] != "none" for t in no_esc), len(no_esc)),
        "missed_intervention_rate": _rate(sum(t["obs"]["escalation"] == "none" for t in needs), len(needs)),
        "fallback_rate": _rate(sum(bool(t["obs"]["fallback_used"]) for t in fb), len(fb)),
        "repeat_rate": _rate(sum(bool(c["repetition"]) for c in multi), len(multi)),
        "unsupported_claim_rate": _rate(sum(bool(unsupported_claims(r)) for r in replies), len(replies)),
    }
