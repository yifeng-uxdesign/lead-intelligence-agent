"""Report-only: score the backend on conformance/heldout.json (never gates CI).

usage: python3 conformance/run_heldout.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from conformance import run_backend  # noqa: E402
from conformance.scoring import load_cases, score_run  # noqa: E402

HERE = Path(__file__).parent


def main() -> dict:
    doc = load_cases(HERE / "heldout.json")
    obs = {c["id"]: run_backend.observe_case(c) for c in doc["cases"]}
    run = score_run(doc, obs, ("understanding",))
    by_group = Counter()
    passed = Counter()
    for c in run["cases"]:
        by_group[c["group"]] += 1
        passed[c["group"]] += c["status"] == "pass"
    print(f"heldout  {json.dumps(run['metrics'])}")
    for g in sorted(by_group):
        print(f"  {g:28} {passed[g]}/{by_group[g]}")
    for c in run["cases"]:
        if c["status"] == "fail":
            t = c["turns"][-1]
            print(f"  FAIL {c['id']}: {t['u']!r} got esc={t['obs']['escalation']} route={t['obs']['route']}")
    return run


if __name__ == "__main__":
    main()
