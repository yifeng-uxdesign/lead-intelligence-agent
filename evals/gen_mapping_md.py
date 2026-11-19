"""Writes MAPPING.md from mapping.py (so the table cannot drift from what the runner applies)."""
import os

import checks
import mapping

HERE = os.path.dirname(os.path.abspath(__file__))
ph = mapping.placeholders_in_yaml(checks.SCEN)
L = []
w = L.append


def esc(x):
    return str(x).replace("|", "\\|").replace("\n", " ")


w("""# MAPPING — YAML placeholders -> real names in code (config A)

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
|---|---|---|---|---|""")
for k in sorted(ph["signals"]):
    m = mapping.SIGNALS[k]
    w(f"| `{k}` | {'DOES NOT EXIST' if m['status']=='none' else m['status']} | {esc(m['real'])} | {esc(m['cite'])} | {esc(m['note'])} |")

w("""
Structured mode injects only the `inject` fields of mapped placeholders (`evals/mapping.py`). Placeholders marked "partial" with no injectable field (`commitment_language`, `pricing_question`) depend on RAW text in `signal_adapters.py`, so they cannot be expressed as a structured signal (from code).

## 3. Triggers (`decision.trigger`)

| YAML trigger | Status | Real trigger(s) accepted | Cite | Note |
|---|---|---|---|---|""")
for k, m in sorted(mapping.TRIGGERS.items()):
    w(f"| `{k}` | {'DOES NOT EXIST' if m['status']=='none' else m['status']} | {esc(sorted(m['real']) or 'DOES NOT EXIST')} | {esc(m['cite'])} | {esc(m['note'])} |")
w("| `null` | exact | no primary trigger this turn and no open intervention | orchestrator.py:451 | from the YAML: means none. |")

w("""
## 4. Decision fields (`decision.*`)

| YAML field | Status | Real name | Cite | Note |
|---|---|---|---|---|""")
fields = sorted(ph["fields"])
for k in fields:
    m = mapping.DECISION_FIELDS.get(k)
    if k == "trigger":
        m = mapping.DECISION_FIELDS["trigger"]
    w(f"| `{k}` | {'DOES NOT EXIST' if m['status']=='none' else m['status']} | {esc(m['real'])} | {esc(m['cite'])} | {esc(m['note'])} |")
w("""| case-level `qualification_at_end`, `terminal_outcome` | DOES NOT EXIST | no session-terminal or qualification state | CLAUDE.md roadmap step 6 | from code: not testable; not asserted by the runner (listed in REPORT_A as not testable). |
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
""")
n = 1
def q(t):
    global n
    w(f"{n}. {t}")
    n += 1
q("**Accountability trigger (`accountability_moment`, signal `accountability_question`)** DOES NOT EXIST. `signal_adapters.py:20-24` states accountability *questions* are answered by the agent and must not match. CLAUDE.md D4 lists 'commitment/accountability demand' but only `commitment_demand` (phrases like 'in writing', 'refund') exists. Is GD-S1 turn 5 a missing feature, or a wrong expectation?")
q("**Security/compliance trigger (`security_compliance`) and all of GD-S4's signals** (`certification_question`, `data_residency_question`, `third_party_llm_question`, `documentation_request`, `enterprise_scale`) DOES NOT EXIST. 'security' only sets `objection_type='trust'` (extractor.py:163-181); `contract_legal_ask` is lexical on contract words. KNOWLEDGE_BASE.md says security topics are 'a person can tell you', but no code routes them to a person.")
q("**Poor-fit / disqualification rule** (GD-S3 `fit_assessment: low_fit`, `terminal_outcome: disqualified`, `requires_feature_check`) DOES NOT EXIST. Fit is a bool `fit_confirmed` from Sierra criteria only when `fit_criteria` is passed; the default pipeline passes none (orchestrator.py:560-564). Add one, or mark expected-fail (YAML open question)?")
q("**Qualification state** (`qualification`, `qualification_at_end`, `INV-NO-QUALIFIED-ON-ENTHUSIASM`) DOES NOT EXIST (CLAUDE.md roadmap step 6 not built).")
q("**Conversation memory** (`context_preserved`, `next_question_targets_any_of`) DOES NOT EXIST: signals are not persisted, replies are static templates (CLAUDE.md roadmap step 5 not built).")
q("**Business-fact signals** (inbound volume, triage pain, CRM present/absent, channels, company size, response-time pain, manual triage, rep adoption, explainability/false-positive/evidence concerns, willingness to pay, implementation date/timeline/rollout, routing disruption, active evaluation, data collection, process fit, human-request-withdrawn): all DOES NOT EXIST in `LeadSignals`. Config A cannot extract them, so their `extraction` checks are 'missing feature', and structured mode injects nothing for them.")
q("**Pricing coverage**: `pricing_model_question` ('Do you charge per lead…') has none of the five pricing lexemes (signal_adapters.py:15) and `implementation_timeline_question` ('How long does implementation usually take?') matches no objection cue; confirm they should be new detectors rather than expectation changes.")
q("**`pricing` vs `commercial_commitment`**: code splits pricing_discussion (attention; agent keeps answering) from pricing_negotiation/commitment_demand (intervention; agent holds). GD-S5 expects `handoff: true` for 'How much does Northstar cost?'. Under the strict reading that is an attention trigger, not a handoff. Which reading is intended? (REPORT_A 1d shows both.)")
q("**RELAY for a human request**: YAML expects `mode: RELAY` (GD-S6 t1, t6) but RELAY is the approval-gate mode; a human request puts an online rep in ALERT (mode_state_machine.py:83-92). Is the YAML meaning something else by RELAY?")
q("**Rep availability and session flags** are not in the YAML (inferred defaults above). Which should each case use? With the rep offline every mode check except AUTONOMOUS is impossible.")
q("**Definition of `handoff: true`** (notified vs a person takes over).")
q("**'Withdrawing' a human request** (GD-S6 t5: `human_request_withdrawn`, `mode: open`): code keeps an intervention open until a rep resolves it (session_state.py:130); no withdrawal path exists. YAML marks the mode `open`; should the handoff stay true?")
q("**Real human-contact action** (YAML open question for INV-FAKE-HUMAN-CONTACT): holding copy says 'I've passed your request to our team' when `handoff_queued` is true (holding_responses.py:27-31); the runner treats `handoff_queued` as 'executed'. Confirm.")
q("**Verified-claims allowlist** for INV-NO-FABRICATED-CLAIMS does not exist; a template-bank provenance proxy is used (inferred).")
q("**Judge keys**: `reply_explains_purpose`, `reply_direct` are unasserted by instruction.")
open(os.path.join(HERE, "MAPPING.md"), "w").write("\n".join(L) + "\n")
print("MAPPING.md written")
