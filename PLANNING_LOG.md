# Planning Log

A running log of brainstorming, strategy iterations and decisions for the Lead Intelligence Agent
(Northstar frontend demo + `intent-agent-v2` behavior backend).

Newest entries go at the top of **Log**. Never delete an old entry. If a decision changes, add a new
entry that says what changed and why, and mark the old one `superseded`.

---

## Current focus

- Northstar conversational demo: customer-facing UI, scripted scenarios, deterministic behavior rules,
  trust and frustration handling, human handoff scenarios.
- Constraint: the architecture stays deterministic. No LLM provider, external API key or external
  service for now.

## Open questions

- [ ] _(add yours here)_

## Ideas parking lot

- _(unrefined ideas; promote to a log entry when you act on one)_

---

## Log

### 2026-11-13 — Owner answers: show the human rep joining; confirmations

**Context / trigger:** Owner answered the open questions on the conversation design plan.

**Decisions:**
- **Demo a person joining the conversation.** A lead workspace notifies sales reps, so instead of disclaiming
  "prototype" in the chat, the demo shows the handoff: notification, context summary, a rep joining, replying, handing
  back or closing. Added section 3.4 (presence states, copy), rules R30 to R33, component 14, and section 6.4 (an
  in-page workspace stand-in; the real workspace is not in this repo).
- Work email stays preferred for follow-up; phone remains an optional alternative (assumed).
- Unverified product topics (integrations, pricing, security and data, setup timelines) stay "a person can tell you".
- Hold copy now says someone has been told, which is true once the workspace notification exists.

**Status:** design only. No widget code changed.

**Open:** workspace layout or screens to match; demo rep name and style; whether the assistant resumes fully after a
hand back (backend decision D2 assumes restricted until a rep resolves).

---

### 2026-11-12 — Owner review of the conversation design plan (three changes)

**Context / trigger:** Owner reviewed `northstar/CONVERSATION_DESIGN.md`.

**Decisions:**
- **R2 changed** from "one question per turn" to "one topic per turn", allowing a small cluster of closely related
  items (max 3, all optional, partial answers accepted, never mixing topics). Added section 4.2 with the tests and
  example clusters, including a contact cluster (name, work email or phone).
- **R15 replaced.** The "be honest about the prototype" rule is removed. Visitor copy talks about the product, not the
  demo, and never mentions lead capture, lead status, scoring, fit checks, or whether anything is collected. Honesty
  about the product itself stays in R12 and R13.
- **New Part 0 (vision and language):** the visitor must understand every line, whatever their industry; the goal is
  interest and trust leading into the sales process; the lead-capture goal stays internal; a word list of internal
  terms that stay out of the chat. Rules V1 to V4.
- **Orient stage and knowledge:** Orient is the longest stage; evidence is gathered quietly (never secretly) and
  asked only when needed. New rules R25 to R29 and section 4.3, a deterministic approved `KNOWLEDGE` table now with a
  RAG-ready contract (answer only from approved passages, retrieval never decides, no-match goes to a new
  knowledge-gap recovery). Recovery copy revised to match, plus new copy for answer-then-ask and knowledge gaps.

**Status:** design only. No widget code changed; `scenarios.js` still contains the older wording (audit list in Part 0).

**Open:** the owner must supply which product facts are verified; where the demo's limits are stated if not in the chat
(R15); confirm the optional phone and preferred work email (R18).

---

### 2026-11-12 — Decisions on the conversation-quality proposal; full design plan drafted

**Context / trigger:** Owner could not judge order and turn-taking without conversation-design foundations, so asked
for the whole plan first and for the agent to draft the copy.

**Decision:**
- Order approved (delegated to me): recovery, then turn-taking, then pacing, then tone doc. Reason: fix what blocks the
  visitor before what only feels slightly off.
- Turn-taking: queue first, cancel later and only with a guard for committed routes (frustration, human request).
- **Supersedes the earlier "owner drafts copy" choice:** the agent drafts recovery copy per stage and scenario, the
  owner reviews and marks lines that sound off.
- Home for principles: `northstar/CONVERSATION_DESIGN.md`. Case-study write-up wanted at the end.

**Output:** `northstar/CONVERSATION_DESIGN.md`: components, 24 rules, stage map, decision table, evidence plan,
recovery ladder with drafted copy for every stage, turn-taking and pacing spec, tone guide, measurement plan, glossary.

**Status:** design only. No widget code changed. Pacing values and recovery copy are untested drafts.

**Follow-ups:**
- [ ] Owner reviews the copy in section 5.4 and the three open questions in section 10.
- [ ] Then implement recovery (small commits), run conformance and pytest, report honestly.

---

### 2026-11-12 — Design proposal: Northstar conversation quality (awaiting owner approval)

**Context / trigger:** Impact assessment flagged recovery and turn-taking as high. Owner also wants this work to
double as conversation-design practice, aligned to two role profiles: a Staff UX Designer for Conversational AI
(experience direction, recovery, turn-taking, pacing, trust, handoffs, principles and frameworks, research from
interaction data) and a conversation / prompt designer for LLM sales agents (diagnose from transcripts, hear what
sounds scripted, routing between answer / clarify / escalate / decline, contracts, prove a fix worked).
**Status: proposal only. No code changed.**

**What the code actually shows (corrections to the planning assessment; `scenarios.js` now read):**
- The canned line in `engine.js` `applyNode` ("I don't have a scripted path…") only fires for an *unknown node id*. It is
  effectively dead. The live recovery problem is the 56 per-node `fallback` entries in `scenarios.js`. 36 of them are
  `next: null` (stay on the node), so the same sentence repeats. Conformance case L1-vague-loop (widget) fails with the
  identical reply five turns in a row. P2 and others re-ask questions.
- The fit-question state already exists (`state.answered`, `FIT.questionNodes`, `FIT.tagNode`, `fitChecks`). Recovery can
  reuse it. A full memory model is still roadmap step 5.
- `run_widget.mjs` detects `fallback_used` by matching the node's own fallback text. A recovery reply that replaces
  fallback text is therefore not counted as a fallback. I will **not** treat a drop in `fallback_rate` as proof. Evidence
  of improvement is L1, `repeat_rate`, P2 `question_reasked`, and a manual transcript review. I will not edit the observer.
- Baseline today (widget): pass 0.575, route_accuracy 0.745, false_escalation 0.137, missed_intervention 0.111,
  fallback 0.188, repeat 0.083. pytest and the 3 known xfails are untouched by widget work.
- Routing misses (many `route=none` failures, e.g. B2, B5, P3) are a keyword-coverage problem. That is the
  step 7 LLM interpreter's job. It is out of scope here and I will not tune patterns to the cases.

**Proposal, in priority order:**

1. **Evidence-seeking recovery (replaces repeating fallbacks).** A recovery ladder driven by a per-node miss counter:
   - Miss 1: say what was understood (reuse the `fit.ack` pattern), then ask the single most useful missing-evidence
     question (next unanswered fit question), offered with suggested-reply chips. Keep the node's own fallback copy where it is
     already good.
   - Miss 2: narrow it to a choice (chips only) and say what a rough answer unlocks.
   - Miss 3+: stop probing. Offer the human path or an explicit "that's enough" exit. Never the same sentence twice.
   - Copy lives in `scenarios.js` (a `RECOVERY` table keyed by tier and missing-evidence tag). The engine only selects.
   - Guards: never fires in the alert hold, on human requests, or on minimal replies (`quiet.*` handles those).
2. **Turn-taking.** Options: (A) keep the lock, (B) enable the input while typing and queue sends FIFO, (C) a new message
   cancels the pending reply. **Recommend B now, C later and only for non-committed replies.**
   - Replies land atomically after a timer, so cancelling is easy. The danger is cancelling a decision: a frustration or
     human-request route must never be dropped by a correction. So under B nothing is dropped.
   - Restart bumps the existing epoch, which also clears the queue. Queue cap 2.
   - Accessibility: the input stays focusable (no focus loss from `disabled`), announcements unchanged. Conformance calls `send`
     sequentially, so it is unaffected.
   - Presentation-only: `widget.js` stops disabling the input. `engine.js` owns the queue.
3. **Length-aware pacing.** `delay = clamp(min, base + chars × perChar, max)` from `config.js`, 80 ms under reduced motion.
   Cost: `respond` currently computes the delay before `resolve()`, and `resolve`/`applyNode` mutate state (`seen`,
   `fitChecks`). I would split into compute (pure) then commit, so length is known before waiting. Later, for an LLM:
   `wait = max(pacing floor, real latency)` so the indicator absorbs latency while decisions stay deterministic.
4. **Tone for evidence gathering** (a checklist for copy review, written to `northstar/CONVERSATION_DESIGN.md`):
   acknowledge before asking; one question at a time; say why it is asked; make the cheapest answer easy (chips); allow
   declining with no penalty; ask only what changes the routing decision; no urgency, no mirrored excitement, no
   defending (already the stated "never" list in `DEMO_SCRIPTS.md`); keep the AI disclosure; vary wording across tiers.
5. **Determinism.** Every selection is a pure function of `(nodeId, misses, answered, alert, fit tags)`. No randomness
   (variation is by tier, not by dice). The queue and pacing are presentation timing and never change which node plays.
   Alert/hold, handoff, and the email-domain gate are untouched. Copy is data. A future LLM may only phrase a tier inside
   an approved response contract (roadmap 4/7).

**Learning layer (how this maps to the two role profiles):**

| Skill asked for | Where it is practised here | Artifact to keep |
|---|---|---|
| Diagnose from transcripts; explain how you knew a fix worked | L1, P2, M1 before/after; manual transcript read of 56 fallbacks | Diagnosis log with hypothesis, change, measured result |
| Hear scripted / off-tone copy | Rewrite of the repeating fallbacks against the tone checklist | Copy audit (before/after pairs) |
| Routing: answer / clarify / escalate / decline | Recovery ladder + guards | Decision table (one page) |
| Recovery, trust, handoff across a journey | Tiers ending in the human path | Recovery pattern with rationale |
| Turn-taking, interruption, latency, pacing | Items 2–3 (text analogues of barge-in and end-of-speech) | Note on how each maps to a voice channel |
| Reusable principles and frameworks | `CONVERSATION_DESIGN.md` | Principles with evidence |
| Contracts and measurement | Deterministic selection plus conformance gates | Metrics before/after, honest regressions |
| Storytelling / influence | Short case study at the end | Portfolio write-up |

Method per change: write the hypothesis, read real transcripts, state the principle, change the smallest thing, measure,
write what surprised me.

**Decision:** pending owner. Nothing implemented.

**Why:** Highest-leverage failures first. Recovery has measurable loops today. Turn-taking depends on the same `send` path.
Pacing needs the compute/commit split, so it goes after recovery.

**What would change my mind:** Transcript review showing the real failures are routing misses, not recovery. Then recovery
effort drops and keyword/label work moves up the list.

**Open questions for the owner:**
- [ ] Approve the order (recovery, turn-taking B, pacing, tone doc)?
- [ ] Turn-taking: queue (B) first, or go straight to supersede (C) with the committed-route guard?
- [ ] Learning mode: should I draft recovery copy and you critique it, or should you draft the copy and I critique, wire it in and measure?
- [ ] Is `northstar/CONVERSATION_DESIGN.md` the right home for the principles, and is the case-study write-up wanted?

**Follow-ups:**
- [ ] After approval: implement in small commits, run `./intent-agent-v2/conformance/run_all.sh "$PWD/northstar"` and
  `cd intent-agent-v2 && python3 -m pytest -q` after each, and report any regression plainly. Record baselines only if
  nothing regressed.

---

### 2026-11-12 — Product vision: Intelligent Intake & Decision Routing

**Context / trigger:** Writing down what I am trying to achieve with the lead agent product.

**Thinking:**

The product category is **Intelligent Intake & Decision Routing**. This is a potential product category, not an established industry standard.

The five stages:

1. **Intake:** What is being requested?
2. **Interpretation:** What does the request actually need?
3. **Qualification:** Is it qualified, eligible, and suitable?
4. **Matching and routing:** Where should it go, and why?
5. **Disposition and feedback:** What happened after routing?

**Decision:** _(none yet; this is the framing)_

**Open threads** (my notes, not decisions; edit or delete):
- Which stages does the current code cover? Possible mapping to check: `signals/extractor.py` for interpretation, the `clients/sierra` fit criteria for qualification, and `collaboration/` handoff for routing. Stage 5 (disposition and feedback) may be the least built.
- Do roadmap steps 5 to 7 in `intent-agent-v2/CLAUDE.md` (memory, qualification separation, LLM interpretation) line up with these five stages?

**Follow-ups:**
- [ ] Map each stage to current code and demo scenarios, and note the gaps.

---

### 2026-11-12 — Cloud environment for the repo

**Context:** Setting up a Claude Cloud dev environment, with the current priority on the Northstar frontend.

**Findings (from inspecting the repo):**
- `northstar/` is plain static HTML, CSS and ES modules. It has no package manager, no build step and no network calls.
- `intent-agent-v2/` core uses only the Python standard library. Its only declared dependencies were `pytest` and `pytest-cov`.
- `tests/test_phase0_api.py` also needs `fastapi` and `httpx`, which were not declared.
- With those installed: 304 passed, 3 xfailed. The 3 xfails are the known roadmap step-3 autonomy-profile gaps.

**Decisions:**
- Personal environment `lead-intelligence-agent`: limited network, package registries only, no extra hosts, no secrets, no variables.
- Setup script: `pip install pytest pytest-cov fastapi httpx`.
- Added `fastapi` and `httpx` to `intent-agent-v2/requirements.txt`, so the script can later become `pip install -r`.
- Do not allow LLM provider hosts yet. This keeps the deterministic-demo constraint intact.

**Follow-ups:**
- [ ] Switch the saved setup script to `cd intent-agent-v2 && pip install -r requirements.txt` (needs approval).
- [ ] Verify the setup script in a fresh session. It has not been proven yet.

---

## Entry template

```
### YYYY-MM-DD — Title

**Context / trigger:**
**Thinking (options considered, trade-offs):**
**Decision:**
**Why:**
**What would change my mind:**
**Follow-ups:**
```
