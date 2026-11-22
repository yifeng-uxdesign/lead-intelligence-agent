# Demo plan v2: real-world scenarios, agent + lead workspace, eval iterations, job fit

Written 2026-11-22. **Supersedes the scenario selection in `PLAN_PORTFOLIO_DEMO.md`** (that file is kept as history). Labels: **from your message**, **from code** (cited), **from the eval**, **inferred**, **proposed**.

## 0. What changed, from your message
- Drop **S1** and **S10** from the demo: they do not reflect real situations. The demo should show scenarios that really happen, with the agent talking to a customer.
- The demo is **one project with two surfaces**: the agent conversation and the **lead workspace**, shown side by side so a design, product or engineering leader sees the agent's behavior land in the workspace.
- **Show eval iterations**, not only one result.
- Fit the demo to a job description (link given).

## 1. Job description: not read yet
I could not open the LinkedIn link: the sandbox cannot resolve `www.linkedin.com` (error `ENOTFOUND`). I will not guess its content. **Please paste the posting text** (title, responsibilities, requirements) and I will map it line by line. Until then, section 5 maps the project to the three audiences you named (design, product, engineering) in general terms, which is **inferred**, not JD-specific. I also cannot tell whether this posting is one of the two you mentioned earlier.

## 2. Scenarios that happen in real inbound conversations (proposed)
Selection: situations a B2B inbound agent meets every week, one decision each, covering all handoff types in `PLAN_BEHAVIOR_LAYER.md`. Existing material is reused where it already fits; the one new scenario needs your wording.

| # | Real situation | Decision | Handoff type | Source | Workspace should show |
|---|---|---|---|---|---|
| 1 | "I'd rather speak with a real salesperson," then keeps asking questions | Honour at once, say it is an AI, carry context | `alert` | S6 (`scenarios_v0.yaml`) | Alert card, SLA, why, summary; follow-ups held |
| 2 | Security, SOC 2, data residency, procurement questions from IT | Do not claim; say a person will answer; notify | `alert`/notice on a knowledge miss | S4 | "Unanswered topic" with the exact question and what the agent said |
| 3 | Eager prospect, budget "approved", wants to sign, but authority and workflow unknown | Enthusiasm is not qualification; no date promise; a rep decides | `relay` | S2 | "Decide this lead": known signals with quotes, missing signals |
| 4 | Visitor discovers over several turns (volume, CRM, who decides, timeline, work email) | Qualifies step by step, asks one thing at a time, never re-asks, hands to the AE | `qualified` | **New (replaces S10), you write the wording** | Qualified brief: each signal with the sentence it came from, contact, recommended next step |
| 5 | Visitor frustrated after other vendors and with this chat; a person joins, hands back, resolves | Hold, person takes over, resume after resolve | `alert` + hand-back | S11 (approved by you earlier; Northstar scenario) | Join, reply, hand back, resolve (the rep side of the full loop) |
| stretch | Enthusiastic tiny startup, 40 inquiries a month, no CRM | Kindly say it is not a fit; do not push | `disqualified` (exit) | S3 | Closed, with reason |

S5 (pricing) is covered by #2 (same knowledge-miss mechanism). Why these five: #1, #2, #5 are the situations where a bot most often harms trust; #3 and #4 are the commercial heart (what qualifies); #4 is the success path you want.

## 3. One project, two surfaces: what exists and what is missing

**Agent side (from code):** `GET /context/{lead_id}` already returns mode, sentiment, handoff queue, `pending_interventions`, `pending_relay_drafts`, `rep_notices`, and the last 50 `decision_trace` entries (`intent-agent-v2/src/api.py:300-332`). `POST /rep/action` supports online, offline, shadow, relay, autonomous, **resolve**, assign, score (`api.py:388-405`); `/rep/approve` and `/rep/reject` handle relay drafts (`api.py:487-504`); `GET /brief/{lead_id}` returns the alert brief (`api.py:335`). Rep endpoints need `X-Rep-Token` (`CLAUDE.md`).

**Workspace side:** two things exist, neither is wired to the backend.
- `rep-workspace/` on `main`: your Figma Make UI (queue, accounts, lead page, activity stream, agent panel) with **hard-coded sample data** (`leads`, `accounts` arrays in `App.tsx`; no `fetch` calls found). From code, inferred as unconnected.
- `northstar/workspace.html` (my stand-in): works only with the scripted widget through browser storage.

**Gap (proposed workstream W):** make the workspace render the real backend behavior.

| Workspace panel | Backend source | Exists? |
|---|---|---|
| Queue ordered by urgency, SLA | `handoff_queue` + trigger SLA (`trigger_catalog.py:77-87`) | Yes; add `handoff_type` |
| "Why this lead needs you" | `decision_trace.primary_trigger` + `triggers[].evidence` | Yes |
| Decision trace timeline per turn | `decision_trace[]` | Yes (last 50) |
| Signals collected, each with its quote | per-signal memory | **No (M3)** |
| Qualification status and missing signals | evaluator | **No (M2)** |
| Relay: draft to approve or edit | `pending_relay_drafts` + `/rep/approve` | Yes (approval-gate meaning) |
| Join, reply, hand back, resolve | `/rep/action resolve`; join/reply as rep message | Resolve yes; rep message to customer: **not found, check** |
| Mode controls (autonomous, shadow, relay) | `/rep/action` | Yes |

**Proposed approach for W:** (W1) a thin client in the workspace that polls `/context` and `/brief` for a chosen `lead_id` and maps fields to the panels above; (W2) a **replay mode** that feeds recorded traces from the eval runner into the same panels, so the demo is repeatable offline; (W3) the live backend as a bonus. Replay first: the same recorded run also drives the eval story.

## 4. Eval iterations to show
The runner and report already exist (`test_config_a.py`, `report_a.py`). Each iteration = one change set, the same runner, a saved snapshot, a row in `evals/ITERATIONS.md` (created; iteration 0 recorded, results copied to `evals/iterations/iter0_config_a_results.json`).

| Iter | Change | Failures it should close (claimed in advance) | Guard |
|---|---|---|---|
| 0 | Baseline (done) | 146 failed checks classified | n/a |
| 1 | Rule fixes: human-request phrases, keyword false alarms, follow-up variants | Extraction misses 18 and repetition 7 (EV-A1..A5) | Held-out set not worse (`conformance/run_heldout.py`); all 307 pytest still pass |
| 2 | `handoff_type` + terminal outcome in the trace | Makes the three types and the success event visible; no pass-rate change expected | Trace tests |
| 3 | Qualification spine (memory, six signals, evaluator, relay) | State layer (32 failed checks) and scenarios #3, #4 | Invariants stay at 0 |
| 4 | Knowledge router (five topics, fixture) | Scenario #2; loop-breakers gone on those turns | No claim in any reply |
| 5 | (If time) LLM extraction, config C, against the frozen baseline | Remaining extraction misses | Rules still own every gate; compare to iteration 4 |
| 6 | (Later) LLM phrasing, config B, behind a validator | Quality of text | Validator + invariants |

Show for each iteration: failed checks by class (the same four classes), per-scenario pass, invariant violations, held-out score, and **one regression you caught** if any. A chart of "failed checks by class per iteration" is the main exhibit; the classification is what makes it credible.
**Honesty rule (proposed):** v0 results stay in every table; new demo cases are a new YAML file, never edits to v0; never tune to the held-out paraphrases.

## 5. How the project reads to each audience (inferred, not from the JD)
| Audience | What they look for | What the demo shows | Exhibit |
|---|---|---|---|
| Design leader | Judgment on human-AI handoff, honesty, tone, edge cases, systems thinking | Why each handoff type exists; honest "a person will answer"; context carried so the customer never repeats; rep-side workspace designed around decisions | Side-by-side conversation + workspace; the three-handoff diagram |
| Product leader | Problem framing, scoping, prioritization, outcomes | Qualified-lead goal, success definition, backlog ranked by evidence, short-term cut for the demo | Plan and iteration table; metrics definitions (`SUCCESS_METRICS.md`) |
| Engineering leader | Determinism, testability, safety, where an LLM belongs | Rules own decisions, LLM only interprets/phrases behind a validator; trace schema; evals with invariants; classification of failures | Decision trace, eval report, iteration history |
Once you paste the JD, I will replace this table with its actual requirements.

## 6. Proposed run of show (about 10 minutes, split screen)
1. 1 min: the problem and the architecture (board 1, board 2).
2. 6 min: scenarios #1, #3, #4, #2 (about 90 seconds each) with the workspace beside the chat. Finish with #5 if time (it shows the whole loop).
3. 3 min: eval iterations: baseline → what changed → what moved; one thing the evals caught.
Replay from recorded traces; show one live typed example only if extraction is solid.

## 7. Revised build order (demo-driven)
1. Iteration 1 rule fixes (hours).
2. Iteration 2 trace vocabulary (hours).
3. Iteration 3 spine (few days) → unlocks scenarios #3, #4.
4. Iteration 4 knowledge router (few days; your approved entries in parallel) → scenario #2.
5. **Workspace W1/W2** (few days, can overlap 3–4): panels bound to trace fields; replay mode.
6. Demo YAML v1 (new file) with the five cases; scenario #4 wording from you; held-out paraphrases.
7. Packaging: replay page or recorded video, iteration chart, case-study page.
Effort labels are rough estimates (inferred).

## 8. Questions
- **J1.** Paste the job description (or allow `www.linkedin.com` and I will retry, though LinkedIn often blocks fetches).
- **J2.** Scenario #4: give me the real multi-turn discovery you have seen, or approve me drafting it for your edit.
- **J3.** Which workspace do you demo: `rep-workspace/` (Figma Make baseline on `main`) or another build? Is it okay to wire it to the backend (changes outside `evals/`)? That is a source change and I will not do it without your go-ahead.
- **J4.** Does the rep need to send a message to the customer from the workspace (join and reply)? I found no endpoint for it.
- **J5.** Is scenario #5 (S11) in scope for the demo or too long?
- **J6.** Replay or live, and the time slot.
