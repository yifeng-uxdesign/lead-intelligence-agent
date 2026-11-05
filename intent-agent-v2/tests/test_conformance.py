"""Conformance suite wired into pytest.

Policy layer (hand-labeled signals): must reach 100%. Cases the backend is KNOWN to fail are
listed in conformance/known_gaps.json and run as strict xfail, tied to the roadmap step that
fixes them. Understanding layer: the rule-based backend may not regress below the recorded
baseline (the bar the LLM interpreter must later beat).
"""
import json
from pathlib import Path

import pytest

from conformance import run_backend
from conformance.scoring import (cases_hash, load_cases, norm, repetition, score_case,
                                 score_run, score_turn, unsupported_claims)
from src.domain.trigger_catalog import HandoffTriggerType

CONF = Path(__file__).resolve().parent.parent / "conformance"
DOC = load_cases()
GAPS = {k: v for k, v in json.loads((CONF / "known_gaps.json").read_text()).items() if not k.startswith("_")}
TAX = json.loads((CONF / "taxonomy.json").read_text())
POLICY = [c for c in DOC["cases"] if c["layer"] == "policy"]
UNDERSTANDING = [c for c in DOC["cases"] if c["layer"] == "understanding"]


def _score(case):
    return score_case(case, run_backend.observe_case(case))


@pytest.mark.parametrize("case", POLICY, ids=[c["id"] for c in POLICY])
def test_policy_case(case, request):
    if case["id"] in GAPS:
        request.applymarker(pytest.mark.xfail(strict=True, reason=f"step {GAPS[case['id']]['step']}: {GAPS[case['id']]['reason']}"))
    scored = _score(case)
    assert scored["status"] == "pass", [(t["u"], t["dims"], t["obs"]) for t in scored["turns"] if t["status"] == "fail"] or scored["repetition"]


def test_known_gaps_registry_is_valid():
    ids = {c["id"] for c in POLICY}
    assert set(GAPS) <= ids
    for k, v in GAPS.items():
        assert v["step"] in (3, 4) and v["reason"], k


def test_baseline_is_not_stale():
    for name in ("backend", "widget"):
        assert json.loads((CONF / "baseline" / f"{name}.json").read_text())["cases_hash"] == cases_hash()


def test_backend_understanding_does_not_regress():
    base = json.loads((CONF / "baseline" / "backend.json").read_text())["metrics"]
    obs = {c["id"]: run_backend.observe_case(c) for c in UNDERSTANDING}
    now = score_run(DOC, obs, ("understanding",))["metrics"]
    assert now["overall_pass_rate"] >= base["overall_pass_rate"]
    assert now["route_accuracy"] >= base["route_accuracy"]
    for worse in ("false_escalation_rate", "missed_intervention_rate", "fallback_rate", "repeat_rate", "unsupported_claim_rate"):
        assert now[worse] <= base[worse], worse


def test_observer_is_deterministic():
    c = next(c for c in DOC["cases"] if c["id"] == "P4-frustrated")
    assert run_backend.observe_case(c) == run_backend.observe_case(c)


def test_derive_route_covers_every_trigger_type():
    from types import SimpleNamespace
    from src.signals.extractor import LeadSignalExtractor
    sig = LeadSignalExtractor().extract("hello")
    routes = {run_backend.derive_route(SimpleNamespace(trigger_type=t.value), sig) for t in HandoffTriggerType}
    assert {"human", "frustration_agent", "pricing", "buying", "compare", "stakeholder", "none"} <= routes


def test_case_vocabulary_matches_taxonomy():
    labels, esc = set(TAX["routes"]["labels"]), set(TAX["escalation"]["values"])
    facing = set(TAX["customer_facing"]["values"])
    for c in DOC["cases"]:
        for t in c["turns"]:
            e = t["expect"]
            for r in ([e["route"]] if isinstance(e.get("route"), str) else e.get("route", [])):
                assert r in labels, (c["id"], r)
            for x in e.get("escalation", []):
                assert x in esc, (c["id"], x)
            for x in ([e["customer_facing"]] if isinstance(e.get("customer_facing"), str) else e.get("customer_facing", [])):
                assert x in facing, (c["id"], x)


def test_cases_cover_personas_and_the_three_issues():
    ids = {c["id"].split("-")[0] for c in DOC["cases"]}
    assert {f"P{i}" for i in (1, 2, 3, 4, 5, 7)} <= ids and {"P6a", "P6b"} <= ids
    groups = {c["group"] for c in DOC["cases"]}
    assert {"issue1_frustration_target", "issue2_accountability", "issue3_nuance", "policy"} <= groups
    assert all(not t["expect"].get("customer_facing") for c in UNDERSTANDING for t in c["turns"])


# --- scorer unit tests --------------------------------------------------------
def test_claims_money_always_flagged_but_negated_percent_exempt():
    assert unsupported_claims("It costs $500 a month, not more.") == ["money_amount"]
    assert unsupported_claims("I can’t promise a 30% lift.") == []
    assert unsupported_claims("We guarantee a 30% lift.") == ["guarantee", "percent_outcome"]


def test_repetition_detects_identical_and_reasked_questions():
    assert repetition(["Hello there.", "Hello there."]) == ["identical_reply@1"]
    assert repetition(["How many leads do you get?", "Thanks. How many leads do you get?"]) == ["question_reasked@1"]
    assert repetition(["One.", "Two."]) == []


def test_na_when_dimension_unobservable():
    r = score_turn({"rep_notified": True, "route": "human"}, {"reply": "x", "route": "human", "rep_notified": None}, "understanding")
    assert r == {"route": "pass", "rep_notified": "na"}
    assert norm("It’s  OK!") == "it's ok"
