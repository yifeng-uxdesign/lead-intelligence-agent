# Short-term plan: portfolio demo for a hiring manager

Written 2026-11-22. Companion to `PLAN_BEHAVIOR_LAYER.md` (the full backlog M1–M13, F-a…F-e). This file picks the minimum slice of that backlog that makes a convincing demo.
Labels: **from the eval** (`REPORT_A.md`, `results/config_a_results.json`), **from code** (cited), **from your message**, **proposed**. No source or YAML was changed.

## 0. What the demo has to prove (proposed)
Your thesis (from your messages and `CLAUDE.md`): *the behavior layer, not the LLM, decides; it is clear, rule-based and measurable before any LLM is added.* A hiring manager should see, in about five minutes:
1. A conversation where the agent makes a **correct decision** and you can see **why** (the decision trace).
2. The **three handoff types** working: `qualified` (to the AE), `relay` (a rep decides), `alert` (a person takes over).
3. Honesty at the edge of its knowledge (security questions: no invented claims).
4. **The eval story**: first run, 146 failed checks classified, plan, second run better. This is the portfolio's strongest evidence of product judgment, and it is real.

## 1. Which scenarios to demo

Selection criteria (proposed): each scenario shows a **different decision**, together they cover **all three handoff types** and the main terminal outcomes, and each is short (4–5 turns). Source: the six golden cases in `evals/inputs/scenarios_v0.yaml` plus **S10** from `northstar/eval/scenarios.json` (your approved scenario), because none of the six golden cases ends in a `qualified` handoff, your ultimate goal.

| # | Scenario | Decision it shows | Outcome (proposed) | Works today? (from the eval) | Blocked by |
|---|---|---|---|---|---|
| 1 | **S10** "Gives everything in one message" (Priya, 400 inquiries, Salesforce, decision-maker named, company email) | The agent **qualifies and hands a lead to the AE** without re-asking anything | `qualified` handoff | No. Not in the v0 YAML; no qualification state or memory; signals have no fields | M3 memory, M2-min qualification, M7 outcome, contact capture |
| 2 | **S2** "Ready to sign today" (800 leads, HubSpot, budget approved) | Enthusiasm is not qualification; no date promise; **a rep decides** | `relay` | No: qualification, next-question and relay do not exist (v0: 17 failed checks) | Same spine as #1 + relay trigger |
| 3 | **S4** Security and compliance (SOC 2, data residency, LLM providers, procurement) | **Knows what it does not know**: no invented claim, a person is alerted | `alert` (or notice) on a knowledge miss | No: generic replies and canned loop-breakers on 4 of 5 turns | M4-min knowledge router + fixture |
| 4 | **S6** Wants a real salesperson, continues, asks again | Human request is honoured at once; **AI disclosure**; context carried | `alert` | **Partly.** Turn 1 works (ALERT mode, human-request trigger, holding copy that says it is an AI). The phrase at turn 6 is not recognized and every follow-up repeats one text | F-a phrases, F-c follow-up variants, M3 memory |
| 5 | **S1** opening only (30 seconds): "our sales reps ended up ignoring the scores" | **Does not over-escalate** on the word "reps" | no handoff | **Yes for turn 1** (no false handoff). Turn 3 fires a false pricing alert on "budget" | F-b keyword fix; accountability turn via the knowledge router |
| stretch | **S3** enthusiastic tiny startup | **Says no to hype**: not every eager lead qualifies | `disqualified` (terminal, not a handoff) | No: no poor-fit rule | M5-min on top of the spine |

Recommended running order for the demo: **S1 opening → S6 → S4 → S2 → S10** (ends on the success path). Skip S5 (pricing): it adds no new decision beyond S4's knowledge routing; mention it as covered by the same mechanism.

**Honest caveat to show, not hide (proposed):** extraction is keyword/rule based, so free-typed paraphrases will sometimes miss. Demo with the scripted texts, say so, and show the structured-mode run (signals injected) next to the free-text run: it makes the layer separation visible, which is the point of the design.

## 2. Which gaps to fill first (minimum set for those scenarios)

Counts are failed checks per scenario in the v0 free_text run (from the eval). The v0 YAML asserts many signals the demo does not need; the demo set (section 3) asserts only the minimal ones.

| Scenario | v0 failed checks by kind | What actually flips it |
|---|---|---|
| S6 | 8 signal, 2 mode, 5 `context_preserved` | F-a (phrases), F-c (variants), M3 memory; the 2 mode failures are the RELAY expectation (change to ALERT in the demo set) |
| S4 | 5 signal, 4 handoff, 5 trigger | M4-min (5 security topics → approved "a person will answer" entries; alert/notice) |
| S2 | 8 signal, 5 qualification, 2 handoff, 1 next-question, 1 trigger | M3 + M2-min + relay trigger + M1 handoff_type |
| S1 | 7 signal, 2 handoff, 2 trigger, 1 mode | F-b (turn 3), M4-min (turn 5 accountability) |
| S10 (new) | not run | M3, M2-min, M7, contact capture (company-domain email) |

### Build order (proposed; each step ends with a re-run of config A)
1. **Rule fixes first (hours).** F-a human-request phrases, F-b keyword false alarms ("budget", "approved", "HubSpot"), F-c three follow-up holding variants. Judge on the held-out set, not on the demo texts (`CLAUDE.md`). *Shows:* S6 and S1 clean.
2. **Trace vocabulary (hours).** M1 `handoff_type` and M7 `terminal.outcome` in the trace. Without them the demo cannot display the three types or the success event.
3. **The spine (a few days).** M3 memory (signals and questions kept) + M2-min: only the signals S10, S2 and S3 need: volume per month, stack/CRM, decision authority, timeline, budget claim, work email (company domain). Evaluator returns `qualified` / `uncertain` / `disqualified`; `uncertain` raises relay (M6). *Shows:* S10, S2 and the stretch S3.
4. **Knowledge router (a few days; owner content in parallel).** M4-min: five topics (accountability, certification/security model, data residency, LLM providers, pricing/timeline), a small **golden fixture** (`kb_fixture_v0`), all entries `unverified` except what you approve. Reply = approved text or honest "a person will answer" + alert/notice (Q-K1). *Shows:* S4, S1 turn 5.
5. **Demo packaging (a day).** A new `scenarios_demo_v1.yaml` (new file; v0 untouched) with the demo cases and the new vocabulary; a second `REPORT_A` run; a **replay page** that shows each conversation with the decision trace beside it (built from the adapter's traces); the architecture canvas as the opening slide.

Not needed for the demo (defer): M8 full contact/unknown handling beyond the email, M9 full question policy (a fixed ask order is enough), M10, M11, M12, config B and C, the full 34-signal set.

## 3. What to show as "good outcomes"
- **Before/after table** per scenario and per handoff type: v0 run (today) versus after each build step. Be explicit that the demo set asserts a smaller, deliberately chosen signal set (new file, labelled), and always show v0 results too; do not present the new pass rate alone.
- **The trace, not the transcript**, is the exhibit: for each turn, the signal, trigger, mode, `handoff_type`, and the reason.
- **The classification** (missing feature / extraction miss / bad expectation) and the failure list: it shows you separate "bug" from "feature not built".
- **Open decisions you made** (handoff types, knowledge-first rule): a short decision log.

## 4. Risks (proposed)
- **Overfitting.** Rules tuned to demo texts will look good and generalize badly. Mitigation: write 2–3 paraphrases per demo scenario as a held-out set, report them separately, never tune to them.
- **Scope creep on the qualification spine.** Keep M2-min to six signals; resist defining all 34.
- **Knowledge content is yours.** The agent can only answer what you approve; unapproved topics will (correctly) alert. Decide which two or three entries you will approve for the demo.
- **Demo surface.** The Northstar widget is scripted JS and not wired to this backend; the backend has a terminal chat (`src/chat.py`) and an API. A replay page built from real traces avoids that gap.

## 5. Questions for you
- **D1.** Is the demo live (typed) or recorded/replayed? Replay is safer given rule-based extraction.
- **D2.** Time budget before you want to show it, and who the audience is (design, product, AI engineering)? This decides whether the eval story or the conversation leads.
- **D3.** Confirm the five scenarios and the running order; swap S3 in if "says no to hype" matters more than S1.
- **D4.** Which knowledge entries will you approve for the demo (suggest: what the agent asks about K10, how a person joins K05, who is accountable; leave security and pricing unverified so they alert)?
- **D5.** Q-H1 and Q-K1 from `PLAN_BEHAVIOR_LAYER.md` (relay mechanics; hold or continue on a miss) block steps 3 and 4.
