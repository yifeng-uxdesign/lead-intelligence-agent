# Northstar conversation design plan

Status: **design draft, not implemented.** Nothing in `scenarios.js`, `engine.js` or `widget.js` has changed.
Written 2026-11-12. Companion to the proposal in `PLANNING_LOG.md`.

How to read this: Part 0 is the vision and the language rules (what the visitor should feel, and the words we
use). Part 1 is the big picture (what conversation design is made of). Part 2 is the rules.
Part 3 is the conversation map, stage by stage, tied to the scenarios in `scenarios.js`. Parts 4 to 6 are
the specs (evidence and knowledge, recovery with drafted copy, timing). Part 7 is tone. Part 8 is how we
measure. Part 9 is a glossary, so the vocabulary is in one place.

---

## 0. Vision: who we talk to, and what for

**What the visitor experiences.** Someone arrives curious, undecided, or wary. The agent helps them understand
the product, answers honestly, and earns enough trust that they *choose* to take a next step with the team.
The best result is a relationship that carries into the sales process, not a form filled in.

**What the business needs (internal only).** The lead agent exists to capture and route leads. That goal shapes
what the system does behind the scenes. It never shows in what the visitor reads. The visitor should feel helped,
never processed, scored or sold to.

Four principles for everything the visitor reads:

- **V1. Anyone can follow it.** Plain words that a person from any industry or role understands on first read.
  Short sentences. If the visitor used a word, use theirs. Do not assume sales jargon (SDR, MQL, pipeline) unless
  they used it first. Explain a product term the first time it appears.
- **V2. The visitor is a person, not a lead.** No label for them (qualified, unqualified, prospect, lead, "a fit")
  ever appears in copy.
- **V3. No pressure, and no talk about collecting.** We never say or imply that we are, or are not, capturing
  them. Show respect by not pushing, rather than by announcing that we are not.
- **V4. Interest is earned, not extracted.** Give something useful first. Ask after.

**Word list for visitor-facing copy.** The internal words are fine in this document, in code and in traces.
They stay out of the chat.

| Instead of | Say |
|---|---|
| "qualified", "unqualified", "not a fit", "fit check" (about the visitor) | "whether this would suit your team", "make sure this would actually help" |
| "evidence", "signals", "I've noted {fit}" | "what you've told me", "what matters to you" |
| "hand off", "escalate", "intervention" | "connect you with someone on the team", "bring in a person" |
| "lead capture", "we won't store / keep your details", "no contact details needed" | "if you'd like someone to follow up, tell me how to reach you" |
| "I'm not asking this to close a deal", "no sales pitch from me" | (just don't pitch; it shows) |
| "hold", "alert" | "I'm waiting for a person to take this over" |
| "prototype", "simulated" | (describe the product, not the demo; see R15) |

Product vocabulary stays when it describes *their* business and the product's job, for example "inquiries that
come in", "deciding which are worth a conversation". Prefer "inquiries" or "people who get in touch" unless the
visitor says "leads" first.

**Audit of existing copy** (`scenarios.js`, to review at implementation): several lines break V2 or V3 today.
Examples: `curious.contact` ("I'm not asking for this to close a deal"), `buyer.mismatch` ("probably isn't the
right fit"), `fit.ack` ("I've noted {fit_new}"), `product.intro` and `qualify.explain` ("evidence for and against
fit"), and the `contact.*` and `intervention.*` nodes ("simulated", "nothing was stored").

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
| 9 | **Trust and disclosure** | Do they know it is an AI, what is kept? | welcome message, `trust.*` |
| 10 | **Handoff** | How does a person take over, and with what context? | `intervention.*`, `alert.*`, `contact.*` |
| 11 | **Memory** | What do we already know, so we never re-ask? | `answered`, `fit`, `seen` (full model is roadmap step 5) |
| 12 | **Measurement** | How do we know it got better? | `intent-agent-v2/conformance/` |
| 13 | **Knowledge** | What may the agent state as fact, and from which approved source? | Today: facts are hard-written inside nodes. Proposed: an approved `KNOWLEDGE` table now, retrieval (RAG) later (4.3) |
| 14 | **Presence and takeover** | Who is speaking for the company right now (assistant or a person), and how does a person join? | Today: nothing. Proposed: presence state plus an in-page lead workspace stand-in (3.4, 6.4) |

Who owns what (the architecture rule): **deterministic code owns decisions** (which node plays, hold, handoff,
fit gate). **Copy is data** (`scenarios.js` / `config.js`). **The UI only presents.** A future LLM may only
(a) interpret the visitor's words into a frozen label set and (b) phrase a reply inside an approved contract.

---

## 2. The rules

Each rule has a reason and a place it is enforced. Numbers are stable so they can be cited in reviews.

**Understanding and evidence**
- R1. **Ask only what changes the next decision.** Every question must map to a fit tag or a routing outcome. If we would do the same thing either way, do not ask.
- R2. **One topic per turn.** Ask one thing, or one small *cluster* of closely related things that share one
  purpose and are natural to answer in one sentence (for example, a name and how to reach you). A cluster has at
  most three items, every item is optional, and it never mixes topics. If the visitor answers only part of it,
  ask only for what is missing (R4). See 4.2.
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
- R15. **Talk about the product, not the machinery.** Say what the product does and how people work with it.
  Visitor-facing copy never mentions lead capture, lead status, scoring, fit checks, the demo or prototype, or
  whether anything is being collected (V2, V3). Because the demo shows a person genuinely joining (3.4), copy
  about connecting a person is true in the demo too. *(Replaces the earlier "be honest about the prototype" rule, by
  owner decision. Honesty about the product itself stays in R12 and R13.)*
- R16. **Frustration holds the conversation.** Once frustrated, the agent stops answering on its own, and holding replies must still vary (never verbatim).
- R17. **A request for a person is honoured at once**, with no detour through more questions. A second request gets a shorter reply.
- R18. **Ask how to reach them only when they want a person to follow up, or have asked for one.** Always
  skippable. The visitor chooses the channel; a work email is preferred, and a phone number is allowed if they
  offer it.

**Timing and interaction**
- R19. **The visitor can always speak.** The input is never locked while the agent is "typing" (Part 6).
- R20. **Never drop a decision.** A frustration or human-request message is always processed, even if it arrives mid-reply.
- R21. **Pacing follows length.** Short replies arrive quickly, long ones after a longer beat, never instant and never slow. Reduced-motion users get the minimum delay.
- R22. **Accessibility is not optional.** New messages are announced politely, focus never falls to `<body>`, restart drops in-flight replies.

**Knowledge and asking**
- R25. **Value before asking.** Give a useful answer before the first evidence question. Then ask something
  related to what was just said.
- R26. **Ask when needed, not by schedule.** Ask only when (a) a pending decision depends on the answer, (b) the
  visitor invites questions, or (c) there is a natural opening tied to what they just said. Otherwise keep
  answering and listening (4.1).
- R27. **Listen quietly, never secretly.** Pick up what the visitor says along the way (company, volume, tools,
  worries, topics they care about) without interrogating. If they ask what we keep or whether we are taking notes,
  answer honestly (R13) and route specifics to a person.
- R28. **Facts come only from approved knowledge.** If the knowledge base has no answer, say so plainly and offer
  a person. Never improvise a fact (4.3).
- R29. **Knowledge informs, it never decides.** Retrieved content cannot change trust state, hold, or the
  decision to bring in a person. Those stay deterministic.

**Presence and handoff**
- R30. **Always show who is speaking.** Assistant and person messages are visibly different (name, label, style),
  and a person joining or leaving is announced in the thread.
- R31. **The visitor never repeats themselves.** A person who joins has already read the conversation, and their
  first message shows it.
- R32. **Never promise a response time.** Say that someone has been told, not when they will answer (R13).
- R33. **When a person is present, the assistant is silent.** Only an explicit action by the person (hand back or
  close) changes that. Authorization stays on the person's side, never in the visitor's chat.

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

**Orient is the longest stage, on purpose.** It is where trust is earned. Two things interleave: *explaining*
(answering from approved knowledge) and *listening* (quietly picking up what the visitor tells us). No evidence
questions are scheduled here; they come only when needed (R26). Gathering evidence is quiet, not secret (R27).

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
| **Route** | E Human intervention | `intervention.explain / again / noted / close`, `contact.*` | Person path, optional way to reach them, a person joins live (3.4) |
| **Hold** | Frustrated | `alert.handoff / noted / hold` | Agent stops; no product answers |
| **Quiet** | Ghoster | `quiet.*`, `pause.normalize`, `share.summary`, `eval.pilot*`, `stakeholder.open` | Patience, shareable summary, timeline honoured |

### 3.3 Decision table: what the agent does, and who decides

| Situation | Action | Decided by |
|---|---|---|
| Visitor says they are frustrated (about the agent or in general) | **Hold**, hand off, stop answering | `GLOBAL_ROUTES.frustration`, deterministic |
| Visitor asks for a person | **Escalate** now | `GLOBAL_ROUTES.human` |
| A person was notified and joins | Assistant goes silent, thread shows who joined, the person replies | An explicit action in the lead workspace (3.4) |
| "Are you a bot?" | **Answer directly** | `GLOBAL_ROUTES.identity` |
| Asks for a guarantee, date, price, legal, security | **Decline plainly + route to person** | `unsupported*`, `pricing`, `setup`, `human` keywords |
| Buying signal ("ready to move forward") | **Fit check**, not handoff | `__fit_gate__` |
| States evidence ("about 300 leads a month") | **Acknowledge, mark answered, ask next gap** | `extractFit` → `fit.ack` |
| Answers the node's question | **Advance** | node `choices` / `routes` |
| Says nothing useful ("ok", "hmm", ".") | **Patient reply**, no pressure | `isMinimal` → `quiet.*` |
| Asks about the product | **Answer from approved knowledge**, then at most one related question | proposed: `KNOWLEDGE` (4.3) |
| Asks something the knowledge does not cover | **Knowledge-gap recovery**: say so, offer nearby topics, then a person | proposed (5.4) |
| Not understood | **Recover** (Part 5), tier by miss count | proposed: `RECOVERY` table |
| Refuses a question | **Respect, mark answered, move on** | proposed (R6) |
| Off-topic | **State scope, redirect** | proposed (Part 5.3) |
| Corrects themselves mid-reply | **Queue; acknowledge in the next reply** | proposed (Part 6) |

### 3.4 A person joins the conversation (handoff experience)

The product's promise is that the right conversations reach the sales team quickly, with context. The demo must
*show* that, so a person joining live is a designed scene, not a footnote. Backend vocabulary maps directly:
interventions (human request, frustration, commitment or pricing negotiation, contract or legal) put the
conversation on hold and notify a rep; attention signals (strong buying signal, pricing interest) notify a rep
while the assistant keeps helping; context signals (competitor, other decision-makers) notify once.

**Presence states** (deterministic; one state at a time):

| State | Who speaks | Visitor sees |
|---|---|---|
| `agent` | the assistant | normal conversation |
| `waiting` | the assistant (or silent if on hold) | the assistant says someone has been told (R32) |
| `rep` | the person | "{Name} from the Northstar team has joined the conversation", then the person's messages |
| `closed` | nobody | "{Name} has ended the conversation. You can restart whenever you like." |
| back to `agent` | the assistant | "{Name} has handed the conversation back to the assistant." |

**What the person sees and does (the lead workspace).** A notification with the reason in plain words ("asked
for a person", "frustrated", "ready for next steps"), a short context summary built from what was said (volume,
tools, worries, topics asked about, anything they declined to share), the full thread, and three actions: join,
reply, and hand back or close. This mirrors the backend's context and brief data, so the person starts with the
whole picture (R31).

**Drafted copy.**
- Assistant, when a person is notified (replaces the old "simulated" wording): "Of course. I've let someone on the team know you'd like to talk. I can't say exactly when they'll join, so I'll stay here with you until they do."
- Assistant, waiting reply 2: "Still here. Someone on the team has been told and will join when they can. I'm happy to keep going in the meantime, or we can wait."
- Assistant, waiting reply 3: "Nothing has changed on my side. They've been told, and I'll stay until they join."
- Thread events: "{Name} from the Northstar team has joined the conversation." · "{Name} has handed the conversation back to the assistant." · "{Name} has ended the conversation. You can restart whenever you like."
- Person's quick replies (editable before sending):
  - Standard: "Hi, I'm {Name} from the Northstar team. I've read what you shared with the assistant, so you don't need to repeat it. Where would you like to start?"
  - After frustration: "Hi, I'm {Name}. I'm sorry this has been so frustrating. I've read the whole conversation, so let's start with what matters most to you. What would you like sorted out first?"
  - Ready for next steps: "Hi, I'm {Name}. It sounds like you're ready to look at next steps. I've seen what you told the assistant, so I'll skip what you've already answered."
  - Hand back: "I'll step back for now. The assistant is here if you need anything, and you can ask for me again anytime."

---

## 4. Evidence plan (what the widget is trying to learn)

| Evidence (fit tag) | Why we need it (what it changes) | Asked by | Stated-in-free-text patterns |
|---|---|---|---|
| Inquiry volume (`low` / `mid` / `high_volume`) | Below ~150/mo a person beats software; ≥250 is a strong fit | `promising.scale` | `parseVolume` |
| Tools in place (`existing_crm` / `no_systems`) | A CRM is a fit signal; no systems is a poor-fit signal | `promising.process` | `FIT.patterns.crm / noSystems` |
| Triage pain (`triage_pain`) | The problem this product solves | `promising.volume` | `FIT.patterns.triage` |
| Automation goal (`wants_automation`) | Wants the outcome the agent delivers | `promising.outcome` | `FIT.patterns.automation` |

Rules for this plan: ask only when needed (R26), at most 3 fit questions (`fitChecks`), skip any already stated
(R4), accept "not sure" as an answer (R6), and never ask once frustrated or after a human request.
These thresholds are **demo heuristics**, not the product's real scoring.

### 4.1 Quiet evidence in Orient

While the agent explains, it keeps listening. Nothing here is shown to the visitor as tracking, and none of it is
hidden if they ask (R27).

| What we notice | Where it comes from | What it changes |
|---|---|---|
| Facts they state (volume, tools, team, role) | free text via `extractFit` | Fills the evidence without a question (R4) |
| Topics they ask about (pricing, setup, privacy, comparison, integrations) | `GLOBAL_ROUTES` matches | What to explain next; pricing and setup suggest they are nearing a person |
| Wording and mood (worried, burned, rushed, brief) | routes and patterns | Tone and pacing; frustration holds (R16) |
| Engagement (questions they volunteer, whether they return) | turn counts | Whether to offer a next step or just keep helping |
| Blockers and other decision-makers | routes | Offer a short summary they can share |

**When the agent asks (R26).**

| Trigger | What it asks | Shape |
|---|---|---|
| They want a demo, pricing, or to start | Volume and current tools, as one cluster (4.2) | "So the right person can help, two quick things…" |
| They describe a problem | One follow-up about that problem | Bridge from their words, then the question |
| They invite it ("ask me", "what do you need?") | The next unanswered gap | One question, plus why |
| They ask for a person | How to reach them (contact cluster) | Cluster, every part optional |
| Several useful answers, no evidence yet | **Permission first**, not a question | "Would it help if I asked a couple of questions about how you handle this today, so my answers fit you better?" |

**Worked example (Orient, quiet listening):**
- Visitor: "How does this work with the inquiries we get through our website?"
- Agent: answers from knowledge in two short sentences, then: "Is that how it works for your team today, or do inquiries reach you another way?"
- Visitor: "We get a few hundred a month and a rep reads all of them."
- Agent: "Thanks, that helps. A few hundred a month, all read by hand, is exactly where it tends to save time." *(volume and triage pain recorded; those two questions are never asked again)* then the next useful answer or, only if needed, one related question.

### 4.2 Clusters (when related questions can be asked together)

Asking related things together can sound more human than a form of single questions, if it passes four tests: the
items share **one purpose**, they are **natural in one breath**, **each is optional**, and the visitor can answer
**partially**.

| Cluster | Items | Shared purpose | Example phrasing |
|---|---|---|---|
| About you | what should I call you, and your role | So the conversation fits them | "What should I call you, and what do you do there?" |
| Your inquiries | how they reach you, and roughly how many | Understand their situation | "How do inquiries reach you today, and roughly how many a month?" |
| Reaching you | name, work email or phone | So a person can follow up | "So a person can pick this up properly, what should I call you, and what's the best way to reach you, a work email or a phone number? Skip any part you like." |

Do not cluster across topics (for example volume plus a worry), and never ask for more than three items. For a
partial answer, ask only for what is missing, in the next turn.
*Engineering note:* today `captureEmail` handles only a work email. A name and phone need small new parsing in
`engine.js`. Nothing about this changes that nothing is stored in the demo.

### 4.3 Knowledge layer (RAG-ready, deterministic today)

To earn trust the agent needs to answer product questions well, and only from facts the team has approved (R28).
There is no model or retrieval service in this demo, so we design the *contract* now and swap the engine later.

- **Today (demo):** an approved `KNOWLEDGE` table in `scenarios.js`. Each entry: `id`, `topic`, `keywords`,
  `answer` (plain-language, V1), `source`, `verified: true/false`, and no commitments (no price, date,
  guarantee). Matching is deterministic keyword lookup. A match plays the approved answer, then optionally one
  related question (R25).
- **Later (RAG):** retrieval replaces keyword lookup; a model may phrase the answer but only from the retrieved
  passages, and a deterministic validator rejects any reply with a price, date, guarantee or claim not in the
  passages. Each answer records its source id in the decision trace.
- **No match:** the knowledge-gap recovery (5.4). It never guesses.
- **Retrieval never decides** (R29): it cannot trigger a hold, a handoff, or change trust state.

Starting topics. "Unverified" means the answer is "a person can tell you", not a made-up one:

| Topic | Status | What the agent says |
|---|---|---|
| What the product does | approved (from `product.intro`) | Plain description |
| How a conversation works | approved (from `qualify.explain`) | One question at a time, honest about being an AI |
| What it will not do | approved (from `hesitant.boundaries`) | No guarantees, no pressure |
| How a person gets involved | approved | A person joins for pricing, contracts, timing |
| Integrations, pricing, security and data handling, setup timelines | **unverified** | Say so plainly; offer a person |

Owner input needed: which facts are verified and may be stated, and in what words.

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
| **Knowledge gap** | "Does it work with our ticketing tool?" | Say we do not have a reliable answer, offer nearby topics, then a person (5.4) |
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
disclosure, avoids promises, and follows the word list in Part 0 (no lead, fit, capture or demo language).

**Open (welcome, a first message we cannot place)**
- T1: "I may have missed what you're after. I can explain how Northstar's agent works, help you see whether it would suit how your team works, or answer questions about getting started. Which is closest?" *(starters stay visible)*
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
- T1: "Whenever you like. If you'd want someone from the team to follow up, tell me the best way to reach you."
- T2: "You can share one, keep exploring here, or stop. Which would you like?" *(chips)*
- T3: "Sounds good. We can carry on without it." → `curious.close`

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
- T1: "A rough range is fine. It just helps me point you to the right things. Is it closer to dozens, a few hundred, or thousands a month?"
- T2: "Pick the nearest, or \"not sure\" is fine too." *(chips)*
- T3: "Okay, I won't guess a number for you. I'll carry on with what you've told me." → `__fit_next__`, marked answered

**C. Promising, process (`promising.process`)**: missing: what happens to a new inquiry
- T1: "Even one word helps. Who sees a new inquiry first: a person, a tool, or no one in particular?"
- T2: "Which of these is nearest?" *(chips)*
- T3: "That's enough to go on. I'll leave this one." → `__fit_next__`, marked answered

**C. Promising, pain (`promising.volume`)**: missing: the harder problem
- T1: "No need to be exact. If you think about last week's inquiries, what bothered you most?"
- T2: "Pick the closest, even if none is perfect." *(chips)*
- T3: "No problem. I'll go with what you've shared so far." → `__fit_next__`, marked answered

**C. Promising, outcome (`promising.outcome`)**: missing: what "better" looks like
- T1: "Think of your best possible week. What would be different for your reps?"
- T2: "Which of these sounds most like it?" *(chips)*
- T3: "That's enough for me to describe a responsible next step." → `__fit_next__`, marked answered *(unchanged: this one is already good)*

**Orient, answer then ask (`qualify.explain`, `product.intro`, and any answered product question)**
Pattern: *approved answer (short, plain) → a bridge from what they said → one optional, related question.*
- Bridge examples: "Is that how it works for your team today?" · "Does that match what you were picturing?" · "What would you want it to do first?"
- Permission ask (after several useful answers, no evidence yet): "Would it help if I asked a couple of questions about how you handle this today, so my answers fit you better?" *(chips: Sure / Not now)*
- Never ask in the first reply, and never twice in a row (R25, R26).

**Orient, knowledge gap (no approved answer for the question)**
- T1: "I don't have a reliable answer to that, and I'd rather not guess. I can speak to what the agent does, how a conversation works, and what it won't do. Which would help?"
- T2: "Would it help to have someone on the team answer that directly, or shall I try a different question?" *(chips: Connect me with someone / Ask something else)*
- T3: "That one is best answered by a person. I can connect you, or we can leave it for now." → `intervention.explain` as a chip, no forced move

**Decide, offer a person (`buyer.handoff`)**
- T1: "No rush. I can pass this along whenever you say so, or we can keep talking first."
- T2: "Would you like to share a work email, wait a bit, or keep asking questions?" *(chips)*
- T3: "Let's leave it here. The chat stays open whenever you want to pick it up."

**Decide, not the right moment yet (`buyer.mismatch`, `buyer.growth`)**
- T1: "I know that isn't the answer you hoped for. If you expect your volume to change, tell me roughly when and I'll keep that in mind."
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
- T1: "Pick one thing that matters most, such as how it handles honesty, how well it suits your team, or setup effort, and I'll stay with that."
- T2: "Which of these is nearest?" *(chips)*
- T3: "I can't compare other products reliably, so a person is a better source for that." → `intervention.explain`

**Route, human path (`intervention.explain`, `intervention.again`)**: a person was already requested
- T1: "A person is still the right next step. You can share a work email, leave a note without one, or stop here."
- T2: "Which would you like?" *(chips)*
- T3: "I'll pass along what we've talked about, so you won't have to repeat yourself." → `intervention.noted`

**Route, reaching you (`contact.ask`, `contact.personal`)**: one cluster, every part optional (R2, 4.2)
- Ask: "So a person can pick this up properly, what should I call you, and what's the best way to reach you, a work email or a phone number? Skip any part you like."
- T1 (partial answer): "Thanks. And what's the best way to reach you, a work email or a phone number?"
- T2: "Whichever is easiest: just an email, just a phone number, or neither for now. A person can still read our conversation and take it from there."
- T3: "Skipping is fine. We can carry on without it." → `intervention.noted`

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
- Hold 2: "Still holding. Someone on the team has been told and will join when they can, so I'm not answering questions in the meantime. You can leave a note for the team below."
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

### 6.4 Demo mechanics: the lead workspace stand-in

The real lead workspace is not in this repository (the backend only exposes the rep-side data endpoints). For the
demo we build a small **in-page stand-in**: no network, no login, deterministic, local state.

- **Where:** a "Lead workspace" panel beside the widget, opened from the page (a toggle for the presenter).
- **Notification:** when a conversation reaches a trigger (human request, frustration, buying signal), the
  workspace shows a toast and a lead card with the reason, the context summary and the thread.
- **Actions:** `Join conversation`, a reply box with the quick replies from 3.4, `Hand back to assistant`,
  `Close`. Name for the demo person is a placeholder (to confirm).
- **Engine (additive, presentation-neutral):** a `mode` (`agent | waiting | rep | closed`), `repJoin(name)`,
  `repSend(text)`, `repHandBack()`, `repClose()`, a `notifications` event the workspace subscribes to, and message
  roles `rep` and `event`. While `mode` is `rep`, `send` stores the visitor's message and the assistant stays silent.
- **Widget:** renders the new roles distinctly, announces joins and rep messages through the existing polite live
  region (R22), focus unchanged. Restart clears presence and bumps the epoch, as today.
- **Conformance impact:** none expected. The conformance runner only calls `send`, and presence changes only by an
  explicit workspace action, so observed behavior before a person joins is identical. We still run the full suite.
- **Honest limits:** the stand-in simulates the rep's side. The product behavior it shows (notify, context, join,
  hand back) matches the backend's design.

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
| "Whether this would suit your team." | "Whether you're a fit / qualified." | The visitor is a person, not a lead (V2) |
| "If you'd like someone to follow up, tell me how to reach you." | "We won't capture your details." | Do not talk about collecting at all (V3) |
| The visitor's own words ("inquiries", "tickets") | Sales jargon they did not use | Anyone can follow it (V1) |
| Answer first, then ask | A question in the first reply | Value before asking (R25) |
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
- **Presence**: who is currently speaking for the company, the assistant or a person. **Takeover**: a person joins and the assistant goes quiet.
- **Barge-in**: interrupting the agent mid-reply (voice term; here, typing while it replies).
- **Latency / pacing**: how long a reply takes to appear, and whether that feels natural.
- **Response contract**: the approved shape and limits of what the agent may say (roadmap step 4).
- **Deterministic**: the same input always produces the same output.

---

## 10. Open questions for the owner

- [ ] Review the drafted copy in 5.4. Mark lines that sound off. Those edits are the practice.
- [ ] Approve pacing starting values (6.2), or ask for a "slower / faster" variant to compare.
- [ ] Should tier 3 ever *close* the chat itself, or always leave the visitor a choice (current draft: always a choice)?
- [x] Verified facts: owner confirmed that integrations, pricing, security and data handling, and setup timelines stay "a person can tell you" (4.3). Verified facts to add later come from the owner.
- [x] Prototype wording: owner decision is to *show* a person joining (3.4, 6.4) rather than disclaim in the chat.
- [x] Work email is preferred (confirmed). Phone stays an optional alternative (assumed; say if not wanted).
- [ ] Does the real lead workspace have screens or a layout the stand-in should match? Otherwise I design a simple one.
- [ ] Name and style for the demo sales person (placeholder "Maya" or something else)?
- [ ] After a person hands back, should the assistant resume fully, or stay restricted (backend decision D2 says restricted until a rep resolves)?
