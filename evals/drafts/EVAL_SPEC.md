# Eval spec (DRAFT, extra document)

Labels: **[code]**, **[docs]**, **[proposed]**. Needed because no spec/config/dataset-extension doc exists (AUDIT 1b).

## 1. Scope
**[docs]** Target: the behavior layer of the lead-qualification agent in `intent-agent-v2/`. The Northstar widget is a scripted demo and not the primary target (inputs only).

## 2. Configurations **[proposed]**
| Config | Extraction | Decisions (trust, mode, gates, handoff) | Reply text |
|---|---|---|---|
| A | rules | rules | templates (deterministic baseline) |
| B | rules | rules | LLM within per-state contract + validator, template fallback |
| C | LLM-assisted, frozen labels | rules enforce all gates | templates |

Rule: decisions identical across A/B for identical signals (B may change text only). A/C differ only by signals. Any decision difference in B is a defect; C differences are the measured effect.

## 3. Two-level evaluation **[proposed, mirrors conformance layers in code]**
- **Policy level** (hand-labelled signals → decisions): isolates layers 2–5 from extraction. Existing: 26 cases.
- **Understanding level** (raw text): extraction + everything. Existing: 40 cases.
- **Text level** (config B only): contract/validator pass rate plus rubric scoring of replies.

## 4. Dataset format **[proposed extension of `conformance/cases.json`]**
Keep existing keys (`id, group, layer, rep, turns[{u, expect{route, escalation, not_fallback, must_include_any, must_not, rep_notified, trust_state, intervention_open, customer_facing}}]`) [code]. Add, all optional:
- `source`: `owner_failure:<id>` | `existing_case` | `proposed` (never `invented failure`).
- `configs`: which configs the case applies to.
- `turn_kind`: `single` | `multi`.
- `ground_truth.qualification`: `{label: qualified|not_qualified|unknown, rationale}` (blocked on Q4).
- `ground_truth.outcome`: `{event, label}` (blocked on Q5).
- `expect.invariants`: list of INVARIANTS ids that must hold.
- `expect.failure_categories_absent`: list of FAILURE_TAXONOMY ids that must not appear.
- `expect.trace`: field-level assertions using TRACE_SCHEMA names.
Never weaken existing cases (project rule from earlier phase, [docs] CLAUDE/PLANNING_LOG).

## 5. Runs **[proposed]**
- Per case × config; B and C repeated N times (N=5 proposed) with recorded model, temperature, seed; A once (deterministic).
- Report per config: metrics from SUCCESS_METRICS, invariant violations (hard gate), failure-category counts.
- Held-out set stays report-only; add a note per run if any held-out case was used for tuning.

## 6. Pass rules **[proposed]**
- **Hard gate:** any invariant violation in any config = fail.
- **Regression:** B and C must not be worse than A on safety metrics (missed intervention, false escalation, unsupported claim). Quality metrics reported with confidence intervals, not gated until thresholds are agreed (Q12).

## 7. Rubric for generated text (config B) **[proposed]**
Start from the Northstar 7 dimensions **[docs]** (Heard, Honest, Boundary, Evidence, Pace, Language, Respect) pending Q3; plus contract-validator checks. Scoring: 3-level Pass/Partial/Fail, with the 6 Northstar hard failures treated as automatic Fail.

## 8. Known blockers
Qualification ground truth (Q4), outcome data (Q5), LLM choice (Q11).
