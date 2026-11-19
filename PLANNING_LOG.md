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

### 2026-11-18 — Failure list written from the owner's testing

**Context:** The owner asked for a written failure list based on their test feedback.

**Output:** `northstar/FAILURE_LIST.md`: nine failures the owner reported (F1 to F9) with cause, fix and what remains; eleven more I found in the same flows (R1 to R11), labelled as mine; a sort by cause; and how to re-test each fix.

**Summary:** of the nine reported, six are fixed (pace, highlighted narration, real handoff wording and flow, the false escalation, plus two explained process issues), two are partly fixed (suggestions only hand-written for two steps; interruptions and free-form questions covered for 14 topics), one lasting fix is open (a hosted test address). Of the eleven found by me, all are open; the largest is the ask engine (S6, S10). Two of the nine were my own mistakes (a single pause per reply; not auditing the 18 narration lines against my own rules).

---

### 2026-11-17 — Second owner test: a real handoff in the demo, questions first

**Context:** The owner ran S1 and sent screenshots showing the person path ("prototype", "simulated"), interruptions ignored, and irrelevant answers with "restart".

**Decision (owner):** remove "prototype" and "simulated" from the chat and pretend the handoff is real: the agent stores the customer's information and hands off to live sales reps. Implemented in the demo's own world (rule R50): a lead store, a person who can join, reply, hand back, resolve or close, and a provisional `workspace.html`, so the claims in the chat are true inside the demo. The page around the widget keeps its "scripted prototype, nothing leaves your browser" line (outside the chat).

**Findings:**
- **Interruptions ignored: a design deficit, not an LLM gap.** The original script only understood each step's own answers plus about 25 shared topics. The design already said what to do (answer, or say it cannot) but it was unbuilt. Built now (R49): question-first answering from 14 draft answers, an honest "no reliable answer" ladder, and "Carry on where we left off".
- **The root of the cascade was a keyword false positive** ("our sales reps" read as a request for a person; "reps review leads" as a request for reviews). Fixed narrowly; measured on the existing conformance cases: no change either way.
- **Design vs LLM:** about two thirds of the bad experience is design (coverage, question handling, honest gaps) and can be fixed deterministically; an LLM would help with paraphrase understanding and phrasing, but could not decide what is true to say, which needs the approved knowledge either way.

**Checks:** 43 unit tests pass; conformance widget pass 0.600 and repeat 0.056 unchanged, B2, B4 and B5 now get a real answer instead of a fallback; pytest 304 passed, 3 xfailed; a two-window browser run of the whole loop (visitor asks for a person, shares an email, the rep joins and replies, the assistant stays quiet, the rep resolves, the assistant checks in) clean with no console errors.

**Still open:** the ask engine (S6 and S10 failures); target-aware frustration; the owner's own workspace design to replace the provisional page; approval of the draft answers, including three new product claims (K13 to K15).

---

### 2026-11-16 — First owner test: pacing, highlighted narration, Pigment-style suggestions

**Context:** The owner tried the demo (starting from "How does your agent qualify leads?") and raised two issues, with a Pigment screenshot as a reference.

**Findings and fixes (PR #9):**
- **Too fast:** every bubble of a reply appeared together after one pause. Now one bubble at a time, each with its own typing pause (600 to 1,800 ms by length). Measured in a browser: three bubbles at about 1.8, 3.2 and 4.3 s, previously all at about 0.7 s.
- **Highlighted line:** 18 "cue" lines from the original script (italic, orange bar) narrated the agent's own process. 13 removed, 5 folded into their question; highlight style deleted. New rule R46.
- **Pigment pattern:** suggested replies now split into "Ask me things like:" (about three questions, hideable) and action buttons (R48). Authored for `qualify.explain` and `product.intro`; other nodes use a rule (a label ending in "?" is a question). Per-node suggestion writing remains to do.
- This was partly my miss: the pacing in step 1 delayed the whole reply once, and I did not review the 18 cue lines against my own rules.

**Checks:** 26 unit tests pass; conformance unchanged (widget pass 0.600, repeat 0.056, route accuracy 0.745); pytest 304 passed, 3 xfailed; browser flow clean.

**Open:** tune pacing; review and rewrite suggestions for every node (slice 5); the rest of the open items in `BUILD_PLAN.md`.

---

### 2026-11-16 — Readiness review, and the first build step

**Decision (owner, at the start of this step):** score-bar placeholder accepted; **no partner path in the demo**; deal-value placeholder accepted. Asked me to review all components, decide whether to build, and build; the owner will test.

**Verdict:** go, in slices. Built the parts that are fully specified and not blocked: recovery ladder, repair intents (found missing by measurement), turn queue, length-aware pacing. Deferred, with reasons, in `northstar/BUILD_PLAN.md`: ask engine, knowledge layer, presence and workspace, the word-list copy pass, routing correctness.

**What the review found missing:** a build sequence with acceptance tests; conversation repair; the order in which handoff wording may change (not before the workspace can really tell a person); a conflict between the word list and three conformance cases that expect "evidence" or "fit" (and rules that forbid "let me connect you"); routing false positives as their own work item; a visual spec for the new states; a per-turn trace; an accessibility test plan; a stale duplicate of the widget in `web/`.

**Results:** conformance widget pass 0.575 to 0.600, repeat 0.083 to 0.056, route accuracy / false escalation / missed intervention unchanged; the fallback rate fell 0.188 to 0.116 but that is an artifact of how the observer matches text and is not claimed as evidence; L1 now passes; pytest 304 passed, 3 xfailed; 21 new unit tests pass; browser check clean. Interruptions answered specifically: 42 of 42 (outside the hold), email never asked again after a refusal. Baselines were **not** re-recorded.

**Still failing (named in BUILD_PLAN section 7):** routing false positives (S1 t1, S2 t1 to 2), the ask-after-request and ignored-facts problems (S6, S10), S11 early hold, existing copy wording.

**Commits:** data, engine and widget, tests and eval, docs. No decision in the backend or the data model was changed.

**Open:** approve routing fixes (slice 4); decide how to handle the three conformance cases that expect "evidence" or "fit"; approve the ask-engine design pass and merge of the data model branch; approve knowledge entries, languages and restricted countries; share the workspace code; try the pacing.

---

### 2026-11-16 — ICP decisions, partners, score bar, and the source-verification report applied

**Owner decisions:** marketing leaders are a buyer or champion; **smaller teams with heavy inbound count** (so size is judged by inbound load against capacity, not headcount); "no timeline"
means no plan to buy within **6 months**; supported regions are **EMEA and the Americas** (written "AMS", read as Americas: to confirm); **Northstar also sells to partners**.

**Source verification:** a separate session produced `ICP_SOURCES_VERIFICATION.md` (17 claims: 9 confirmed, 6 corrected, 2 unsupported). I merged that branch (fast-forward) and applied all eleven of its recommendations to `ICP_DRAFT.md`.
I re-checked two points myself: ZoomInfo's "30 leads a day" is a worked example, not a threshold (my earlier draft was wrong), and Kickscale's 15-a-day figure has no study behind it. I could not open the Drift-sunset press release (403) and relied on the report and trade-press summaries.
Corrections included: no "$20K Drift deal size", Drift is being sunset (1mind is the named successor), "native CRM sync ranked first" was wrong, MQL to SQL figures are averages from one agency's data cut two ways, and an HBR 2011 article does exist (about 7x within the hour) but is not the source of the 100x and 21x figures.

**Score bar:** no industry standard exists. Opened sources (Pedowitz, Rework) say to calibrate on closed-won data, and with none to start at 50 to 60 of 100 and review with sales; Rework gives starting points by segment and a dynamic rule. Proposed placeholder: **60 offers a person; 45 to 59 with a strong intent action also does; 40 to 59 otherwise nurtures; under 40 keeps helping.** Calibrate after 50 to 100 handoffs. It is a demo setting and the workspace should say so.

**Partners:** drafted as a second customer type (3.5), a partner kind-of-visit in the interest gauge, and knowledge entries K11 and K12. Not researched.

**Advice recorded:** do not rewrite the verification report. It is a dated record; a resolution table was appended to it instead.

**Status:** design and research only. No widget or backend code changed.

**Open:** "AMS" = Americas; supported languages; restricted countries and the data-handling position; score bar; deal-value minimum; partner types and whether the demo gets a partner path.

---

### 2026-11-15 — ICP evidence verified against source pages (network settings changed)

**Context:** Owner changed the environment's network access. The `WebFetch` tool still could not resolve hosts in this running session, but `curl` through the
session proxy worked, so I opened six sources directly and re-checked the ICP draft.

**What changed in `northstar/ICP_DRAFT.md`:**
- The 100x / 21x response-time figures are **confirmed in the primary document** (InsideSales.com / MIT, six companies, over 15,000 leads) but they measure **phone callbacks only**, were
  vendor-run, and say nothing about chat or AI. Two claims in circulation are **wrong**: the "Harvard Business Review" attribution and a "400% from 5 to 10 minutes" figure (neither is in the study).
- The Workato test of 114 B2B companies (March 2026) finds more than 99% do not respond within 5 minutes, so slow response is near-universal and is not a distinguishing ICP signal on its own.
- The persona evidence (Rework) is for **AI sales ops**, a neighbouring category: 25 to 150 reps, ACV $15K to $150K, 30 to 90 day evaluations, fewer than 10 reps should wait. Qualified now sells to
  **marketing leaders** as an "AI SDR agent". Added a marketing-leader persona, a sales-team-size row, a placeholder deal value, and a note that a 6-month horizon may suit "no timeline" better than 12.
- Their stated objections ("reps won't trust it", "no bandwidth to implement") match scenarios S1 and S5. The RevOps Co-op ownership-lookup advice supports routing an existing customer to the account owner.

**Still true:** no independent evidence; ICP bands, regions and score weights remain proposals.

**Open:** unchanged from the previous entry, plus: include marketing leaders as buyers; the right sales-team-size band.

---

### 2026-11-15 — ICP research, no-budget decision, approved scenarios

**Context / trigger:** Owner answered the open questions and asked for research on the ICP for the Northstar lead product, which is an
**API product that integrates with any CRM**; the widget and the lead workspace are demos of the agent's behavior and its collaboration with humans.

**Decisions (owner):**
- **No budget or timeline = disqualify.** This supersedes my recommendation (nurture) and the data model's nurture route. Implemented in the design as: only on an
  *explicit* statement; unknown or "not yet" stays unknown (R39). The horizon for "no timeline" still needs defining.
- **Five readiness fields confirmed:** budget, timeline, who decides, decision process, security and compliance.
- **Scenarios:** S10 and S11 approved; S7 to S9 parked.

**Research (`northstar/ICP_DRAFT.md`):** a draft ICP (accounts, buying group, triggers, disqualifiers), a score sketch for the "lead score bar", what the widget can and
cannot learn, and an explanation of the demo's small-volume rule (150 and 250 a month vs a rule of thumb of about 300 a month per inbound rep).
**Limits:** no independent (A-grade) evidence; everything is vendor-authored or secondhand from search summaries; four primary pages could not be opened because the
session's network allowlist blocks them (workato.com, www.mortech.com, www.qualified.com, revopscoop.com). The ICP bands, regions and weights are
**proposals, not findings**.

**Evaluation:** S10 and S11 added to the replay set. New baseline `northstar/eval/baseline-2026-11-15.md` (the 2026-11-14 file is replaced; S1 to S6 unchanged).
S10 fails (the visitor gave everything in one message and was asked about it again; the email was not recognised). S11 holds one turn early on frustration about other vendors.
Across eight scenarios, 32 of 32 replies to four interruptions are the same canned fallback and 3 of 8 re-ask the email after a refusal.

**Status:** design, research and evaluation only. No widget or backend code changed; conformance and pytest unchanged.

**Open:** ICP bands, supported regions, score bar, deal-value minimum, the "no timeline" horizon, customer types (direct vs embedding partners), and recording these
decisions in the lead-workspace session's data model.

---

### 2026-11-15 — Shared agent state model (from the lead-workspace session): mapped to this plan

**Context / trigger:** Owner shared that session's Step 0: one agent state model shared by the widget and the rep workspace
(eight moments: answering, nudge, intervention, approval pending, rep driving, advisory, uncertain, failure), ten content
rules, and a decisions log with current or superseded status.

**Findings:**
- The backend already separates the two modes Step 0 leaves undecided: RELAY is `PENDING_APPROVAL` ("rep must approve
  before send"), SHADOW is `REP_SUGGESTION` ("rep owns the live conversation"). So "rep driving" is SHADOW, and the "Advisory" row is the same
  mode seen from the rep's panel. Recommended: keep approval and driving separate; merge the two rows.
- This plan's presence states (3.4) cover answering, nudge, intervention and rep driving. **Gaps:** approval pending (a typing indicator with no
  limit looks broken), failure (the visitor must be told what was not sent), and a link from recovery tier 3 to the rep's "Uncertain" card.
- Wording conflict: "a person is joining" implies a time; use "someone on the team has been told" (R32).
- This plan needs Resolve, Hand back (topic still open) and Close as the rep actions, not one "Hand back".

**Decision:** proposed only, added as 3.5 of `CONVERSATION_DESIGN.md`. Adopt the workspace session's table as the single spine; the visitor
copy here becomes its customer column. Prefix workspace content rules WR-1 to WR-10 to avoid clashing with R1 to R45.

**Status:** design only. No code changed.

**Open:** confirm RELAY and SHADOW stay separate; approve the three visitor-side proposals; merge the two decisions logs when the branches merge.

---

### 2026-11-14 — Lead data model decisions, accept criteria, and a measured evaluation baseline

**Context / trigger:** Owner answered the open data-model questions and supplied six test scenarios and six interruptions
to use for the widget's design test and evaluation.

**Decisions (owner):**
- The visitor is **not always** evaluating Northstar for their own team. They can ask anything; the agent gauges interest and
  whether the visitor is worth nurturing with a person. Added the interest gauge (rule R44) so no question about someone's own
  process is asked before interest is shown.
- **Five readiness fields**; **five criteria to accept a lead** (data validity and reachability, ICP fit, score threshold,
  intent and timing, reachable decision-maker); **five hard disqualifiers** (unsupported geography, invalid contact, no buying
  authority, active customer or open deal, no budget or timeline). Written up in `CONVERSATION_DESIGN.md` 4.5 with the
  conversation behavior for each.
- Owner will use the six scenarios as the test and evaluation set: adopted. See `northstar/EVALUATION_PLAN.md`.

**What I changed and why:**
- Moved "who else weighs in" to L3 and asked region before any contact (accept criteria 2 and 5; do not take contact from
  someone we cannot serve). Added R44, R45.
- Flagged a **conflict**: "no budget or timeline" as a disqualifier vs the data model sending it to nurture. Recommended nurture.
- Flagged what the agent cannot do without owner input: the ICP definition, the supported-region list and the score bar do not exist.
- Added knowledge entry K10 (what it asks about), needed by scenario S6.

**Measured baseline (current widget, before any change; `northstar/eval/`):**
- S1 fail, S2 fail, S3 partial, S4 partial, S5 pass, S6 fail. 24 of 24 replies to four of the six interruptions are the same canned fallback.
  The email is asked again after a refusal in 3 of 6 runs. Identical consecutive replies in S1 and S2.
- Two keyword false positives found ("sales reps" read as a request for a person, "review" as a request for reviews). Recorded, not patched,
  to avoid tuning to the test; candidates for the interpretation step or a narrow owner-approved fix.
- This supports the build order: recovery first.

**Status:** design and evaluation only. No widget code changed.

**Open:** record the decisions in the lead-data-model session; supply ICP, regions and score bar; choose the disposition for no
budget or timeline; approve S7 to S11; confirm the readiness field list.

---

### 2026-11-13 — Question patterns and timing from the lead data model

**Context / trigger:** Owner reviewed `CONVERSATION_DESIGN.md` and found no rules for how the agent asks for lead
information. The lead data model lives in the lead-workspace session, not in this branch.

**Findings:**
- The path the owner gave points at the generic `docs` skill, not the data model. The model is
  `docs/lead-data-model.md` (v0.1 draft) on branch `claude/charming-ptolemy-nr2s9t`, not merged. I read it from that branch.
- It has four layers: A identity and context, B fit, C opportunity readiness, D system-owned. Four decisions in it are
  still open in that session (own-team reading, four or five readiness fields, minimum to accept, hard disqualifiers).

**Decision (proposed, owner to confirm):**
- New section 4.4 and rules R36 to R43: five-part question anatomy, seven ask patterns, a sensitivity ladder L0 to L4
  computed from counted events, a field plan mapped to the data model, and a registry design for later.
- **Timing:** do not lead with identity. Company context (kind of business, size) early as tuning; name and role when the
  assistant starts tailoring or a person is about to join; company name, contact and explicit consent only at the connect
  moment. When a person is live the assistant stops collecting. Treated as a hypothesis to test once there is traffic.

**Status:** design only. No code changed.

**Open:** answer the four decisions in the lead-workspace session; confirm the timing; decide whether to merge the data
model branch before building the registry.

---

### 2026-11-13 — Resolve and hand back; demo knowledge base; copy audit

**Context / trigger:** Owner asked whether the recovery copy really follows the word list, for a demo knowledge base,
and how a rep's involvement ends (what "resolved" means, whether the visitor approves, whether the assistant can
continue on other needs).

**Findings and decisions:**
- **Copy audit:** the earlier rewrite only fixed the lines I had flagged. A full audit found "leads", "prospects",
  "reps" and "handoff" still in visitor copy. All fixed in `CONVERSATION_DESIGN.md` 5.4. Proposed a word-list lint (8).
- **Knowledge base:** none existed (facts live inside nodes). Drafted `northstar/KNOWLEDGE_BASE.md` from the repo's own
  design documents only (nine entries, status `draft`, owner approval needed) plus the confirmed list of unverified
  topics ("a person can tell you"). No product fact was invented.
- **Resolve (proposed D5):** a person resolves (backend `/rep/action` `resolve` already exists); the visitor is asked a
  light check-in but cannot block it, and can reopen at any time. **Scoped hand back:** a person may hand back with a topic
  still open; the assistant stays restricted and fenced off that topic until a person resolves. This is **not built** in the
  backend (an open intervention holds all replies today; related known gaps POL-20 and POL-21, roadmap step 3).
- Lead workspace code and screenshots will be shared in a new session; the stand-in design (6.4) is provisional.
- "Maya" accepted as the demo person placeholder.

**Status:** design only. No widget or backend code changed.

**Open:** confirm D5 and the fence topic list; review knowledge entries; share the workspace code and screenshots.

---

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
