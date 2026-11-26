# Eval iterations log

One row per change set, same runner (`test_config_a.py` + `report_a.py`). Snapshots of the raw results live in `evals/iterations/`. Never edit a past row; add a new one. Labels: **from the run** (measured). Classification rules: `REPORT_A.md`.

| Iter | Date | Change (commit) | Failed checks | missing feature | extraction miss | repetition / decision | bad expectation | Case/mode tests passing | Invariant violations | Held-out | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 2026-11-19 | Baseline, no source change (`ec279c3` + eval files) | 146 | 117 | 18 | 7 | 4 | 0 of 12 (+ 18 of 36 perturbation cases pass) | 0 of 82 per mode; static audit 0 of 59 templates | not run | `iterations/iter0_config_a_results.json` |
| 1 | | Rule fixes (human-request phrases, keyword false alarms, follow-up variants) | | | | | | | | | claimed to close: extraction misses and repetition |
| 2 | | handoff_type + terminal outcome in trace | | | | | | | | | no pass-rate change expected |
| 3 | | Qualification spine | | | | | | | | | claimed to close: state layer |
| 4 | | Knowledge router | | | | | | | | | claimed to close: security/pricing turns |

Note on comparability: from iteration 3 on the demo YAML (new file) asserts a smaller, chosen signal set. Always report v0 and the new set side by side.
