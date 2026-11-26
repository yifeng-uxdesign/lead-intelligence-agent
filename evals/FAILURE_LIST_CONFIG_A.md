# Failure list — additions from the config A eval run (2026-11-19)

Your failure list (`evals/inputs/FAILURE_LIST_2026-11-18.md`, F1–F9) is **unchanged**; it is still in progress and yours. This file only records what the config A run **measured on the backend**, so nothing here is an invented failure: each item cites the check that failed (`REPORT_A.md`, case/turn) and the code. Labels: **from the run** (measured), **from code** (cited), **inferred**. "Matches your F-id" means the *symptom* resembles your report; it is not asserted to have the same cause.

| ID | Observed (from the run) | Where in code (from code) | Resembles | Case / check |
|---|---|---|---|---|
| EV-A1 | "Let me talk to someone." and "I still want to talk to someone before making a decision" are not recognised as a human request (signals.human_request = False). In 5 scenarios this means no handoff on PERT-5; in GD-S6 t6 the conversation is only held because an earlier request is still open | `src/signals/extractor.py:250` (phrase list + patterns) | missed intervention (conformance metric `missed_intervention_rate`); F9-style keyword brittleness | GD-S1..S5 +PERT-5; GD-S6 t6 |
| EV-A2 | A hypothetical question about "no budget or decision-making authority" fires the `pricing_discussion` trigger (rep notified) on the word "budget" | `src/application/signal_adapters.py:15,100-102` | F9 (keyword false positive) | GD-S1 t3 handoff/trigger |
| EV-A3 | "approved" in "We have budget approved" sets `stakeholder_signal` (substring "approve"), producing a stakeholder-approval context trigger alongside strong_buying_signal; "We use HubSpot" fires `competitor_mention` | `src/signals/extractor.py:316-372` | F9 | GD-S2 t2, t4; GD-S4 t5 ("procurement") |
| EV-A4 | Canned loop-breaker replies ("I want to make sure I'm being useful…") appear 4 turns in a row in GD-S3 (t2–t5) and on 2 turns in each of GD-S1, S4, S5; "That's not what I asked" produces a loop-breaker in 4 scenarios | `src/orchestrator.py:170-189`; `src/customer_layer/fallback_variants.py:21-32` | F8 (irrelevant answers / canned fallback); role-play issue 3 in CLAUDE.md | PERT-1, no_canned_fallback_loop; replies in REPORT_A §7 |
| EV-A5 | After an open human request every follow-up gets the same holding text verbatim (GD-S6 t2–t6), so the question at t2 ("what information would you collect?") is not answered | `src/customer_layer/holding_responses.py:64-70`; known gap POL-26 | F7 (question ignored) | GD-S6; PERT-1 no_repeat |
| EV-A6 | All five security/compliance questions (GD-S4) get a generic trust/curiosity template or a loop-breaker; none tells the visitor that a person must answer. Invariants pass only because the text claims nothing | `extractor.py:163-181` ('security' => objection 'trust'); `behavior_engine.py:144-157` | F8 | GD-S4 t1–t5 (REPORT_A §7) |
| EV-A7 | Questions about price structure and implementation time (GD-S5 t3–t5) get the generic objection/curiosity template; no pricing-model or timeline handling | `signal_adapters.py:15` (no match for "charge per lead"); no timeline cue for "how long" | F8; R6/R7 in your inputs are the widget analogues (mine, not yours) | GD-S5 t3–t5 |
| EV-A8 | PERT-2 "Why do you need to know that?" is answered with a template that asks another question in 2 scenarios (new data request in the same reply) | `behavior_engine.py:117-234` | — | PERT-2 no_new_data_request (inferred proxy: '?') |

## Not failures but needing your decision (see REPORT_A + MAPPING Open Questions)
GD-S1 t5 accountability (design says no handoff), GD-S5 t2 pricing as attention, GD-S6 RELAY vs ALERT, definition of `handoff`, rep availability defaults.

## Suggested taxonomy mapping (inferred; for your list)
EV-A2/A3 -> FT-07 (keyword false positive); EV-A4/A6/A7 -> FT-06 (out-of-script question, irrelevant answer); EV-A5 -> FT-05 (question ignored) ; EV-A1 -> new candidate category "human request missed" (not in your list; I did not add it to `drafts/FAILURE_TAXONOMY.md`).
