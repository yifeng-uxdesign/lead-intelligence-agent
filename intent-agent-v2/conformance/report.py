"""usage: report.py <scored_a.json> [<scored_b.json> ...]  -- side-by-side metrics + group pass counts + failures."""
import json, sys
from collections import defaultdict
from pathlib import Path

runs = [json.loads(Path(p).read_text()) for p in sys.argv[1:]]
names = [r["engine"] for r in runs]
print(f"{'metric':28s}" + "".join(f"{n:>12s}" for n in names))
for k in runs[0]["metrics"]:
    print(f"{k:28s}" + "".join(f"{str(r['metrics'][k]):>12s}" for r in runs))
print("\ngroup pass (passed/judged)")
groups = sorted({c["group"] for r in runs for c in r["cases"]})
for g in groups:
    cells = []
    for r in runs:
        cs = [c for c in r["cases"] if c["group"] == g and c["status"] in ("pass", "fail")]
        cells.append(f"{sum(c['status']=='pass' for c in cs)}/{len(cs)}")
    print(f"{g:28s}" + "".join(f"{c:>12s}" for c in cells))
for r in runs:
    print(f"\n-- {r['engine']} failures")
    for c in r["cases"]:
        if c["status"] != "fail":
            continue
        for t in c["turns"]:
            bad = [d for d, v in t["dims"].items() if v == "fail"]
            if bad:
                print(f"  {c['id']}: {t['u'][:50]!r} fail={bad} got route={t['obs'].get('route')} esc={t['obs'].get('escalation')}")
        if c["repetition"]:
            print(f"  {c['id']}: repetition {c['repetition']}")
