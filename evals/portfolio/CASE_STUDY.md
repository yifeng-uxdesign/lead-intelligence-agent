# Case study: designing and evaluating the behavior of a lead-qualification agent

**Status: living draft v0.1 (2026-11-23).** Written from the project record in this repository. Voice is first person so you can edit it directly; anything I cannot know is marked **[your input]**. Claims are tied to files so you can verify them. Update this document at every milestone (rule in `/CLAUDE.md`); the Update log at the end records each change.

Labels: **record** = documented in this repo (file cited); **measured** = from an eval run; **planned** = not done yet. Nothing marked planned should be presented as done.

---

## 1. One-line pitch
I designed the decision rules of a customer-facing conversational agent (when to answer, when to say "a person will answer", when to hand a lead to a rep, and how), then built an eval harness that measures those rules and used its failures to decide what to build next.

**Three versions of the opening line, by target role** (use one):
- *UX / conversation-design leadership (Genesys-type):* "I define when AI hands a customer to a person, with what context and what honesty, as a framework teams can reuse."
- *Prompt and agent-systems (1mind-type):* "I design the routing and contracts around an LLM agent: when it answers, asks, escalates or declines, and how each decision is tested."
- *Evaluation-heavy (Morgan Stanley-type):* "I build the evaluation method for conversational AI behavior: invariants, classified failures, groundedness checks and a judge calibrated against human labels."

## 2. Project background
- **What it is (record):** Northstar's lead-qualification agent. A B2B website visitor talks to an AI assistant; the system decides whether to keep conversing, answer from approved knowledge, alert a person, ask a rep to decide, or hand a qualified lead to an account executive. Three parts: a scripted demo widget (`northstar/`), a Python behavior backend (`intent-agent-v2/`) and a rep/lead workspace (`rep-workspace/` on `main`, plus a stand-in `northstar/workspace.html`).
- **Why it exists (record, `intent-agent-v2/CLAUDE.md`):** make the *deterministic behavior layer correct and measurable before adding an LLM*, so the project shows behavior-layer design, not model magic. Architecture rule: deterministic code owns decisions (trust state, handoff, authorization, delivery); an LLM may only interpret into a frozen label set and phrase within an approved contract, checked by a validator.
- **The product problem (record, `PLANNING_LOG.md`, "Intelligent Intake & Decision Routing"):** inbound inquiries are slow and inconsistent to triage; reps lose time on unqualified leads; fast, honest first conversations matter. Target customer and ICP: `northstar/ICP_DRAFT.md` (marketing and revenue leaders, smaller teams with heavy inbound, EMEA and the Americas; draft, with decisions marked).
- **Starting point (measured, `northstar/EVALUATION_PLAN.md`, 2026-11-14):** the demo widget failed or partly failed 5 of 6 test scenarios; in four interruption tests, 24 of 24 replies were the same canned fallback.

## 3. The design problem
How should an AI first-contact agent behave so that a visitor is helped honestly and a rep receives the right lead at the right time?

Sub-problems I framed (record, evolving through the logs):
1. **Handoff:** not one thing. Three kinds with different customer experience and rep action: **alert** (a human is needed), **relay** (the agent cannot tell if the lead qualifies, a rep decides), **qualified** (hand to the AE). Decided 2026-11-22 (`evals/PLAN_BEHAVIOR_LAYER.md`).
2. **Honesty at the edge of knowledge:** security, compliance, pricing and accountability questions must not be answered with invented claims. Rule: retrieve an approved answer first; if none, say a person will answer and alert.
3. **Qualification without pressure:** what counts as qualified, and what the agent may ask, in what order, without re-asking (`evals/drafts/QUALIFICATION_CRITERIA.md`).
4. **Recovery and turn-taking:** interruptions, repeats, "that's not what I asked" (`northstar/CONVERSATION_DESIGN.md`).
5. **Measurability:** every rule should be checkable, so a change can be shown to help or harm.

## 4. My role and decisions
**[your input: confirm wording and add prior experience.]** I owned problem framing, product and design decisions, test judgments and the plan; I used Claude Code as an implementation and analysis partner for code, test harnesses and drafts, and reviewed what it produced. Evidence of my decisions (record, `PLANNING_LOG.md` and `evals/PLAN_*`):
- Defined the ICP boundaries and disqualifiers; decided that an explicit "no budget or no plan within 6 months" **disqualifies**, while "unknown" does not; chose supported regions; accepted a placeholder lead-score bar.
- Defined handoff as alert and relay (relay = qualification uncertain), with the qualified handoff to an AE as the ultimate goal (2026-11-22).
- Chose knowledge-first answering with alert on a miss.
- Ran two manual test rounds on the widget and reported failures (F1–F9): pacing, narration lines, suggested replies, prototype wording in the handoff, ignored interruptions, irrelevant answers.
- Decided to drop demo scenarios that do not reflect real situations; chose persona-driven demos with the lead workspace shown beside the chat.
- Decided rules come first, a small LLM prototype later, and an LLM-as-judge exhibit.
- Defined success: a session passes when it reaches the correct terminal outcome (qualified handoff, disqualified, handoff, or informational) with no invariant violation and no unneeded handoff.

## 5. The solution (current state)
**Architecture (record):** pipeline per turn: extract signals → trust state → trigger evaluation → mode transition → delivery authorization → reply from approved templates or holding copy → decision trace (`intent-agent-v2/src/orchestrator.py`). Layer map and where an LLM may go: `evals/drafts/LAYER_MAP.md`.
**Behavior rules (record):** value constitution (`intent-agent-v2/src/core/soul.md`, seven values), trigger catalog with three classes (context, attention, intervention) and fixed precedence (`src/domain/trigger_catalog.py`), delivery matrix that fails closed (`src/collaboration/delivery_policy.py`), approved holding copy (`src/customer_layer/holding_responses.py`).
**Handoff framework (planned design, `evals/PLAN_BEHAVIOR_LAYER.md`):** three handoff types, knowledge router, qualification evaluator. Visualised on the design canvas, board 2.
**What is built vs planned (be explicit in the portfolio):**
| Built (record) | Planned |
|---|---|
| Alert path with holding copy, trigger catalog, trust and mode machines, decision trace, 307 tests, 66-case conformance suite, widget with recovery, pacing and question-first answering, workspace stand-in | Relay and qualified handoff, memory, qualification evaluator, knowledge router, contact capture, LLM extraction and phrasing, wired workspace |

## 6. Process: iterations and evals
**Phase 1: conversation quality in the widget (2026-11-12 to 17, record `PLANNING_LOG.md`).** Wrote a conversation design (`northstar/CONVERSATION_DESIGN.md`: rules R1–R50, plain-language word list), built a recovery ladder, repair intents, question-first answering, turn queue and bubble-by-bubble pacing, a demo knowledge base and a provisional lead workspace. Two owner test rounds exposed failures (F1–F9, `northstar/FAILURE_LIST.md`); I fixed pacing, removed agent-narration lines, added question handling and removed "prototype" wording.
**Phase 2: define "good" (2026-11-14 to 16).** ICP research and decisions (`northstar/ICP_DRAFT.md`), accept criteria, six test scenarios plus two approved additions, a seven-dimension rubric with six hard failures (`northstar/EVALUATION_PLAN.md`).
**Phase 3: audit the behavior layer (2026-11-18, `evals/drafts/`).** Mapped what exists against what a complete eval needs (spec, metrics, taxonomy, dataset, rubric, trace, invariants); found contradictions between docs and code (for example the trust machine allows COMMITMENT without a buying signal while `soul.md` forbids it); wrote success metrics, 24 candidate invariants, a failure taxonomy limited to my own reported failures, a trace schema and a layer map.
**Phase 4: first eval run, config A (2026-11-19, `evals/REPORT_A.md`).** Mapped scenario placeholders to the real code, built an adapter, a runner (free-text and structured modes, which separate extraction misses from logic bugs), a static audit of the template bank and a classified report. **Measured:** 146 failed checks: 117 missing feature, 18 extraction miss, 7 repetition, 4 bad expectation; 0 invariant violations in 82 checks per mode and 0 hits in 59 templates; "Let me talk to someone" was never recognized in 6 of 6 runs. The result was not "tests failing": it was a map of what to build.
**Phase 5: decisions and plans (2026-11-22 to 23).** Rethought handoff (alert, relay, qualified), knowledge-first rule, missing-feature backlog ranked by evidence, persona-driven demo plan, job-requirements consolidation (`evals/PLAN_*`, `JD_*`).
**Next (planned, `evals/ITERATIONS.md`):** iterations 1–4 close rule and feature gaps with a re-run each; iteration 5 runs an LLM-as-judge on config A replies, calibrated against my human labels; iterations 6–7 prototype LLM extraction and phrasing behind a validator, compared with the config A baseline.

### Eval method (what I would explain in an interview)
- **Two modes isolate causes:** free-text runs the full pipeline; structured injects signals. Fails in free-text only → extraction fix; fails in both → logic bug or missing rule; no counterpart in code → missing feature, build or drop the case.
- **Invariants as hard gates**, text and field checks, plus a static scan of every reply template (59 strings).
- **Classified failures, never a single pass rate.** The first run was 0 of 12 case-mode tests passing; the classification, not the rate, drove the plan.
- **Honest labelling:** every statement tagged from code, from my docs, proposed or inferred; ground truth for qualification labelled by me before runs with a second annotator on a sample; no LLM output as ground truth.
- **Guards against fooling myself:** held-out paraphrase set kept separate and never tuned on; v0 results always shown next to any new case set.

## 7. Outcomes so far
- **Measured:** the numbers above (section 6, phase 4). A baseline to improve against, with iteration rows in `evals/ITERATIONS.md` (iteration 0 recorded).
- **Not yet claimed:** any improvement over baseline (iterations 1+ are planned), any user study result, any LLM result. **[your input: add anything you can honestly evidence, such as the observed change in the widget after the pacing fix]**

## 8. Reflection (draft; edit to your voice)
- The most useful move was refusing to treat a low pass rate as the story: separating "missing feature" from "bug" turned 146 failures into a short backlog.
- Defining handoff as three types, instead of one boolean, removed most of the ambiguity in the scenarios.
- A rule-based baseline makes the later LLM comparison meaningful; it also exposed that the LLM's real jobs are paraphrase recognition and phrasing, not decisions.
- Limits I name up front: scenarios are author-written, one tester so far, voice not built, and cross-team influence cannot be shown by a solo project.

## 9. Artifact index (design deliverables)
| Deliverable | Where | What it shows | Status |
|---|---|---|---|
| Architecture map (board 1) | Design canvas | Layers, gaps, relationships | Done (update at milestones) |
| Three handoffs (board 2) | Design canvas | The framework | Done |
| Evidence (board 3), Order of work (board 4), Demo plan (board 5) | Design canvas | First-run result classes, sequence, demo scenarios | Done; board 5 superseded by personas plan |
| Design story timeline (board 6) | Design canvas | How the design evolved, decision by decision | New, 2026-11-23 |
| Case-study storyboard by target role (board 7) | Design canvas | Which sections and exhibits lead for each target role | New, 2026-11-23 |
| Failure list and taxonomy | `northstar/FAILURE_LIST.md`, `evals/drafts/FAILURE_TAXONOMY.md` | Findings from my testing | Living |
| Eval report and mapping | `evals/REPORT_A.md`, `evals/MAPPING.md` | Method and result | Iteration 0 |
| Plans and decisions | `evals/PLAN_*.md`, `PLANNING_LOG.md` | Reasoning over time | Living |
| Iteration log | `evals/ITERATIONS.md` | Before/after per change | Iteration 0 recorded |
| Persona scripts and workspace view | planned | The demo | Planned |
| Principles page | planned (after requirements consolidation) | Reusable framework | Planned |

Design canvas: https://claude.ai/artifact/A715tTjGBPrQw5duzggCRT (private to you until you share it).

## 10. Tailoring to the target roles
Source: `evals/JD_REQUIREMENTS_CONSOLIDATED.md` (three postings so far; refine as more arrive).
| Requirement theme (all three postings) | Where this case study answers it | Lead-with exhibit |
|---|---|---|
| Evaluation and evidence-driven iteration | Sections 6 and 7 | Classified report, iteration table |
| Trust, safety, governance | Sections 3 and 5 | Invariants, holding copy, fails-closed delivery |
| Prompt and context design | Planned iterations 6–7 (an honest gap today) | LLM prototype with contracts, when built |
| Knowledge grounding | Knowledge-first rule; groundedness check planned | Knowledge router demo |
| Language and conversation craft | Phase 1; word list and rules | Before/after conversation excerpts |
| Collaboration, documentation, frameworks | Decision log, Open Questions, principles page (planned) | Three-handoff framework |
| Handoff and routing logic | Section 5 | Board 2 and the workspace |
Emphasis by role: Genesys-type leads with the handoff framework, recovery and trust, and the voice-transfer note; 1mind-type leads with routing, contracts, transcript diagnosis and the LLM prototype; Morgan Stanley-type leads with eval method, groundedness, judge calibration and risk.

## 11. Open items to complete this story
- **[your input]** Your background, years and prior projects to anchor the role section.
- **[your input]** Your preferred first-person phrasing and what you want to show as your own work versus assisted.
- Persona wording for A and F; role-play participants if you want real-data evidence.
- Screenshots or short recordings of the widget before/after and the workspace (not captured yet).

## Update log
| Date | Milestone | What changed in this document |
|---|---|---|
| 2026-11-23 | First draft consolidated from the full session record | Created; artifact index and timeline boards added |
