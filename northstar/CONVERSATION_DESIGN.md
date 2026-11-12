# Northstar conversation design plan

Status: **design draft, not implemented.** Nothing in `scenarios.js`, `engine.js` or `widget.js` has changed.
Written 2026-11-12. Companion to the proposal in `PLANNING_LOG.md`.

How to read this: Part 1 is the big picture (what conversation design is made of). Part 2 is the rules.
Part 3 is the conversation map, stage by stage, tied to the scenarios in `scenarios.js`. Parts 4 to 6 are
the specs (evidence, recovery with drafted copy, timing). Part 7 is tone. Part 8 is how we measure.
Part 9 is a glossary, so the vocabulary is in one place.

---

## 1. The big picture: what a conversation design is made of

The Northstar widget is not a chatbot that "answers questions". Per the product framing, the lead agent is an
inbound decision-and-routing system, and the widget is one channel for **gathering evidence under trust
constraints**. So every part below serves one loop: *understand → gather the next piece of evidence → decide
(deterministically) → say what happens next.*

| # | Component | The question it answers | Where it lives today |
|---|---|---|---|
| 1 | **Purpose and persona** | Who is the agent, what is it for, what will it never do? | `config.js` welcome, `DEMO_SCRIPTS.md` "always / never" |
| 2 | **Signals (understanding)** | What did the visitor just tell us or ask for? | `GLOBAL_ROUTES`, node `routes`, `extractFit` |
| 3 | **Dialogue stages** | Where are we in the conversation, and what comes next? | `SCENARIOS`, node ids (`curious.*`, `promising.*`…) |
| 4 | **Evidence model** | What do we need to know, in what order, and what have we already got? | `FIT`, `state.fit`, `state.answered` |
| 5 | **Decision points** | When do we answer, ask, decline, hand off, or hold? | `evaluateGate`, `alert.*`, `GLOBAL_ROUTES` order |
| 6 | **Response library** | What exactly do we say? | `NODES[...].replies` (copy lives here, never in UI code) |
| 7 | **Recovery (repair)** | What do we do when we did not understand, or cannot help? | per-node `fallback` (to be redesigned, Part 5) |
| 8 | **Turn-taking and pacing** | Who speaks when, how long do we wait, can the visitor interrupt? | `typingDelayMs`, `typing` lock (to be redesigned, Part 6) |
| 9 | **Trust and disclosure** | Do they know it is an AI, what is stored, what is simulated? | welcome message, `trust.*`, "simulated" wording |
| 10 | **Handoff** | How does a person take over, and with what context? | `intervention.*`, `alert.*`, `contact.*` |
| 11 | **Memory** | What do we already know, so we never re-ask? | `answered`, `fit`, `seen` (full model is roadmap step 5) |
| 12 | **Measurement** | How do we know it got better? | `intent-agent-v2/conformance/` |

Who owns what (the architecture rule): **deterministic code owns decisions** (which node plays, hold, handoff,
fit gate). **Copy is data** (`scenarios.js` / `config.js`). **The UI only presents.** A future LLM may only
(a) interpret the visitor's words into a frozen label set and (b) phrase a reply inside an approved contract.

---

## 2. The rules

Each rule has a reason and a place it is enforced. Numbers are stable so they can be cited in reviews.

**Understanding and evidence**
- R1. **Ask only what changes the next decision.** Every question must map to a fit tag or a routing outcome. If we would do the same thing either way, do not ask.
- R2. **One question per turn.** Never stack two asks.
- R3. **Say why you are asking**, in one short clause, the first time the question type appears. (Existing `tone: "cue"` messages do this.)
- R4. **Never re-ask what you already know.** A fact the visitor stated, or a question they declined, is marked answered. (`state.answered`; step 5 formalises it.)
- R5. **Make the cheapest answer easy.** Offer suggested replies for every question. Free text always works too.
- R6. **A refusal is an answer.** "I'd rather not say" closes that question, with no penalty and no second attempt.

**Recovery**
- R7. **Never say the same sentence twice in a row.** Recovery escalates by tier (Part 5), it does not loop.
- R8. **Recovery narrows, never widens.** Each tier asks for less than the last.
- R9. **Say what you understood before asking for more** ("Thanks, I've noted…"), so the visitor knows they were heard.
- R10. **Three misses end the probing.** The third tier always releases the visitor: a person, a skip, or a stop.
- R11. **Recovery never fires in a hold or after a human request.** Those states have their own rules (R16, R17).

**Trust, authority, handoff**
- R12. **Always disclose AI, and answer "are you a bot?" directly**, every time it is asked.
- R13. **Do not claim what you cannot verify.** No prices, guarantees, dates, SLAs, reviews or security details. Say so plainly and route to a person.
- R14. **Do not push.** No urgency language, no mirrored excitement, no defending. A buying signal triggers a fit check, not a handoff.
- R15. **Be honest about the prototype.** Any handoff or note is described as simulated. Nothing is stored or sent.
- R16. **Frustration holds the conversation.** Once frustrated, the agent stops answering on its own, and holding replies must still vary (never verbatim).
- R17. **A request for a person is honoured at once**, with no detour through more questions. A second request gets a shorter reply.
- R18. **Contact details only after real interest or a human request, company email only.** Always skippable.

**Timing and interaction**
- R19. **The visitor can always speak.** The input is never locked while the agent is "typing" (Part 6).
- R20. **Never drop a decision.** A frustration or human-request message is always processed, even if it arrives mid-reply.
- R21. **Pacing follows length.** Short replies arrive quickly, long ones after a longer beat, never instant and never slow. Reduced-motion users get the minimum delay.
- R22. **Accessibility is not optional.** New messages are announced politely, focus never falls to `<body>`, restart drops in-flight replies.

**Determinism**
- R23. **Same inputs, same reply.** Every selection is a pure function of state. Variety comes from tiers and rotation by count, never from random choice.
- R24. **No copy in presentation code.** `widget.js` and `engine.js` select. `scenarios.js` and `config.js` speak.

---

## 3. The conversation map

### 3.1 Stages (the spine of every conversation)

```
 OPEN ──► ORIENT ──► GATHER EVIDENCE ──► DECIDE ──► ROUTE / CLOSE
 welcome   explain     one question       fit gate    handoff, note,
 + starters  why       at a time          (pure)      exit, or "not yet"

 Side states, reachable from anywhere:
   TRUST   (are you a bot? burned before? who is accountable?)
   HOLD    (frustrated: agent stops, person takes over)
   QUIET   (minimal replies, "need to think", returning later)
   LIMIT   (pricing, setup, legal, guarantees: decline + route)
```

### 3.2 Stage to scenario to node map

| Stage | Scenario / persona | Nodes in `scenarios.js` | Evidence it collects or decision it makes |
|---|---|---|---|
| **Open** | all | welcome message, starters, `quiet.patient` | Intent of the visit, whether they are exploring, worried, or asking how it works |
| **Orient** | A Curious (Ghoster) | `curious.business`, `curious.process`, `curious.keep` | Business type; how leads are judged today |
| **Orient** | B Hesitant (Skeptic) | `hesitant.ack`, `hesitant.privacy`, `hesitant.boundaries`, `trust.*` | The specific worry; what they need to test |
| **Orient** | C Promising (Eager buyer) | `qualify.explain`, `product.intro` | Consent to be asked about their process |
| **Gather** | C Promising, Poor fit | `promising.scale / process / volume / outcome` | Volume, process and tools, pain, desired outcome (the four fit tags) |
| **Decide** | C, Poor fit | `__fit_gate__` → `buyer.handoff`, `buyer.mismatch`, `buyer.unclear`, `buyer.fitcheck(_again)` | confirmed / poor / unclear fit |
| **Limit** | D Unsupported commitment | `unsupported.honest / timeline`, `pricing.person`, `setup.person`, `trust.accountability`, `trust.reviews` | Decline, say why, route to a person |
| **Route** | E Human intervention | `intervention.explain / again / noted / close`, `contact.*` | Person path, optional work email, simulated note |
| **Hold** | Frustrated | `alert.handoff / noted / hold` | Agent stops; no product answers |
| **Quiet** | Ghoster | `quiet.*`, `pause.normalize`, `share.summary`, `eval.pilot*`, `stakeholder.open` | Patience, shareable summary, timeline honoured |

### 3.3 Decision table: what the agent does, and who decides

| Situation | Action | Decided by |
|---|---|---|
| Visitor says they are frustrated (about the agent or in general) | **Hold**, hand off, stop answering | `GLOBAL_ROUTES.frustration`, deterministic |
| Visitor asks for a person | **Escalate** now | `GLOBAL_ROUTES.human` |
| "Are you a bot?" | **Answer directly** | `GLOBAL_ROUTES.identity` |
| Asks for a guarantee, date, price, legal, security | **Decline plainly + route to person** | `unsupported*`, `pricing`, `setup`, `human` keywords |
| Buying signal ("ready to move forward") | **Fit check**, not handoff | `__fit_gate__` |
| States evidence ("about 300 leads a month") | **Acknowledge, mark answered, ask next gap** | `extractFit` → `fit.ack` |
| Answers the node's question | **Advance** | node `choices` / `routes` |
| Says nothing useful ("ok", "hmm", ".") | **Patient reply**, no pressure | `isMinimal` → `quiet.*` |
| Not understood | **Recover** (Part 5), tier by miss count | proposed: `RECOVERY` table |
| Refuses a question | **Respect, mark answered, move on** | proposed (R6) |
| Off-topic | **State scope, redirect** | proposed (Part 5.3) |
| Corrects themselves mid-reply | **Queue; acknowledge in the next reply** | proposed (Part 6) |

---

## 4. Evidence plan (what the widget is trying to learn)

| Evidence (fit tag) | Why we need it (what it changes) | Asked by | Stated-in-free-text patterns |
|---|---|---|---|
| Inquiry volume (`low` / `mid` / `high_volume`) | Below ~150/mo a person beats software; ≥250 is a strong fit | `promising.scale` | `parseVolume` |
| Tools in place (`existing_crm` / `no_systems`) | A CRM is a fit signal; no systems is a poor-fit signal | `promising.process` | `FIT.patterns.crm / noSystems` |
| Triage pain (`triage_pain`) | The problem this product solves | `promising.volume` | `FIT.patterns.triage` |
| Automation goal (`wants_automation`) | Wants the outcome the agent delivers | `promising.outcome` | `FIT.patterns.automation` |

Rules for this plan: ask at most 3 fit questions (`fitChecks`), skip any already stated (R4), accept "not sure"
as an answer (R6), and never ask about fit once frustrated or after a human request.
These thresholds are **demo heuristics**, not the product's real scoring.

---

## 5. Recovery design (with drafted copy)

"Recovery" (also called repair) is what the agent does when the conversation is not working but nothing has
crashed: it did not understand, the answer was vague, the visitor is off-topic, or the agent is not allowed to
answer. The goal is that the visitor never feels stuck and never hears the same line twice.

### 5.1 Why the current fallbacks are not enough

The engine has 56 per-node fallbacks. 36 of them stay on the same node, so the visitor can get the identical
sentence again and again (conformance case L1 shows five identical replies in a row). Several only say "even a
rough picture helps", which does not tell the visitor *what* kind of answer would help.

### 5.2 The cause taxonomy (recovery depends on *why* it failed)

| Cause | Example visitor message | Right response |
|---|---|---|
| **No match** | "it's complicated" | Ladder (below) |
| **Vague / minimal** | "ok", "maybe", "." | Patient reply, narrow the ask, never chase (Ghoster rules) |
| **Out of authority** | "How much is it?" | Decline plainly, route to a person (existing nodes) |
| **Off-topic** | "What's the weather?" | State scope in one line, redirect (5.3) |
| **Refusal** | "I'd rather not say" | Respect it, mark answered, move on (R6) |
| **Frustration** | "this is useless" | Not recovery. Hold (R16) |
| **Correction** | "No, I meant…" | Not recovery. Turn-taking (Part 6) |

### 5.3 The ladder (for "no match" and "vague")

Selected by a per-node miss counter that resets when the visitor gives a usable answer. The pure function is
`(nodeId, misses, answered, alert)`.

| Tier | Job | Shape |
|---|---|---|
| **1. Narrow** | Show we heard them, make the answer easier | acknowledge → why we ask → a smaller, concrete ask |
| **2. Choose** | Remove the need to write | one line, then the node's own suggested replies |
| **3. Release** | Stop probing | mark the question answered, offer a person or an exit, move on |

Guards: never in `alert` (hold) or right after a human request; the third tier always ends the probing; the
copy for a tier is never identical to the copy for another tier of the same node.

### 5.4 Drafted recovery copy, stage by stage

Conventions: *T1/T2/T3* = tier. "Chips" = the node's existing suggested replies stay visible. "→" = where tier 3
moves the conversation (same destination as today's fallback where it already advances). All copy keeps the AI
disclosure, avoids promises, and describes handoffs as simulated.

**Open (welcome, a first message we cannot place)**
- T1: "I may have missed what you're after. I can explain how Northstar's agent works, help you see whether it fits your sales process, or answer questions about getting started. Which is closest?" *(starters stay visible)*
- T2: "No need to word it perfectly. Pick the one that's nearest, or just tell me what you were hoping to find out."
- T3: "That's fine. I'll start with the basics, and you can steer me from there." → `product.intro`

**A. Curious, business (`curious.business`)**: missing: kind of company
- T1: "That's okay. I only ask so my examples fit you. A few words is plenty, like \"B2B software\" or \"a consulting firm\"."
- T2: "Let me make it easier. Does one of these come close?" *(chips)*
- T3: "No need to label it. We can skip this and look at how you handle inbound leads instead." → `curious.process`

**A. Curious, process (`curious.process`)**: missing: how leads are judged today
- T1: "Thanks. Even one word helps here: when a lead comes in, does a person look at it first, a tool, or nobody in particular?"
- T2: "Which of these is nearest to what happens?" *(chips)*
- T3: "It's fine if it's messy. I'll take that as \"no consistent process\" unless you tell me otherwise." → `curious.contact`

**A. Curious, contact (`curious.contact`)**: missing: whether they want a follow-up
- T1: "No pressure either way. If you do want a follow-up, a work address like name@yourcompany.com is all that's needed, and it's only so a person can reach you."
- T2: "You can share one, keep exploring here, or stop. Which would you like?" *(chips)*
- T3: "Then we'll leave contact details out. Nothing here depends on them." → `curious.close`

**B. Hesitant, worry (`hesitant.ack`)**: missing: which concern
- T1: "You don't need to name it exactly. Is it closer to the agent saying something wrong, pressuring people, or what happens to the details people share?"
- T2: "Pick the nearest, or tell me in your own words." *(chips)*
- T3: "We can leave it there. If you'd rather a person talk this through, I can show you that path." → `intervention.explain` as a chip, no forced move

**B. Hesitant, privacy / boundaries (`hesitant.privacy`, `hesitant.boundaries`)**
- T1: "Just to be sure I answer the right thing: is it about what you'd have to share, or about what the agent says to prospects?"
- T2: "Which of these is closest?" *(chips)*
- T3: "I'd rather not guess at the worry. A person can answer this directly, or we can pause here." → chips: person / pause

**B. Trust cluster (`trust.skeptic`, `trust.burned`, `trust.honest`, `trust.morework`, `trust.reps`, `trust.incentive`, `trust.nosell`)**
- T1: "No need to be precise. One detail is enough: what would you want to see or test first?"
- T2: "Here are a few ways to test me. Pick whichever you like." *(chips)*
- T3: "I don't want to keep guessing at what would help. A person can take your question directly, or we can leave it here." → person / stop chips

**C. Promising, scale (`promising.scale`)**: missing: monthly volume
- T1: "A rough range is fine. I only use it to judge fit. Is it closer to dozens, a few hundred, or thousands a month?"
- T2: "Pick the nearest, or \"not sure\" is fine too." *(chips)*
- T3: "Okay, I won't guess a number for you. I'll carry on with what you've told me." → `__fit_next__`, marked answered

**C. Promising, process (`promising.process`)**: missing: what happens to a new inquiry
- T1: "Even one word helps. Who sees a new inquiry first: a person, a tool, or no one in particular?"
- T2: "Which of these is nearest?" *(chips)*
- T3: "That's enough to go on. I'll leave this one." → `__fit_next__`, marked answered

**C. Promising, pain (`promising.volume`)**: missing: the harder problem
- T1: "No need to be exact. If you think about last week's inquiries, what bothered you most?"
- T2: "Pick the closest, even if none is perfect." *(chips)*
- T3: "Fair enough. I'll note that this part is unclear rather than guess." → `__fit_next__`, marked answered

**C. Promising, outcome (`promising.outcome`)**: missing: what "better" looks like
- T1: "Think of your best possible week. What would be different for your reps?"
- T2: "Which of these sounds most like it?" *(chips)*
- T3: "That's enough for me to describe a responsible next step." → `__fit_next__`, marked answered *(unchanged: this one is already good)*

**Decide, offer a person (`buyer.handoff`)**
- T1: "No rush. I can pass this along whenever you say so, or we can keep talking first."
- T2: "Would you like to share a work email, wait a bit, or keep asking questions?" *(chips)*
- T3: "Let's leave it here. Nothing is sent unless you choose to, and the chat stays open."

**Decide, not a fit yet (`buyer.mismatch`, `buyer.growth`)**
- T1: "I know that isn't the answer you hoped for. If you expect your volume to change, tell me roughly when and I'll note it."
- T2: "Would one of these be useful?" *(chips)*
- T3: "I'll leave it there. You're welcome to come back when it's closer, or a person can weigh in."

**Decide, unclear (`buyer.unclear`)**
- T1: "I'd rather not guess. Would a person looking at this with you be more useful, or shall we keep talking here?"
- T2: *(chips: person / keep talking)* "Either works for me."
- T3: "Either is fine, and I won't push one. Say the word when you want to pick it up."

**Limit, commitments (`unsupported.honest`, `unsupported.timeline`)**
- T1: "To be clear, I still can't promise that. I can do two useful things: explain how the agent is meant to behave, or have a person review your request."
- T2: "Which would help more?" *(chips)*
- T3: "That's a question a person should answer, so I'll show you how that works." → `intervention.explain`

**Limit, pricing / setup (`pricing.person`, `setup.person`)**
- T1: "I can't give you a number or a timeline. A person can. Would you like that route, or shall we keep exploring?"
- T2: *(chips)* "Either is fine."
- T3: "A person is the right place for this, so I'll show you that path." → `intervention.explain`

**Compare (`eval.compare`)**
- T1: "Pick one thing that matters most, such as honesty, fit, or setup effort, and I'll stay with that."
- T2: "Which of these is nearest?" *(chips)*
- T3: "I can't compare other products reliably, so a person is a better source for that." → `intervention.explain`

**Route, human path (`intervention.explain`, `intervention.again`)**: a person was already requested
- T1: "A person is still the right next step. You can share a work email, leave a note without one, or stop here."
- T2: "Which would you like?" *(chips)*
- T3: "I'll leave a simulated note so nothing you said is lost. No one has been contacted." → `intervention.noted`

**Route, contact capture (`contact.ask`, `contact.personal`)**
- T1: "A work address looks like name@yourcompany.com. It's only so a person can follow up, and nothing is stored here."
- T2: "You can also skip. I can leave a simulated note without any contact details."
- T3: "Skipping is fine. Nothing here depends on it." → `intervention.noted`

**Pilot, stakeholders (`eval.pilot`, `stakeholder.open`)**
- T1: "A rough idea is enough. Would it matter more for rep time, how prospects react, or handoff quality?" *(stakeholder: safety, cost, or effort?)*
- T2: "Pick the nearest." *(chips)*
- T3: "That can wait. I can write a short summary you can pass along instead." → `share.summary`

**Quiet / vague (`quiet.patient`, `quiet.return`, `empathy.ack`; minimal replies like "ok", ".")**
- T1: "No rush at all. I'm here whenever you want to pick this up, and it's completely fine not to." *(existing, kept)*
- T2: "Still here. If it helps, I can answer one small question, like what Northstar does, or we can stop."
- T3: "I'll leave it there. The chat stays open whenever you come back."

**Hold (`alert.hold`)**: *not a recovery ladder.* The agent stays on hold, but repeated holding replies must vary (R16, and the widget twin of the backend gap POL-26).
- Hold 1: "I'm holding here so a person can take this over. I won't keep answering on my own, because that isn't what would help." *(existing, kept)*
- Hold 2: "Still holding. A person should pick this up, so I'm not answering questions in the meantime. You can leave a simulated note below."
- Hold 3+: "Nothing has changed on my side: I'm waiting for a person. The note option is below, or you can restart the chat."

### 5.5 Where this lives (implementation sketch, for later)

- `scenarios.js`: a `RECOVERY` table keyed by *stage group* (above) holding tiers 1 to 3 as `{ text, next? }`, plus a `NODE_GROUP` map from node id to group. Existing per-node `fallback` stays as the default where a node has no group entry.
- `engine.js`: a `misses` counter per node (reset on any understood reply), a pure `pickRecovery(nodeId, misses)`, and guards (R11). Marking the question answered at tier 3 reuses `state.answered`.
- `widget.js`: no change.

---

## 6. Turn-taking and pacing

### 6.1 Turn-taking (decision: queue, not cancel)

Today the input is disabled while the agent is "typing", so the visitor cannot correct themselves. We change
that in two steps.

- **Step 1 (planned): enable the input and queue.** Messages sent during a reply are held in order (max 2) and
  handled after the reply lands. No message is dropped, so a frustration or human request (R20) can never be
  lost. The input stays focusable, so there is no focus loss (R22). A restart clears the queue and in-flight
  replies via the existing epoch (R22).
- **Step 2 (later, only with a guard): cancel.** A new message may cancel a pending reply *only if* that reply is
  not a decision (alert, human, handoff). Needs the compute/commit split from 6.2.
- **Acknowledging a correction:** the reply to a queued message begins by showing it heard the correction
  (R9), for example "Thanks, I'll go with that instead."

### 6.2 Pacing (length-aware)

```
delay = clamp(MIN, BASE + chars * PER_CHAR, MAX)   // reduced motion: 80 ms
```

Starting values, **to be tuned by reading real sessions** (not tested yet): `MIN 500 ms`, `BASE 350 ms`,
`PER_CHAR 8 ms`, `MAX 2200 ms`. They live in `config.js`. A short ack arrives fast. A 400-character
explanation takes about 2 seconds.

Engineering note: `respond()` waits *before* it resolves nodes, and resolving changes state. To know the length
first we split it into a pure *compute* step (which replies would play) and a *commit* step. When an LLM later
phrases replies, the wait becomes `max(pacing floor, real latency)`, so the typing indicator hides latency
while decisions stay deterministic.

### 6.3 Voice analogues (kept so this ports to a voice channel later)

| Text today | Voice equivalent |
|---|---|
| Typing while the agent replies | Barge-in / interruption |
| Queue vs cancel | Whether the agent stops talking on interruption |
| Pacing delay | Response latency and end-of-speech timing |
| Typing indicator | Filler or acknowledgement ("one moment") |
| Chips | Spoken options |
| Tier 3 release | Offering to transfer to a person |

---

## 7. Tone guide for evidence gathering

The voice: **calm, plain, transparent, never pushy.** Written for a busy sales or marketing person.

| Do | Don't | Why |
|---|---|---|
| "Thanks, I've noted tools already in place." | "Great! Awesome!" | Acknowledge, do not mirror excitement (R14) |
| "I'm asking so my examples fit you." | (ask with no reason) | Reason lowers the cost of answering (R3) |
| "Dozens, a few hundred, or thousands?" | "Please provide your monthly volume." | Concrete, easy, human (R5) |
| "That's fine. We can skip this." | "I need this to continue." | Refusal is an answer (R6) |
| "I can't promise that. A person can." | "Unfortunately that is not possible." | Decline plainly, then route (R13) |
| Short sentences, one idea each | Long stacked explanations | Reads fast on a small panel |
| Vary wording by tier | The same stock phrase everywhere | "Sounds scripted" is a trust problem |

**Scripted-sounding audit** (use when reviewing any reply): Would a person say it this way? Does it repeat a
phrase used in the last three turns? Does it say the same thing as the node's cue line? Does it apologise more
than once? Does it end on a clear next step?

---

## 8. Measurement: how we will know it improved

Run after every change touching widget behavior, from the repo root:

```bash
./intent-agent-v2/conformance/run_all.sh "$PWD/northstar"
cd intent-agent-v2 && python3 -m pytest -q   # expect 304 passed, 3 xfailed
```

| What we watch | Why |
|---|---|
| **L1-vague-loop** (identical replies) and `repeat_rate` | Direct evidence that loops are gone |
| **`question_reasked`** in P2 and M1 | Evidence R4 works |
| **Manual transcript read** of each recovery tier | Automated checks cannot hear "scripted" |
| `overall_pass_rate`, `false_escalation_rate`, `missed_intervention_rate` | Must not regress |
| `fallback_rate` | **Caution.** The observer detects a fallback by matching the node's own fallback text, so replacing that text makes the number fall without proving anything. We report it but do not use it as proof, and we do not edit the observer. |

Known baseline (widget): pass 0.575, route_accuracy 0.745, false_escalation 0.137, missed_intervention 0.111,
fallback 0.188, repeat 0.083.

**Diagnosis log template** (one per change): *Hypothesis · Transcript evidence · Principle (rule number) · Change ·
Measured result · What surprised me.* Never weaken `cases.json` to make a number pass.

---

## 9. Glossary

- **Turn**: one message from one side. **Turn-taking**: who speaks when.
- **Intent**: what the visitor wants (here: routes like `human`, `pricing`).
- **Slot / evidence**: a fact we want, like monthly volume.
- **Grounding**: showing the other side we understood ("I've noted…").
- **Repair / recovery**: fixing a conversation that stalled or went wrong.
- **Fallback**: the reply used when nothing matched.
- **Escalation / handoff**: passing the conversation to a person.
- **Hold**: the agent deliberately stops answering until a person takes over.
- **Barge-in**: interrupting the agent mid-reply (voice term; here, typing while it replies).
- **Latency / pacing**: how long a reply takes to appear, and whether that feels natural.
- **Response contract**: the approved shape and limits of what the agent may say (roadmap step 4).
- **Deterministic**: the same input always produces the same output.

---

## 10. Open questions for the owner

- [ ] Review the drafted copy in 5.4. Mark lines that sound off. Those edits are the practice.
- [ ] Approve pacing starting values (6.2), or ask for a "slower / faster" variant to compare.
- [ ] Should tier 3 ever *close* the chat itself, or always leave the visitor a choice (current draft: always a choice)?
