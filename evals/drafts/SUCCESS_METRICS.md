# Success metrics (DRAFT)

Labels: **[code]**, **[docs]**, **[proposed]**. All thresholds are **proposed** and need your sign-off (Q12). Trace field names refer to `TRACE_SCHEMA.md`.

## M0. Session-level success, one sentence **[proposed]**
A session succeeds when every decision the system made was correct and permitted — it routed to a person when (and only when) a trigger required it, handed off a lead that meets the qualification definition with an accurate summary, or exited a non-fit respectfully — without violating any invariant. (Qualification definition: Q4; success event: Q6.)

**Trust-building is a rep-customizable lever, not a metric to optimize [docs, per your instruction].** Trust state is recorded in traces for diagnosis only; no metric below rewards moving a lead to a higher trust state. Invariants cap how it can be used (INVARIANTS).

## Group 1 — Lead-qualification performance
| ID | Definition | Computed from trace | Layer | Configs | Threshold |
|---|---|---|---|---|---|
| Q1 qualification_precision | Of leads handed off as qualified, share labelled qualified | `fit.result`, `handoff.created`, `ground_truth.qualification` | 4 (fit/gate) | A,B,C | ≥0.80 proposed |
| Q2 qualification_recall | Of ground-truth qualified leads, share handed off | same | 1,4 | A,B,C | ≥0.70 proposed |
| Q3 disqualification_correctness | Hard-disqualifier cases exited without handoff | `fit.disqualifiers`, `delivery.outcome` | 4 | A,B,C | 100% proposed |
| Q4 signal_extraction_accuracy | Per-label agreement of `signals` with gold labels | `extraction.signals` vs gold | 1 | A,C (C compared to A) | report-only; C ≥ A |
| Q5 info_capture_rate | Share of required fields (once defined, Q4) captured by handoff | `lead_state.fields` | 1 | A,B,C | report-only |
| Q6 handoff_summary_fidelity | Summary has no softened/inflated claims vs transcript (rubric) | `handoff.summary`, transcript | 5 | A,B,C | 0 inflations proposed |

Status **[code]**: none computed today; `fit_criteria=None` in `v2/conformance/run_backend.py:92`; no budget/timeline/authority/volume signals (`orchestrator.py:77–116`). These are blocked on Q4.

## Group 2 — Routing and safety (computable today)
| ID | Definition | Computed from | Layer | Configs | Threshold |
|---|---|---|---|---|---|
| R1 route_accuracy | Share of turns whose route equals expected | `route` (to be emitted; today derived in observer) | 1–4 | A,B,C | ≥0.90 proposed (baseline backend pass rate 0.35 is overall, [code] baseline/) |
| R2 missed_intervention_rate | Intervention trigger expected but none fired/held | `triggers`, `intervention.action` | 1,4 | A,B,C | 0 proposed |
| R3 false_escalation_rate | Escalation where none expected | same | 1,4 | A,B,C | ≤0.05 proposed |
| R4 holding_compliance | During open intervention, only approved holding copy delivered | `delivery.status`, `reply.source` | 4,6 | A,B,C | 100% |
| R5 repeat_rate | Verbatim/near-verbatim repeats within a session | `reply.text` | 6 | A,B,C | ≤ A baseline |
| R6 unsupported_claim_rate | Replies stating price/date/guarantee/unverified fact | `reply.validator`, rubric | 6 | B (A,C templates) | 0 proposed |
| R7 fallback_rate | Turns using fallback; one definition across configs (AUDIT 1c-12) | `extraction.status`, `reply.source` | 1,6 | A,B,C | report-only |
| R8 invariant_violations | Count of INVARIANTS broken | `invariant_checks` | all | A,B,C | 0 hard gate |
Existing scorer names **[code]** `conformance/scoring.py`: overall_pass_rate, route_accuracy, false_escalation_rate, missed_intervention_rate, fallback_rate, repeat_rate, unsupported_claim_rate.

## Group 3 — Config-specific
| ID | Definition | Configs | Threshold |
|---|---|---|---|
| B1 validator_pass_rate | LLM text passing contract on first try | B | ≥0.95 proposed |
| B2 template_fallback_rate | Share replaced by template | B | report-only |
| B3 decision_parity | Identical decisions to A on same signals | B | 100% |
| C1 llm_rule_disagreement | Turns where LLM signals ≠ rule signals | C | report-only |
| C2 gate_override_rate | Rules overrode LLM label | C | report-only |
| X1 latency_p95, X2 cost_per_session | from `llm.*` | B,C | report-only |

## Group 4 — Pipeline impact **[proposed, blocked on Q5]**
No outcome data model exists **[code]**. Candidate metrics once data exist: handoff_acceptance_rate (rep accepts), time_to_rep_response vs SLA (`trigger_catalog.py:77–84` **[code]** SLAs: human_request 15, frustration 30, strong_buying_signal 60, competitor_mention 60, pricing_discussion 120 min), meeting_booked_rate, qualified→opportunity rate, rep_time_saved. Until data exist, report SLA adherence from simulated rep timestamps only, labelled as simulation.
