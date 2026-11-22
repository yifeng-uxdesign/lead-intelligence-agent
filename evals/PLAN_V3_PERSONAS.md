# Plan v3: persona-driven, end to end (capture → qualify → hand off), eval-led

Written 2026-11-22. Tailors the plan to your last replies and the three postings consolidated in `JD_REQUIREMENTS_CONSOLIDATED.md`. Supersedes the scenario list in `PLAN_DEMO_V2.md` (kept as history); the job-fit notes in `JD_FIT_GENESYS.md` stay valid. Labels: **from your message**, **from code** (cited), **from the eval**, **proposed**, **inferred**.

## 0. Decisions recorded (from your message)
- Target roles: **both** the prompt-and-agent-systems kind (1mind) and the evaluation-heavy kind (Morgan Stanley). Evals are a core part of conversation and agent design.
- A **small LLM prototype is acceptable** in the portfolio, but **rules are finished first**.
- **Principles page: after** the requirements consolidation is final (more postings to come).
- **LLM-as-a-judge run: yes**, on the config A replies as an early exhibit.
- Current goal: use the code evals to **fill the main gaps in missing behavior rules**, and show the **end-to-end process**: the agent captures a lead and hands off on **alert** or **relay** situations. The demo shows behavior across **different personas**.

## 1. The end-to-end process to demo, and where each step stands

| Step | What the agent does | Code today (from code / eval) | Needed (backlog id from `PLAN_BEHAVIOR_LAYER.md`) |
|---|---|---|---|
| 1 Greet and understand intent | Reads the first message, answers or asks | Static templates by trust state; keyword signals | F-b keyword fixes |
| 2 Discover | Asks one thing at a time, never repeats, remembers answers | No memory; loop-breakers fire (EV-A4) | M3 memory, M9 question policy |
| 3 Answer from knowledge | Retrieves an approved answer, else says a person will answer | No KB, no router | M4 knowledge router |
| 4 Capture contact | Asks for a company-domain email, respects "no" | No capture, no unknown state | M8 contact and unknown |
| 5 Decide | Qualified / uncertain / disqualified; alert triggers | Alert triggers exist (lexical); no qualification | M2 evaluator, F-a human-request phrases |
| 6 Route | `qualified` to AE, `relay` to a rep, `alert` to a person, exit, or continue | Alert only | M1 handoff type, M6 relay trigger, M7 outcome |
| 7 Rep side (workspace) | Brief, evidence, approve or take over, resolve | Backend endpoints exist (`api.py:300-505`); workspace not wired | W1/W2 from `PLAN_DEMO_V2.md` §3 |
| 8 Hand back and resume | Rep resolves, agent continues | `/rep/action resolve` exists | Workspace binding |

## 2. Personas for the demo (proposed, for you to edit)

Personas come from the buying group in `northstar/ICP_DRAFT.md` §3.2 (titles are from that doc). Persona = who they are + how they write + what they reveal and when. In config A the agent's **behavior** differs by persona because different **signals and triggers** fire; **tone adaptation** to style is a config B (LLM phrasing) item and is not claimed for A.

| # | Persona | How they write | What they reveal (turn) | Decision the agent must make | Outcome | Workspace shows |
|---|---|---|---|---|---|---|
| A | **RevOps/Sales Ops director** (champion and evaluator) | Precise, multi-sentence | Pain (1), volume and CRM (2), who decides, timeline (3–4), work email (5) | Qualify step by step, never re-ask, capture email, hand to AE | `qualified` | Qualified brief: each signal with its source sentence, contact, next step |
| B | **VP Sales or founder, eager** | Short, urgent, "ready to sign" | Budget claim, pushes for a date (2–3); authority and workflow never given | Enthusiasm is not qualification; no date promise; ask once for the missing signals, then ask a rep to decide | `relay` | "Decide this lead": known vs missing signals |
| C | **IT/security gatekeeper** | Formal checklist questions | SOC 2, residency, LLM providers, procurement docs | Answer nothing unapproved; honest "a person will answer"; notify | `alert` or notice (KB miss) | Unanswered topics with the exact questions |
| D | **Frustrated operations lead** (two vendors already failed) | Terse, annoyed | Frustration at other vendors, then at this chat (3) | Hold; a person joins; resume after hand-back | `alert` + hand-back | Join, reply, hand back, resolve |
| E | **Small-team founder, enthusiastic** | Warm, hopeful | 40 inquiries a month, no CRM | Do not push; kindly say it is not a fit yet | `disqualified` (exit) | Closed with reason |
| F | **Demand-gen or marketing leader, just looking** | Curious, one-line questions | Little; asks what it does, how it differs | Answer from the knowledge base; offer a resource; no handoff | `informational_only` | Logged as nurture |
| ⚡ | **Interruption injections** (any persona): "Let me talk to someone", "That's not what I asked", "I don't want to share my email" | n/a | n/a | Human request always wins; no repeat; no repeated email ask | `alert` / continue | Alert raised, no duplicate asks |

Coverage: all five terminal outcomes (qualified, relay as a handoff, alert, exit, informational) and every trigger class. Existing material reused: B = S2, C = S4 (+ pricing from S5), D = S11, E = S3, interruptions = Round 2 perturbations. **A and F are new and need your wording** (S10 and S1 are dropped as you asked).
Open: whether to include an "existing customer on the website chat" persona (the ICP draft routes active customers to the account owner); it adds a feature (D-4 fixture), so it is not in the set.

## 3. What the personas need, minimum (maps to build order)

| Persona | Needs (minimum) | Works today? (from the eval) |
|---|---|---|
| ⚡ interruptions | F-a (phrases), F-c (follow-up variants) | No: "Let me talk to someone" missed in 6 of 6 |
| D | F-a, F-b, `/rep/action resolve` binding, join/reply (J4) | Partly (alert exists) |
| C | M4 router + fixture, no loop-breakers on those turns | No |
| B | M3, M2-min, M6 relay trigger, M1 | No |
| A | M3, M2-min, M8 contact, M7 outcome, M9 order of questions | No |
| E | M5 poor-fit on M2 | No |
| F | M4 router (product basics), M7 informational outcome | Partly |

## 4. Iterations (each is a run of the same runner; rows go into `ITERATIONS.md`)

| Iter | Change | Personas that should flip | Eval additions |
|---|---|---|---|
| 1 | F-a, F-b, F-c rule fixes | ⚡ interruptions; D (first turns) | Held-out score before/after; extraction **precision/recall/F1 per label** from the YAML gold signals (new metric, deterministic) |
| 2 | M1 `handoff_type`, M7 `terminal.outcome` in the trace | none expected; makes outcomes measurable | Trace tests; persona YAML v1 (new file) with outcomes |
| 3 | M3 memory, M2-min evaluator, M6 relay, M8 contact, M9 order | A, B, E | Qualification precision/recall against **your** labels (blind, second annotator on 20–30 cases per `QUALIFICATION_CRITERIA.md`) |
| 4 | M4 knowledge router + fixture | C, F | **Faithfulness check**: every KB reply must be derivable from an approved entry (deterministic RAGAS-style groundedness for config A); no claim invariants |
| 5 | **LLM-as-a-judge on config A replies** | all (scoring only) | Judge rubric (`inputs/judge_rubric_v0.yaml`, not yet read); calibrate the judge against your human labels on a sample; report judge-human agreement, not just scores |
| 6 | **LLM extraction prototype (config C)** behind the frozen labels | A, B, C, F | F1 vs iteration 4; gates still rule-owned; log LLM-vs-rule disagreements |
| 7 | **LLM phrasing prototype (config B)** inside a response contract with a validator | all (text quality) | Judge + validator pass rate + invariants; decisions identical to config A |

Why this serves both role types (inferred): iterations 1–4 are the evaluation-method story (metrics, groundedness, annotation agreement, regressions); iterations 5–7 are the prompt and agent-systems story (contracts between an extractor, a retriever, a responder and a validator: inputs, structured outputs, confidence, evidence, failure handling, which is how 1mind describes subagents). Keep the rules-first order: nothing in 5–7 changes who decides.

## 5. Demo structure (proposed, about 12 minutes, split screen: chat + workspace)
1. 1 min: framing and the three-handoff diagram.
2. 7 min: personas A, B, C, D (about 100 seconds each) with the workspace beside the chat; E and F as quick cuts; one interruption injected live in persona A.
3. 3 min: eval iterations chart (failed checks by class, extraction F1, judge-human agreement) and one thing the evals caught.
4. 1 min: next steps (voice transfer, real participants).

## 6. Constraints and risks
- **The LLM judge and prototypes need an API key and network access** to a model API. This sandbox's network is restricted (a LinkedIn fetch failed on DNS earlier). Needed: an approved key via the environment's credential flow and the model host in the allowed hosts. I will request it only when we reach iteration 5.
- **Changing agent behavior means editing source** under `intent-agent-v2/` (extractor, adapters, templates, orchestrator, new modules). I have not done that. It stays on the session branch and every change is run against the 307-test suite, the conformance harness and the held-out set.
- **Overfitting:** rule fixes tuned to demo texts will not generalize. Keep 2–3 held-out paraphrases per persona, report separately, never tune on them.
- **Persona wording is yours.** I can draft, but realism comes from you or real people (role-play study, optional, from `JD_FIT_GENESYS.md` §4).

## 7. Questions
- **P1.** Approve, edit or swap the personas (A to F). Please give me the real first message and one or two typical follow-ups for A and F, or let me draft them for you to correct.
- **P2.** **Go-ahead to start iteration 1** (rule fixes F-a, F-b, F-c in `intent-agent-v2/`) on this branch? Scope: human-request phrases, keyword false alarms ("budget", "approved", "HubSpot"), three follow-up holding variants; tests and held-out must not regress; report before/after in `ITERATIONS.md`.
- **P3.** During an open alert, should the agent stay silent after the holding copy, vary the holding copy, or answer from the knowledge base? (Affects F-c and persona D.)
- **P4.** Q-H1/Q-K1 from `PLAN_BEHAVIOR_LAYER.md` (relay mechanics; hold or continue on a knowledge miss) still gate iterations 3 and 4.
- **P5.** Which workspace do you demo, and may I wire it to the backend (J3)?
