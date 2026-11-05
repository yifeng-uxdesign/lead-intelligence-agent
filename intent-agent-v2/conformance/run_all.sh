#!/usr/bin/env bash
# usage: conformance/run_all.sh <widget_dir> [--record]   (--record overwrites baseline/*.json)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(dirname "$HERE")"
WIDGET="${1:?widget dir}"; mkdir -p "$HERE/results" "$HERE/baseline"
cd "$ROOT"
HASH=$(python3 -c "from conformance.scoring import cases_hash; print(cases_hash())")
python3 conformance/run_backend.py "$HERE/results/backend.obs.json" 2>/dev/null
# throwaway copy so Node treats the widget as ESM without modifying it
TMP=$(mktemp -d); cp -r "$WIDGET"/. "$TMP"; echo '{"type":"module"}' > "$TMP/package.json"
node "$HERE/run_widget.mjs" "$TMP" "$HERE/cases.json" "$HERE/results/widget.obs.json" "$HASH"; rm -rf "$TMP"
python3 conformance/score_observations.py "$HERE/results/backend.obs.json" "$HERE/results/backend.json"
python3 conformance/score_observations.py "$HERE/results/widget.obs.json" "$HERE/results/widget.json" understanding
python3 conformance/report.py "$HERE/results/widget.json" "$HERE/results/backend.json"
if [[ "${2:-}" == "--record" ]]; then
  # the backend baseline covers the understanding layer only (policy is gated at 100% separately)
  python3 conformance/score_observations.py "$HERE/results/backend.obs.json" "$HERE/baseline/backend.json" understanding
  cp "$HERE/results/widget.json" "$HERE/baseline/widget.json"; echo recorded baselines
fi
