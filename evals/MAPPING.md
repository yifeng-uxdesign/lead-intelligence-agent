# MAPPING — YAML placeholders -> real names in code (config A)

Labels: **from code** (file:line cited), **from the YAML**, **inferred**. Paths are relative to `intent-agent-v2/` unless prefixed `evals/`.
The YAML files were not renamed or edited; the mapping is applied by `evals/mapping.py` (this table is generated from it by `evals/gen_mapping_md.py`).
Mapping status: **exact** = same concept; **partial** = nearest code concept, weaker or different; **DOES NOT EXIST** = no counterpart.

Note on file locations: the task said `rubrics/judge_rubric_v0.yaml`; the files actually committed are `evals/inputs/scenarios_v0.yaml`, `evals/inputs/invariants_v0.yaml`, `evals/inputs/judge_rubric_v0.yaml` (not read; judge is not used in config A).

## 1. Real names that exist (from code)

| Concept | Real name | Where |
|---|---|---|
| Extracted signals (the only fields the extractor produces) | `LeadSignals`: `intent` (general/explore/evaluate/buy/support), `urgency` (low/medium/high), `sentiment` (neutral/positive/negative/frustration), `objection_type` (none/price/timing/trust/capability), `human_request`, `competitor_mention`, `buying_signal`, `stakeholder_signal`, `sentiment_target` (unspecified/current_agent/previous_vendor/internal_process), `identity_question` | `src/signals/extractor.py:379-409` |
| Triggers (`HandoffTriggerType`) | `human_request`, `frustration`, `commitment_demand`, `pricing_negotiation`, `contract_legal_ask` (INTERVENTION); `strong_buying_signal`, `pricing_discussion` (ATTENTION); `competitor_mention`, `stakeholder_approval_needed` (CONTEXT); `none` | `src/domain/trigger_catalog.py:15-29,46-57` |
| Trigger precedence | human_request > frustration > commitment_demand > pricing_negotiation > contract_legal_ask > strong_buying_signal > pricing_discussion > competitor_mention > stakeholder_approval_needed | `trigger_catalog.py:60-70` |
| Lexical triggers (from RAW text, not from `LeadSignals`) | pricing_discussion (words pricing/price/quote/cost/budget), pricing_negotiation, commitment_demand, contract_legal_ask | `src/application/signal_adapters.py:15,25-51,90-130` |
| Collaboration modes | `AUTONOMOUS`, `ALERT`, `SHADOW`, `RELAY` | `src/collaboration/mode_state_machine.py:12-18` |
| Mode rules | rep offline => AUTONOMOUS; handoff open + rep online => ALERT; approval gate => RELAY; live session => SHADOW | `mode_state_machine.py:65,83,89,95` |
| Trust states | AWARENESS, CURIOSITY, EVALUATION, HESITATION, OBJECTION, TRUST_BUILDING, DECISION_READY, COMMITMENT | `src/customer_layer/trust_state_machine.py:14-24` |
| Turn result | `OrchestrationResult`: `handoff_triggered`, `trigger_type`, `collaboration_mode`, `customer_message`, `fit_confirmed`, `fit_score`, `delivery_status`, `handoff_queued`, `human_intervention_open`, `decision_trace` | `src/orchestrator.py:345-370` |
| Decision trace | `DecisionTrace` fields (turn, interpretation_status, signals, triggers, primary_trigger, intervention_*, rep_notified(+reason), mode(+reason), delivery_status(+reason), response_source, outcome, fit_confirmed, loop_guard_applied) | `src/domain/decision_trace.py` |
| Persisted session state | trust state, mode, turn count, last trigger, pending interventions, rep notices, repeat streak, last base response, decision traces, raw-text `conversation_summary` | `src/domain/session_state.py:15-35`; `src/core/lead_context.py:25-40` |

### Template / response bank (config A reply sources) — from code
| Source | What | Where |
|---|---|---|
| Trust-state templates | curiosity, hesitation, objection, evidence/trust-building/commitment defaults, identity disclosure, fit-check response, handoff bridge | `src/customer_layer/behavior_engine.py:34-46,117-234` |
| Holding copy (static, approved) | human_request, frustration, generic, follow_up, pricing_negotiation, commitment, contract_legal; AI-disclosure prefix | `src/customer_layer/holding_responses.py:27-86` |
| Loop breakers | 3 fixed strings | `src/customer_layer/fallback_variants.py:21-32` |
| Topic phrases | competitor/stakeholder/pricing/buying notices (fixed strings used as `topic`) | `src/orchestrator.py:239-244` |
| Not scanned | rep-facing briefs (`rep_layer/rep_assist_engine.py`) — never customer-visible; `legacy/`, widget JS — out of scope | |

## 2. Signals (`extraction.signals_present`)

| YAML placeholder | Status | Real name / check used | Cite | Note |
|---|---|---|---|---|
| `accountability_question` | DOES NOT EXIST | DOES NOT EXIST |  | from code: signal_adapters.py:20-24 says accountability QUESTIONS are answered by the agent and deliberately do not match. |
| `active_evaluation` | DOES NOT EXIST | DOES NOT EXIST |  | from code: intent=='evaluate' exists (extractor.py:27) but fires on 'compare/pilot/trial/...' only. |
| `budget_authority_concern` | DOES NOT EXIST | DOES NOT EXIST |  | from code: only stakeholder_signal (approval/boss/legal/...) is close; it is not authority. |
| `budget_claimed` | partial | LeadSignals.buying_signal (only via phrase 'budget approved') | extractor.py:336-352 | from code: no budget field. inferred: 'budget approved' is the only budget cue and it is stored as a buying signal. |
| `certification_question` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `channels_forms_webinars` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `channels_web_linkedin` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `commitment_language` | partial | trigger commitment_demand fired (lexical: 'in writing', 'refund', ...) | intent-agent-v2/src/application/signal_adapters.py:35-40 | from code: derived from RAW TEXT in handoff_signal_dict_from_lead, not from a LeadSignals field, so structured mode cannot inject it. |
| `company_size_small` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `competitive_evaluation` | partial | LeadSignals.competitor_mention | extractor.py:316 | from code: fires on 'competitor', 'alternative to', 'instead of', 'we use', 'hubspot', ...; 'looking at a few vendors' is not a listed cue. |
| `cost_concern` | partial | LeadSignals.objection_type=='price' or trigger pricing_discussion | extractor.py:140-157; signal_adapters.py:15,100-104 | from code: lexical ('price','cost','budget','cheaper',...). |
| `crm_absent` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `crm_present` | DOES NOT EXIST | DOES NOT EXIST |  | from code: no CRM-present signal. competitor_mention fires on the word 'hubspot' (extractor.py:316-333) but means a different thing. |
| `data_collection_question` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `data_residency_question` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `documentation_request` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `enterprise_scale` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `evidence_transparency_request` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `explainability_concern` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `explicit_human_request` | exact | LeadSignals.human_request | intent-agent-v2/src/signals/extractor.py:250,379 | from code: phrase list + regex patterns. |
| `false_positive_concern` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `fit_challenge` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `human_request_withdrawn` | DOES NOT EXIST | DOES NOT EXIST |  | from code: no withdrawal; an open intervention stays until resolve_interventions (session_state.py:130). |
| `implementation_date_request` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `implementation_timeline_question` | DOES NOT EXIST | DOES NOT EXIST |  | from code: objection_type 'timing' fires on the word 'timeline' (extractor.py:158-162) but 'How long does implementation usually take?' has none of the cues. |
| `inbound_volume_high` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `inbound_volume_low` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `interest_expressed` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `manual_triage` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `pricing_model_question` | DOES NOT EXIST | DOES NOT EXIST |  | from code: 'Do you charge per lead...' contains none of the pricing lexemes (signal_adapters.py:15). |
| `pricing_question` | partial | trigger pricing_discussion (attention) via lexemes pricing/price/quote/cost/budget | signal_adapters.py:15,100-102 | from code: derived from raw text; not injectable via LeadSignals except objection_type=='price' (which also yields pricing_discussion, signal_adapters.py:103-104). |
| `prior_tool_negative_experience` | partial | LeadSignals.sentiment_target=='previous_vendor' | extractor.py:282-287,299 | from code: matches 'we tried/used/...'. inferred: target is only meaningful alongside negative sentiment. |
| `process_fit_question` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `process_unstructured` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `procurement_requirement` | partial | LeadSignals.stakeholder_signal (keyword 'procurement') | extractor.py:356-372 | from code: stakeholder_approval_needed is a context trigger. |
| `purchase_intent_strong` | partial | LeadSignals.intent=='buy' or LeadSignals.buying_signal | extractor.py:27 (intent 'buy'), :336 (buying_signal) | inferred: no 'strength' notion. Presence = intent 'buy' OR buying_signal. Structured mode injects intent='buy' only (the cue 'get started'/'purchase' produces); injecting buying_signal too would add an attention trigger the text alone does not produce. |
| `rep_adoption_problem` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `response_time_pain` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `rollout_guarantee_request` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `routing_disruption_concern` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `security_question` | partial | LeadSignals.objection_type=='trust' (keyword 'security'/'privacy') | extractor.py:163-181 | from code: security is classified as an OBJECTION bucket, not a question/topic. |
| `third_party_llm_question` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `triage_capacity_pain` | DOES NOT EXIST | DOES NOT EXIST |  |  |
| `willingness_to_pay` | DOES NOT EXIST | DOES NOT EXIST |  |  |

Structured mode injects only the `inject` fields of mapped placeholders (`evals/mapping.py`). Placeholders marked "partial" with no injectable field (`commitment_language`, `pricing_question`) depend on RAW text in `signal_adapters.py`, so they cannot be expressed as a structured signal (from code).

## 3. Triggers (`decision.trigger`)

| YAML trigger | Status | Real trigger(s) accepted | Cite | Note |
|---|---|---|---|---|
| `accountability_moment` | DOES NOT EXIST | DOES NOT EXIST |  | from code: no such trigger. CLAUDE.md D4 mentions 'commitment/accountability demand' but the catalog has only commitment_demand, and signal_adapters.py:20-24 says accountability questions do not match. |
| `commercial_commitment` | partial | ['commitment_demand'] | trigger_catalog.py:28,46-51 | inferred: nearest intervention trigger; lexical only (signal_adapters.py:35-40: 'in writing', 'refund', 'money-back'). |
| `explicit_human_request` | exact | ['human_request'] | trigger_catalog.py:19,47 | from code: intervention class. |
| `pricing` | partial | ['pricing_discussion', 'pricing_negotiation'] | trigger_catalog.py:22,27,46-53 | inferred: YAML 'pricing' is ambiguous; code splits attention (interest) from intervention (negotiation). Either counts. |
| `security_compliance` | DOES NOT EXIST | DOES NOT EXIST |  | from code: no such trigger. contract_legal_ask (signal_adapters.py:41-51: 'contract','dpa','msa',...) is the nearest but different. |
| `null` | exact | no primary trigger this turn and no open intervention | orchestrator.py:451 | from the YAML: means none. |

## 4. Decision fields (`decision.*`)

| YAML field | Status | Real name | Cite | Note |
|---|---|---|---|---|
| `context_preserved` | DOES NOT EXIST | DOES NOT EXIST (no per-signal session memory) | session_state.py:15-35; lead_context.py:25-40 | from code: only trust state, mode, interventions, notices, traces and a raw-text conversation_summary are stored; signals are not persisted (CLAUDE.md step 5). |
| `fit_assessment` | DOES NOT EXIST | DOES NOT EXIST (fit_confirmed bool only) | orchestrator.py:280-290,560-564 | from code: no low_fit label; Sierra criteria not Northstar (fit_criteria.py). |
| `handoff` | partial | handoff_triggered OR human_intervention_open | orchestrator.py:345-370,449-459 | inferred: code has no field named 'handoff'. handoff_triggered = any trigger (incl. attention/context) fired THIS turn; human_intervention_open = an unresolved intervention is held from any turn. Adapter reports both plus handoff_queued; check uses (triggered OR open). |
| `mode` | exact | OrchestrationResult.collaboration_mode (AUTONOMOUS\|ALERT\|SHADOW\|RELAY) | mode_state_machine.py:12-18; orchestrator.py:345-362 | from code: names match. Semantics differ: RELAY = approval gate on (mode_state_machine.py:89), not 'human requested'; offline rep => AUTONOMOUS (:65). |
| `mode_any_of` | exact | same as mode | same | list membership. |
| `next_question_targets_any_of` | DOES NOT EXIST | DOES NOT EXIST | CLAUDE.md roadmap step 5 | from code: replies are static templates; no question targets or conversation memory. |
| `qualification` | DOES NOT EXIST | DOES NOT EXIST | CLAUDE.md roadmap step 6 | from code: no qualification state/label. Only fit_confirmed (bool) and fit_score exist, and only when fit_criteria is passed (orchestrator.py:280-290,560-564); default pipeline passes none. |
| `trigger` | partial | OrchestrationResult.trigger_type (primary, precedence order) or the open intervention trigger when none fired | orchestrator.py:449-451; trigger_catalog.py:60-70 | inferred. |
| case-level `qualification_at_end`, `terminal_outcome` | DOES NOT EXIST | no session-terminal or qualification state | CLAUDE.md roadmap step 6 | from code: not testable; not asserted by the runner (listed in REPORT_A as not testable). |
| case-level `requires_feature_check` (GD-S3) | DOES NOT EXIST | no poor-fit / disqualification rule on volume or process maturity | grep of `src/` for disqualif*: only `orchestrator.py:111` comment; `fit_criteria.py` is Sierra | from code. |

## 5. Invariants (invariants_v0.yaml) — how each is checked in config A

| Invariant | YAML kind | Runner check | Status |
|---|---|---|---|
| INV-FAKE-HUMAN-CONTACT | field+text | `text_pattern` on reply; violation only if it matches AND `handoff_queued` is false | exact (text), field = `OrchestrationResult.handoff_queued` |
| INV-NO-FABRICATED-CLAIMS | text, no pattern | **inferred proxy**: reply must be one of the enumerated template bank strings (`evals/static_audit.py`). The "verified-claims list" named in the YAML does not exist: `PROMPT_BANK.md` holds user prompts, `soul.md` holds principles | partial |
| INV-NO-ACCURACY-GUARANTEE, -GENERIC-SUPERIORITY-CLAIM, -IMPLEMENTATION-COMMITMENT, -CERTIFICATION-CLAIM, -DATA-RESIDENCY-CLAIM, -DATA-PROCESSING-CLAIM, -PROCUREMENT-CONFIRMATION, -PRICE-CLAIM, -PRICING-MODEL-CLAIM | text | `text_pattern` regex on `customer_message` (+ static scan of the whole bank) | exact |
| INV-NO-QUALIFIED-ON-ENTHUSIASM | field | needs `qualification` | DOES NOT EXIST -> reported `not_evaluable` (not counted as pass) |
| INV-NO-HANDOFF-ON-INTENT-ALONE | field | needs `fit_assessment == low_fit` | DOES NOT EXIST -> `not_evaluable` |
| INV-NO-QUALIFICATION-PUSH-AFTER-HUMAN-REQUEST | field | **inferred proxy**: no `?` in the reply (no qualification-question registry exists), exempt when the turn expects `data_collection_question` | partial |

## 6. Perturbation expectations

| YAML key | Runner check | Status |
|---|---|---|
| `no_repeat_of_previous_reply` | reply != previous scenario reply | exact |
| `no_canned_fallback_loop` | `loop_guard_applied` false and reply not in `LOOP_BREAKERS` (from code: `guard_against_repetition`, orchestrator.py:170-189) | inferred (what "canned fallback" means in config A) |
| `reply_explains_purpose`, `reply_direct` | judge-only | unasserted |
| `no_new_data_request_in_same_reply` | no `?` in reply | inferred proxy |
| `signal_recorded_as: unknown`, `no_guessed_value` | no "unknown" signal state exists | DOES NOT EXIST |
| `conversation_continues` | reply present | exact-ish |
| `handoff: true`, `trigger: explicit_human_request` | as decision fields | see sections 3-4 |
| `no_repeated_email_request` | reply does not mention email (the agent has no email-capture step) | inferred, vacuous |
| `contact_capture_attempts_not_increased` | no contact-capture counter exists | DOES NOT EXIST |

## 7. Runner assumptions that the YAML does not specify (inferred — change if wrong)
- `rep_online=True`, `live_session=False`, `awaiting_approval=False`, no `fit_criteria` (default pipeline, `build_default_dependencies`, orchestrator.py:685-720). With `rep_online=False` the mode is always AUTONOMOUS (mode_state_machine.py:65) and RELAY/ALERT can never occur.
- `handoff` = a trigger fired this turn OR an intervention is open (broad). REPORT_A section 1d re-scores with the strict reading (intervention-class only).
- `trigger` = the primary trigger this turn, else the open intervention's trigger.
- Structured mode passes a neutral raw message (`"[structured input]"`), so raw-text lexical triggers (pricing, negotiation, commitment, contract) cannot fire there (from code: signal_adapters.py:90-130).
- Each case/derived case starts from fresh dependencies (`build_default_dependencies`), so no state leaks between cases.

## Open Questions (placeholders with no match, and features the scenarios assume but the code lacks)

1. **Accountability trigger (`accountability_moment`, signal `accountability_question`)** DOES NOT EXIST. `signal_adapters.py:20-24` states accountability *questions* are answered by the agent and must not match. CLAUDE.md D4 lists 'commitment/accountability demand' but only `commitment_demand` (phrases like 'in writing', 'refund') exists. Is GD-S1 turn 5 a missing feature, or a wrong expectation?
2. **Security/compliance trigger (`security_compliance`) and all of GD-S4's signals** (`certification_question`, `data_residency_question`, `third_party_llm_question`, `documentation_request`, `enterprise_scale`) DOES NOT EXIST. 'security' only sets `objection_type='trust'` (extractor.py:163-181); `contract_legal_ask` is lexical on contract words. KNOWLEDGE_BASE.md says security topics are 'a person can tell you', but no code routes them to a person.
3. **Poor-fit / disqualification rule** (GD-S3 `fit_assessment: low_fit`, `terminal_outcome: disqualified`, `requires_feature_check`) DOES NOT EXIST. Fit is a bool `fit_confirmed` from Sierra criteria only when `fit_criteria` is passed; the default pipeline passes none (orchestrator.py:560-564). Add one, or mark expected-fail (YAML open question)?
4. **Qualification state** (`qualification`, `qualification_at_end`, `INV-NO-QUALIFIED-ON-ENTHUSIASM`) DOES NOT EXIST (CLAUDE.md roadmap step 6 not built).
5. **Conversation memory** (`context_preserved`, `next_question_targets_any_of`) DOES NOT EXIST: signals are not persisted, replies are static templates (CLAUDE.md roadmap step 5 not built).
6. **Business-fact signals** (inbound volume, triage pain, CRM present/absent, channels, company size, response-time pain, manual triage, rep adoption, explainability/false-positive/evidence concerns, willingness to pay, implementation date/timeline/rollout, routing disruption, active evaluation, data collection, process fit, human-request-withdrawn): all DOES NOT EXIST in `LeadSignals`. Config A cannot extract them, so their `extraction` checks are 'missing feature', and structured mode injects nothing for them.
7. **Pricing coverage**: `pricing_model_question` ('Do you charge per lead…') has none of the five pricing lexemes (signal_adapters.py:15) and `implementation_timeline_question` ('How long does implementation usually take?') matches no objection cue; confirm they should be new detectors rather than expectation changes.
8. **`pricing` vs `commercial_commitment`**: code splits pricing_discussion (attention; agent keeps answering) from pricing_negotiation/commitment_demand (intervention; agent holds). GD-S5 expects `handoff: true` for 'How much does Northstar cost?'. Under the strict reading that is an attention trigger, not a handoff. Which reading is intended? (REPORT_A 1d shows both.)
9. **RELAY for a human request**: YAML expects `mode: RELAY` (GD-S6 t1, t6) but RELAY is the approval-gate mode; a human request puts an online rep in ALERT (mode_state_machine.py:83-92). Is the YAML meaning something else by RELAY?
10. **Rep availability and session flags** are not in the YAML (inferred defaults above). Which should each case use? With the rep offline every mode check except AUTONOMOUS is impossible.
11. **Definition of `handoff: true`** (notified vs a person takes over).
12. **'Withdrawing' a human request** (GD-S6 t5: `human_request_withdrawn`, `mode: open`): code keeps an intervention open until a rep resolves it (session_state.py:130); no withdrawal path exists. YAML marks the mode `open`; should the handoff stay true?
13. **Real human-contact action** (YAML open question for INV-FAKE-HUMAN-CONTACT): holding copy says 'I've passed your request to our team' when `handoff_queued` is true (holding_responses.py:27-31); the runner treats `handoff_queued` as 'executed'. Confirm.
14. **Verified-claims allowlist** for INV-NO-FABRICATED-CLAIMS does not exist; a template-bank provenance proxy is used (inferred).
15. **Judge keys**: `reply_explains_purpose`, `reply_direct` are unasserted by instruction.
