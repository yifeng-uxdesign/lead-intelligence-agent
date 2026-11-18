# Eval setup audit — behavior layer (DRAFT)

Status: draft for owner review. Nothing in `intent-agent-v2/` or `northstar/` was modified; everything here is new, under `evals/drafts/`.

**Label key.** Every statement carries one label: **[code]** from code (file:line cited), **[docs]** from your docs, **[failures]** from your failure list, **[proposed]** my proposal, not yet agreed. Anything I could not resolve is in *Open Questions* (end of file) and not guessed.

Repo root `/home/user/lead-intelligence-agent`; backend `intent-agent-v2/` (cited as `v2/`). Companion drafts: `LAYER_MAP.md`, `EVAL_SPEC.md`, `SUCCESS_METRICS.md`, `INVARIANTS.md`, `FAILURE_TAXONOMY.md`, `TRACE_SCHEMA.md`.

---

## 0. Where the material actually is

- **[code]** `evals/` and `evals/inputs/` did not exist before this task. The "existing eval material is in evals/inputs/" list was an unfilled placeholder, so nothing was read from there. (Open Question Q1.)
- **[code]** Eval-like material lives in four places: `v2/conformance/` (harness, 66 cases, taxonomy, known gaps, held-out set, baselines), `v2/tests/` (pytest suite, 307 tests collected; plus `.md` test docs), `northstar/` (`EVALUATION_PLAN.md`, `eval/scenarios.json`, `FAILURE_LIST.md`), and `v2/CLAUDE.md` / `v2/src/core/soul.md` (rules).
- **[docs]** Your failure list: the only failure list in the repo is `northstar/FAILURE_LIST.md`. Part 1 (F1–F9) records your feedback from two Northstar widget test rounds; Part 2 (R1–R11) was found by me, not you. I treat F1–F9 as your input and R1–R11 as unconfirmed. (Q2.)

## 1(a). What exists, per document, and what it covers

| Doc / asset | Label | Covers | Does not cover |
|---|---|---|---|
| `v2/CLAUDE.md` | [code]/[docs] | Architecture rule: deterministic Python owns decisions; LLM only interprets into frozen labels or phrases within a contract, checked by a validator (CLAUDE.md:5–8). Trigger rules, modes, roadmap | No eval spec, no config A/B/C |
| `v2/src/core/soul.md` | [docs] | 7 values; "will not do" list (l.123); behavior guardrails Always/Never (l.183–212); conflict hierarchy (l.167) | Not machine-checkable; no thresholds |
| `v2/conformance/cases.json` | [code] | 66 cases: 26 `policy` (hand-labelled signals) + 40 `understanding` (raw text); groups: policy 26, issue1_frustration_target 8, issue3_nuance 8, persona 8, issue2_accountability 7, human_and_identity 7, loops_and_memory 2. Expect keys: `route, escalation, not_fallback, must_include_any, must_not, rep_notified, trust_state, intervention_open, customer_facing` | Fit/qualification, pipeline outcome, free text quality; multi-turn is only a few cases |
| `v2/conformance/taxonomy.json`, `known_gaps.json` | [code] | Frozen label set; strict-xfail known gaps tied to roadmap steps (POL-20/21/26 in the file) | — |
| `v2/conformance/heldout.json` + `run_heldout.py` | [code] | 22 report-only cases (same-author caveat) | Not a gate |
| `v2/conformance/scoring.py`, observers | [code] | Metrics: overall_pass_rate, route_accuracy, false_escalation_rate, missed_intervention_rate, fallback_rate, repeat_rate, unsupported_claim_rate. Route is derived in the observer, not emitted by the system; "fallback" is defined differently per engine | Fit score, handoff quality, latency/cost, outcome metrics |
| `v2/conformance/baseline/*.json` | [code] | Recorded baselines: backend pass 0.35, widget 0.575 | Not re-recorded after the pacing change (reported earlier) |
| `v2/tests/*.py` (307) | [code] | Unit/behavior tests per FSM, delivery matrix, triggers/trace, soul compliance, API leaks | Not an eval set; no scoring |
| `v2/tests/TEST_PLAN.md`, `PERSONA_SCRIPTS.md` (P1–P6), `PROMPT_BANK.md` (28 "EXTRACTOR LIMIT" tags), `REP_SCRIPTS.md` | [docs] | Test intent, persona scripts, prompt bank | Stale in places (see 1c) |
| `northstar/EVALUATION_PLAN.md` | [docs] | Rubric: 7 dimensions (Heard/Honest/Boundary/Evidence/Pace/Language/Respect), 6 hard failures, verdicts Pass/Partial/Fail; scenarios S1–S6, S10, S11; 6 interruptions; baselines | Widget only; qualitative, human-scored |
| `northstar/eval/scenarios.json` | [docs] | Scenario data for the widget | — |
| `northstar/FAILURE_LIST.md` | [docs] | F1–F9 (yours), R1–R11 (mine) | Widget-focused; none yet for the backend layers |
| `northstar/KNOWLEDGE_BASE.md` | [docs] | 14 draft answers (K01–K15), "known unknowns" table; all `draft`, not approved | — |
| `v2/src/domain/message_schema.yaml` | [code] | Message types + global rules (chips non-binding, ≤3 chips, no pressure language, rep notes never customer-facing) | — |

## 1(b). What a complete eval setup needs, vs. what exists

| Need | Status | Evidence |
|---|---|---|
| Spec (what is evaluated, configs, inputs/outputs, pass rules) | **Missing** | No doc defines configs A/B/C. Drafted: `EVAL_SPEC.md` [proposed] |
| Success metrics (session-level success, lead-qual performance, pipeline impact) | **Partial** | Routing/safety metrics exist in `scoring.py` [code]; no fit/qualification metric: `fit_criteria=None` in `conformance/run_backend.py:92` [code]; no pipeline-impact data model [code]. Drafted: `SUCCESS_METRICS.md` |
| Failure taxonomy | **Partial** | `taxonomy.json` labels are *route* labels, not failure categories [code]; Northstar F1–F9 exist but are widget-level [docs]. Drafted: `FAILURE_TAXONOMY.md` |
| Dataset format | **Partial** | `cases.json` has a usable per-turn `expect` schema [code]; no fields for config, fit/qualification ground truth, outcome labels, or reply-text rubric. Proposed extension in `EVAL_SPEC.md` |
| Rubrics | **Partial** | Human rubric exists for the widget (EVALUATION_PLAN) [docs]; none for backend generated text (config B) or extraction (config C) |
| Trace schema | **Partial** | `DecisionTrace` exists (`v2/src/domain/decision_trace.py`) with turn, interpretation_status, signals, triggers, primary_trigger/class, intervention_*, rep_notified(+reason), mode(+reason), delivery_status(+reason), response_source, outcome, fit_confirmed, loop_guard_applied [code]. Missing: trust state, fit score/inputs, per-layer owner/source, generated text + contract id, validator result, LLM call metadata [code: absent]. Drafted: `TRACE_SCHEMA.md` |
| Invariants | **Partial** | Stated in prose in soul.md, `message_schema.yaml`, trigger catalog; only some are tested. Drafted: `INVARIANTS.md` |
| Held-out / contamination control | **Partial** | 22 held-out cases, report-only, same author [code] | 
| Ground truth for qualification / outcomes | **Missing** | No labelled "qualified lead" or deal outcome anywhere [code]; (Q4, Q5) |
| Run/compare harness across configs | **Missing** | Harness runs one backend; no config switch exists since no LLM code exists |

## 1(c). Contradictions and gaps (docs vs code, docs vs docs)

1. **Trust FSM COMMITMENT without a buying signal.** [code] From DECISION_READY the FSM moves to COMMITMENT unless `objection` or `urgency == "low"`; `strong_buying_signal` is read but not checked on that path (`v2/src/customer_layer/trust_state_machine.py:56–60`). [docs] soul.md:197 says "Never … Move to COMMITMENT from DECISION_READY without a positive buying signal". → Contradiction; becomes an invariant (INV-12). Not asserted to be a bug in production: whether a caller guarantees the signal elsewhere is unverified (Q8).
2. **Fit threshold `>` vs `>=`.** [code] `evaluate_fit` docstring says `>` (`v2/src/clients/sierra/fit_criteria.py:407`); `fit_summary` uses `>=` (l.476). Boundary behaviour is ambiguous (Q9).
3. **Fit uses only the current message.** [code] Fit is computed from the current turn's signals and all hard disqualifiers are hard-wired False (`v2/src/orchestrator.py:77–116`). No budget/timeline/authority/volume fields exist in `LeadSignals` [code]. [docs] Northstar ICP/accept criteria (budget, timeline, five readiness fields, five hard disqualifiers) are described in `PLANNING_LOG.md` and `northstar/ICP_DRAFT.md` but have no counterpart in the backend. → Qualification cannot currently be evaluated on the backend.
4. **Default client config.** [code] `fit_criteria.py` / `product_context.md` are for Sierra; Northstar default has empty criteria (CLAUDE.md roadmap step 6). `TEST_PLAN.md` still says "Sierra AI" [docs].
5. **Test counts.** [docs] TEST_PLAN says 30 unit / 20 behavior tests; [code] repo has 307.
6. **Missing artifact.** [docs] TEST_PLAN.md refers to an "extractor gap log" (l.28, 554, 737, 841, 849–853); [code] no such file exists.
7. **Dead code.** [code] `v2/src/customer_layer/response_policy.py` (`ResponsePolicy`, uses "low_trust/high_trust" vocabulary) is not part of the pipeline.
8. **LLM claimed, none present.** [code] The extractor/adapter docstrings and `requirements.txt:17–21` mention an LLM only as a future plug-in; `holding_responses.py:15–16` says holding copy must stay static. No LLM call exists anywhere → configs B and C require new code (`LAYER_MAP.md`).
9. **Handoff copy vs must_not.** [code] `behavior_engine.py:34–37` `_HANDOFF_BRIDGE_TEMPLATE` begins "Let me connect you with…"; [code] several `cases.json` cases list `"let me connect you"` in `must_not` (e.g. lines 944, 963, 1167, 1458, 1487). Which situations each applies to is not yet checked. (Q10)
10. **Unresolved TODO.** [code] `v2/src/rep_layer/rep_assist_engine.py:21–25` leaves frustration-action consistency unresolved; soul.md:211 says "Never: Trigger frustration action without immediately escalating to rep alert".
11. **Route is not emitted.** [code] Route is derived in the conformance observer, so "route_accuracy" measures the observer's mapping as well as the system. Trace has no `route` field (see `TRACE_SCHEMA.md`).
12. **Fallback means different things.** [code] Per-engine definitions; the earlier fallback_rate drop was a measurement artifact (reported earlier). Cross-config comparisons need one definition.
13. **Widget vs backend scope.** [docs] Northstar widget is a scripted JS demo (not the target). Its rubric and failure list are usable as *inputs* but their pass/fail can't be applied to the backend without a mapping (Q3).
14. **Held-out set is same-author.** [code] Caveat stated in the set itself; report-only.
15. **Stopgap in orchestrator.** [code] `NOTICE_TOPIC_PHRASES` marked STOPGAP (`orchestrator.py:232–244`); a keyword list sits in the decision path.

## 2. Layer map and LLM boundary

See `LAYER_MAP.md`.

## 3. Drafts produced

`EVAL_SPEC.md`, `SUCCESS_METRICS.md`, `INVARIANTS.md`, `FAILURE_TAXONOMY.md`, `TRACE_SCHEMA.md`, `LAYER_MAP.md`. Extra doc beyond your list: `EVAL_SPEC.md`, because the audit shows no spec, config definition or dataset-extension format exists [proposed].

---

## Open Questions (for you to answer)

- **Q1.** `evals/inputs/` does not exist and the file list was blank. Which files are the canonical inputs? Should I copy/index them into `evals/inputs/` (copy only, originals untouched)?
- **Q2.** Is `northstar/FAILURE_LIST.md` F1–F9 the whole of "my failure list", or is there another list (e.g. for the backend)? R1–R11 are mine: may they be used as taxonomy input, or must they be excluded?
- **Q3.** Is the Northstar rubric (7 dimensions, 6 hard failures) to be reused for the backend's generated text in config B, or replaced?
- **Q4.** What is a "qualified lead" for the backend: Sierra `fit_criteria.py`, the Northstar ICP/accept criteria (budget, timeline, five readiness fields, five hard disqualifiers), or something else? Who labels ground truth?
- **Q5.** What pipeline-impact data exists or will exist (meetings booked, rep acceptance, opportunity created, win)? Without it those metrics can only be proxies.
- **Q6.** What is the session-level success event: handoff accepted by a rep, a meeting booked, a correct "not a fit" exit, or a combination? (`SUCCESS_METRICS.md` M0 is my proposal.)
- **Q7.** For config B, which per-state response contracts are approved (message_schema types, chips, banned phrases)? Who approves the contract text?
- **Q8.** Does any caller guarantee a positive buying signal before DECISION_READY→COMMITMENT (trust_state_machine.py:56–60)? Should soul.md:197 or the code be treated as the truth?
- **Q9.** Is the fit threshold `>` or `>=` (fit_criteria.py:407 vs 476)?
- **Q10.** For cases with `"let me connect you"` in `must_not`, is the bridge template meant to be excluded there, or are those cases wrong?
- **Q11.** Which LLM(s), temperature and call budget should configs B and C use? Needed for reproducibility and cost metrics.
- **Q12.** Are thresholds in `SUCCESS_METRICS.md` allowed to be set from the baselines (backend pass 0.35) or do you want to supply them?
- **Q13.** May I commit and push `evals/` to the session branch (PR #9 would receive it), or leave it uncommitted?
