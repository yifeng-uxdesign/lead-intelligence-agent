# Layer map and LLM boundary (DRAFT)

Labels: **[code]** code (file:line), **[docs]**, **[failures]**, **[proposed]**. `v2/` = `intent-agent-v2/`.

Architecture rule **[code]** `v2/CLAUDE.md:5–8`: deterministic Python owns decisions; an LLM may only (a) interpret into a frozen label set, (b) phrase within an approved response contract, with a deterministic validator. **No LLM call exists in the code today [code]** (`requirements.txt:17–21` comments only; `signals/extractor.py:1–6`, `application/signal_adapters.py:1–4` docstrings).

Pipeline order **[code]** `v2/src/orchestrator.py:378–620` (`run_turn`): load/hydrate → interpret → trust FSM → triggers → mode transition → rep notify/intervention → delivery authorization → reply (holding copy or template + loop guard) → decision trace (`_build_trace`, 623–678) → persist.

## Layer table

| # | Layer | Code owner | Decides today (all rule-based) | Config A | Config B (LLM text) | Config C (LLM extraction) |
|---|---|---|---|---|---|---|
| 1 | **Signal extraction** | `signals/extractor.py`; `application/signal_adapters.py`; `orchestrator.interpret_message` (143–167); keyword list `NOTICE_TOPIC_PHRASES` (232–244) | **[code]** Rule/keyword extraction into `LeadSignals`; fallback path when extraction fails. Frustration is target-aware in backend | rules | rules | **LLM proposes labels** into the frozen set; rules validate/clamp. New: LLM client, prompt, schema validation, timeout → rule fallback, `interpretation_source` in trace |
| 2 | **TrustStateMachine** | `customer_layer/trust_state_machine.py` | **[code]** Pure transitions from signals (l.40–75; DECISION_READY→COMMITMENT at 56–60) | rules | rules | rules (signal quality changes inputs only) |
| 3 | **ModeStateMachine** | `collaboration/mode_state_machine.py` | **[code]** AUTONOMOUS/ALERT/SHADOW/RELAY transitions from triggers + rep presence | rules | rules | rules |
| 4 | **Gates / triggers** | `domain/trigger_catalog.py` (class map 47–55, precedence 58–69, SLA 77–84); `collaboration/delivery_policy.py`; fit gate `clients/sierra/fit_criteria.py`; orchestrator fit 77–116 | **[code]** Trigger evaluation, primary-trigger precedence, delivery matrix (AUTONOMOUS→deliver; ALERT/open intervention→holding copy; SHADOW→rep suggestion; RELAY→pending approval; unknown mode fails closed); fit gate before decision-ready bridge | rules | rules | rules enforce all gates; LLM never sets trigger, mode, delivery or fit directly |
| 5 | **Handoff** | `collaboration/handoff_manager.py`; `core/handoff_queue.py`; `rep_layer/rep_assist_engine.py` | **[code]** Queue creation, dedupe vs open intervention, SLA by trigger, rep brief mapping | rules | rules (brief text stays template) | rules |
| 6 | **Generation** | `customer_layer/behavior_engine.py` (templates, bridge 34–37), `holding_responses.py` (static copy; 15–16 says must stay static), `fallback_variants.py`, loop guard `orchestrator.guard_against_repetition` (170–189) | **[code]** Static templates keyed by trust state/mode; holding copy static; loop breaker static | templates | **LLM phrases** a reply only inside the per-state contract; validator (banned phrases, required elements, no new facts, no pressure, length) → on failure fall back to template. Holding copy stays static (code comment) unless you decide otherwise (Q) | templates |

## What must change for config B **[proposed]**
1. A `ResponseContract` per (trust_state, mode, delivery outcome): allowed intent, required elements (e.g. identify as AI, offer person), forbidden content (price, dates, guarantees, pressure language, rep-internal notes), max length, language rules. Source: soul.md, `message_schema.yaml` global rules, trigger catalog.
2. A deterministic validator that takes (contract, text, context) → pass/fail + reasons; failing text is replaced by the template (fail closed) and logged.
3. An LLM client behind an interface with seed/temperature/model recorded in the trace.
4. Trace fields for contract id, generated text, validator result, fallback-used.
5. Decide which paths are *never* LLM-phrased: holding copy (code comment says static), handoff brief, compliance responses (INVARIANTS).

## What must change for config C **[proposed]**
1. LLM extractor that outputs only frozen labels (`taxonomy.json` + `LeadSignals` keys); schema-checked.
2. Rule-side validation: unknown label → dropped; contradiction with hard rules (e.g., explicit human request keywords) → rules win or both recorded.
3. Disagreement logging: LLM vs rule signals per turn, to measure extractor quality independent of downstream decisions.
4. New fit inputs are out of scope until Q4 (qualification definition) is answered; currently fit has no budget/timeline fields (`orchestrator.py:77–116`).

## Unverified **[code]** points to check before building
- Whether `ModeStateMachine` reads rep presence from session state or a callback (not re-read for this draft).
- Whether the approval gate flag is per-session or global.
