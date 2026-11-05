"""usage: score_observations.py <observations.json> <scored.json> [layer,...]"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from conformance.scoring import cases_hash, load_cases, score_run

obs = json.loads(Path(sys.argv[1]).read_text())
layers = tuple(sys.argv[3].split(",")) if len(sys.argv) > 3 else ("understanding", "policy")
if obs["cases_hash"] != cases_hash():
    sys.exit(f"observations are stale (cases hash {obs['cases_hash']} != {cases_hash()}); re-run observers")
run = score_run(load_cases(), obs["observations"], layers)
Path(sys.argv[2]).write_text(json.dumps({"engine": obs["engine"], "cases_hash": obs["cases_hash"], **run}, indent=1))
m = run["metrics"]
print(f"{obs['engine']:8s} " + "  ".join(f"{k}={v}" for k, v in m.items()))
