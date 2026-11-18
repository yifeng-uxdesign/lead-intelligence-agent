# Trace schema (DRAFT)

Purpose: one record per customer turn, with the same field names that golden/test cases use in `expect.trace` (EVAL_SPEC §4). Labels: **[code]** exists today in `DecisionTrace` (`v2/src/domain/decision_trace.py`), **[proposed]** new. Traces are rep-internal and never sent on the customer channel **[code]** (decision_trace.py docstring). Each layer emits only its own section; the orchestrator assembles them **[proposed]**.

## Envelope
| Field | Type | Status |
|---|---|---|
| `session_id`, `case_id`, `config` (A/B/C), `run_id`, `seed` | str | proposed |
| `turn` | int | **[code]** `turn` |
| `customer_text` | str | proposed |
| `pending_question` | str\|null | proposed (needed for FT-05) |

## Layer 1 — extraction  (`extraction.*`)
| Field | Status |
|---|---|
| `status` | **[code]** `interpretation_status` |
| `signals` (dict of `LeadSignals`) | **[code]** `signals` |
| `source` = `rules` \| `llm` \| `llm_fallback_rules` | proposed |
| `llm_signals`, `rule_signals`, `disagreements[]` | proposed (config C) |
| `llm.model`, `llm.latency_ms`, `llm.tokens_in/out`, `llm.error` | proposed |

## Layer 2 — trust  (`trust.*`)  — proposed (not in trace today)
`from`, `to`, `reason` (which signal/rule), `signals_used[]`.

## Layer 3 — mode  (`mode.*`)
`mode` **[code]** `mode`; `reason` **[code]** `mode_reason`; `from` proposed; `rep_presence` proposed.

## Layer 4 — gates/triggers/delivery
| Field | Status |
|---|---|
| `triggers[]` {type, class, evidence} | **[code]** `triggers` (TriggerHit) |
| `primary_trigger`, `primary_class` | **[code]** |
| `fit.confirmed` | **[code]** `fit_confirmed` |
| `fit.score`, `fit.threshold`, `fit.criteria_met[]`, `fit.disqualifiers[]`, `fit.result` | proposed |
| `delivery.status`, `delivery.reason` | **[code]** `delivery_status`, `delivery_reason` |
| `outcome` (answered/held/drafted_for_rep/suggested_to_rep) | **[code]** `outcome` |
| `route` (derived label used by scoring) | proposed — today derived in observer, not emitted (AUDIT 1c-11) |

## Layer 5 — handoff
| Field | Status |
|---|---|
| `intervention.action` (none/opened/already_open/carried_over), `intervention.trigger` | **[code]** `intervention_action`, `intervention_trigger` |
| `rep_notified`, `rep_notified_reason` | **[code]** |
| `handoff.id`, `handoff.sla_minutes`, `handoff.summary` | proposed (SLA from `trigger_catalog.py:77–84`) |

## Layer 6 — generation
| Field | Status |
|---|---|
| `reply.source` | **[code]** `response_source` |
| `reply.loop_guard_applied` | **[code]** `loop_guard_applied` |
| `reply.text`, `reply.chips[]` | proposed |
| `reply.contract_id`, `reply.validator.{passed,violations[]}`, `reply.template_fallback_used` | proposed (config B) |
| `reply.llm.*` as in layer 1 | proposed |

## Cross-cutting
`invariant_checks[]` = {id, passed, detail} (INVARIANTS ids) **[proposed]**; `explanation[]` **[code]** (`DecisionTrace.explain()`).

## Case-file field mapping [proposed]
Existing `cases.json` expect keys **[code]** → trace fields: `route`→`route`; `escalation`→`primary_class`/`intervention.action`; `not_fallback`→`extraction.status`; `rep_notified`→`rep_notified`; `trust_state`→`trust.to`; `intervention_open`→`intervention.action`; `must_include_any`/`must_not`→`reply.text`; `customer_facing`→(payload scan, INV-04).

## Gaps this closes
Trust state, fit inputs, generated text/contract and LLM metadata are absent today **[code]**, so configs B and C cannot be compared without them. Not verified: whether `DecisionTrace` is exposed by the API for the harness (to check in `v2/src/api.py`).
