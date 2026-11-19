"""Config A eval runner (rules + templates, no LLM). Run: cd evals && PYTHONDONTWRITEBYTECODE=1 python3 -m pytest test_config_a.py

Expected values come from inputs/scenarios_v0.yaml and are never edited here.
Failures are the useful output; the report is built by report_a.py from results/config_a_results.json.
"""
import re

import pytest

import adapter
import checks
import conftest
import mapping
import static_audit

CASES = checks.SCEN["cases"]
PERTS = checks.SCEN["perturbations"]


def _fail_text(records):
    bad = [r for r in records if r["status"] == "fail"]
    return "\n".join(f"  t{r['turn']} {r['layer']}/{r['check']}: expected={r['expected']!r} actual={r['actual']!r}" for r in bad)


@pytest.mark.parametrize("mode", ["free_text", "structured"])
@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_case(case, mode):
    out = checks.run_case(case, mode)
    conftest.RESULTS.extend(out["records"])
    # traces kept for the report's reply excerpts
    conftest.RESULTS.append(dict(case=case["id"], turn=0, input_mode=mode, layer="_trace", check="_trace",
                                 status="info", expected=None,
                                 actual=[dict(turn=t["turn"], user=t["user_message"], reply=t["reply"], mode=t["mode"],
                                              trust=t["trust_state"], trigger=t["handoff"]["trigger"],
                                              effective=t["handoff"]["effective"], src=t["delivery"]["response_source"],
                                              signals=t["extraction"]["signals"]) for t in out["traces"]],
                                 placeholders=[], note=""))
    fails = [r for r in out["records"] if r["status"] == "fail"]
    assert not fails, f"{len(fails)} failed checks in {case['id']} [{mode}]:\n" + _fail_text(out["records"])


@pytest.mark.parametrize("pert", PERTS, ids=[p["id"] for p in PERTS])
@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_perturbation(case, pert):
    out = checks.run_perturbation(case, pert)
    conftest.RESULTS.extend(out["records"])
    fails = [r for r in out["records"] if r["status"] == "fail"]
    assert not fails, f"{case['id']}+{pert['id']}:\n" + _fail_text(out["records"])


def test_static_template_audit():
    a = static_audit.audit()
    conftest.RESULTS.append(dict(case="STATIC", turn=0, input_mode="static", layer="_static", check="_static",
                                 status="info", expected=None, actual=a, placeholders=[], note=""))
    assert not a["hits"], "\n".join(f"{h['invariant']} matches {h['template']}: {h['match']!r}" for h in a["hits"])


def test_static_audit_selftest():
    """The scanner must catch a known-bad string (guards against a silent 0-hit audit)."""
    bad = "Yes, we have SOC 2 certification and it can be live next week for rollout. It costs $500 per month."
    hit = set()
    for inv in static_audit.INVS:
        if inv.get("text_pattern") and re.search(inv["text_pattern"], bad):
            hit.add(inv["id"])
    assert {"INV-NO-CERTIFICATION-CLAIM", "INV-NO-IMPLEMENTATION-COMMITMENT", "INV-NO-PRICE-CLAIM"} <= hit


def test_determinism_and_replay():
    """Config A must be deterministic: two runs and the stateless run_turn(history, msg) agree."""
    for case in CASES:
        users = [t["user"] for t in case["turns"]]
        a = checks.run_case(case, "free_text")["traces"]
        b = checks.run_case(case, "free_text")["traces"]
        for x, y in zip(a, b):
            for k in ("reply", "mode", "trust_state"):
                assert x[k] == y[k], f"nondeterministic {case['id']} t{x['turn']} {k}"
        last = adapter.run_turn(users[:-1], users[-1])
        assert last["reply"] == a[-1]["reply"] and last["mode"] == a[-1]["mode"], f"replay differs {case['id']}"
    conftest.RESULTS.append(dict(case="DETERMINISM", turn=0, input_mode="free_text", layer="_det", check="_det",
                                 status="info", expected=None, actual="no nondeterminism found", placeholders=[], note=""))


def test_every_yaml_placeholder_is_mapped():
    ph = mapping.placeholders_in_yaml(checks.SCEN)
    unknown = [s for s in ph["signals"] if s not in mapping.SIGNALS] + \
              [t for t in ph["triggers"] if t not in mapping.TRIGGERS]
    assert not unknown, f"placeholders missing from mapping.py: {unknown}"
