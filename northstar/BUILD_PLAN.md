# Northstar widget: readiness review and build plan

Written 2026-11-16, after the first build step. Companion to `CONVERSATION_DESIGN.md` (what and why), `EVALUATION_PLAN.md` (how we measure) and `ICP_DRAFT.md`.

## 1. Verdict: go, in slices

**It is the right time to start building, but not to build everything.** The design is complete enough for the parts that decide how the agent recovers, takes turns and paces itself. Those were built and measured in this pass. The rest depends on things that are
not ready (the lead workspace, approved knowledge, a decision about wording versus the conformance suite), so building them now would mean guessing. Each deferred slice below says exactly what it is waiting for.

The one design document you gave me to review, `CONVERSATION_DESIGN.md`, is about 1,000 lines. That is too large to build from directly, which is the first thing the review found missing: **a build sequence with acceptance tests.** This file is it.

## 2. Components you may have missed

The design covers conversation behavior well. These are the gaps the review found, in order of how much they matter for building.

| # | Gap | Why it matters | Status |
|---|---|---|---|
| 1 | **A build sequence with acceptance tests** | The design was too big to build from in one go | This file |
| 2 | **Conversation repair** ("that's not what I asked", "why do you need that", "I don't know", "I'd rather not say") | The ladder alone did not fix your Round 2 interruptions; the measurement showed it. A visitor talking *about* the conversation needs its own recognition | **Found and built this pass** |
| 3 | **Sequencing of honest handoff wording** | A reply must not say a person "has been told" until the workspace can really tell one (hard failure 6). So the handoff copy must change *with* the workspace stand-in, not before | Recorded; the new copy avoids the claim |
| 4 | **Word list versus the conformance suite** | The word-list rewrite removes "evidence" and "fit", but three conformance cases require those words in replies, and three must-not rules forbid "let me connect you". The suite must never be weakened, so the owner has to decide how to change those cases deliberately | **Needs your decision** |
| 5 | **Routing false positives** | "our sales reps…" is read as a request for a person; "review leads" as a request for reviews; "sent me in circles" about other vendors triggers the hold. The evaluation shows these cause S1 and S2 to fail, and the ladder cannot fix them | Deferred; needs your approval (see slice 4) |
| 6 | **A visual spec for the new states** | Queued messages are done. A person's messages, join and leave lines, the check-in, the failure line and the holding line have no visual design yet | Deferred with the workspace |
| 7 | **A per-turn trace in the widget** | The rep workspace needs "why was a person notified" and "what was said, with its source"; the evaluation needs it too. The backend has a decision trace; the widget has none | Deferred (slice 3) |
| 8 | **Accessibility test plan** | R22 states the rules, but nothing checks them. The browser check this pass covers focus, input and queue behavior only | Partly done; checklist in section 6 |
| 9 | **Consent and privacy wording for EMEA** | Needed before any real visitor, not for the demo. Depends on the data-handling position | Not needed for the demo |
| 10 | **Stale duplicate in `web/`** | `web/` holds an older copy of the widget files. It is not what runs or what the conformance suite tests, so it can mislead | Not touched; recommend removing |

## 3. Readiness by component

| Component | Design | Blocked by | Verdict |
|---|---|---|---|
| Recovery ladder | Complete, copy drafted | Nothing | **Built** |
| Repair intents | Added this pass | Nothing | **Built** |
| Turn-taking (queue) | Complete | Nothing | **Built** |
| Length-aware pacing | Complete, values are guesses | Tuning by you | **Built** (config) |
| Ask engine: field registry, ladder levels L0 to L4, interest gauge, memory, clusters, consent | Complete on paper | Needs a follow-up design pass (see slice 3) and a decision about the data model branch | Not yet |
| Knowledge layer | Complete | **Your approval of K01 to K12**, languages, restricted countries | Not yet |
| Presence, hand back, workspace stand-in | Provisional | **The workspace code and screenshots**, RELAY and SHADOW decision, D5 | Not yet |
| Copy pass (word list) | Audit done | Gap 3 (sequence with workspace) and gap 4 (conformance cases) | Not yet |
| Routing correctness | Not designed | **Your approval** | Not yet |

## 4. Slices

| Slice | Content | Status |
|---|---|---|
| **0. Safety net** | `northstar/test/` (21 unit tests, no dependencies), the replay set in `northstar/eval/`, a browser check | **Done** |
| **1. Recovery and repair** | Three-tier ladder for 23 node groups, no verbatim repeats, tier 3 can offer its own suggested replies; five repair intents; varied holding lines | **Done** |
| **2. Turn-taking and pacing** | Input stays enabled; up to two messages wait in order; nothing dropped; restart clears them; typing delay grows with reply length | **Done** |
| **3. Ask engine v1** | Field registry replacing the fixed four questions; ladder levels; interest gauge; memory with provenance (never re-ask what was said); clusters and consent; a per-turn trace. Fixes S10 and the post-request questions in S6 | Next. Needs a short design pass first, because the data model and the registry need to agree on field ids |
| **4. Routing correctness** | Target-aware frustration, the "sales rep" keyword, the "review" pattern. Measured on the existing conformance cases (A1 to A4, C8, H4 fail today) | Needs your approval, because pattern changes are the easiest way to overfit |
| **5. Knowledge layer and copy pass** | Approved facts, knowledge-gap recovery, the word-list rewrite of all existing copy | Needs approvals and gap 4 |
| **6. Presence and the lead workspace stand-in** | Person joins, hand back, resolve, the visitor-side states | Needs the workspace session; the copy changes here, together |

## 5. What was built in this pass

- `scenarios.js`: `RECOVERY` (23 groups, alternates, node mapping) and `REPAIR` (five intents, reasons for each question). Each grouped node's own `fallback` is kept equal to tier 1 so the conformance observer keeps counting the first reply to an unmatched input as a fallback.
- `engine.js`: the ladder (`pickRecovery`), repair recognition, the turn queue, length-aware pacing (`paceMs`), staging of replies so the typing time can depend on their length.
- `widget.js`, `styles.css`, `config.js`: the input is never disabled; queued messages show as "waiting"; the Send button is disabled only when two are waiting; pacing values moved to `config.pacing` (500 to 2,200 ms).
- `test/`: 21 tests, including that no recovery text contains an internal word or claims a person has been told.

**Not changed:** the existing node copy (still has "simulated", "prototype", "fit"), routing patterns, the fit questions, the welcome flow. Behavior a visitor sees before any miss or interruption is unchanged.

## 6. Measured results

| Check | Before | After |
|---|---|---|
| Conformance, widget, overall pass rate | 0.575 | **0.600** |
| Conformance, widget, repeat rate | 0.083 | **0.056** |
| Conformance, widget, route accuracy, false escalation, missed intervention | 0.745, 0.137, 0.111 | unchanged |
| Conformance, widget, fallback rate | 0.188 | 0.116 (**a measurement artifact, not an improvement**: the observer only counts a reply as a fallback if it matches the node's own fallback text, so the later rungs of the ladder are no longer counted) |
| L1 (same reply five times in a row) | failing | **passing** |
| `pytest` | 304 passed, 3 xfailed | 304 passed, 3 xfailed |
| Unit tests (`northstar/test/run.sh`) | none | 21 passed |
| Interruptions answered specifically (outside the frustrated hold) | 0 of 42 for four of the six; email asked again 3 of 8 | **42 of 42**; the email is never asked again |
| Browser check (Chromium) | n/a | input enabled and focused mid-reply, 2 waiting bubbles, Send disabled when full, third message kept in the input, clean restart, no console errors, reduced motion about 200 ms |

I did **not** re-record the conformance baselines, because the recorded fallback rate would then contain the artifact. Say if you want them recorded.

## 7. Known issues that remain (so none surprises you in testing)

1. **S1 turn 1** is still escalated by "our sales reps…". The ladder then makes the false escalation more visible: real questions get "Which would you like?" and then "I'll leave a note" with "Simulated note filed". Root cause: slice 4.
2. **S2 turns 1 and 2** are still misrouted (exhaustion, reviews), and its turn 5 still repeats turn 4 verbatim (the same node replays; the repeat guard applies only to recovery, not to normal replies).
3. **S6** still asks qualification questions after the visitor asked for a person, and **S10** still ignores facts given in the first message. Both are slice 3.
4. **S11** still holds one turn early on "sent me in circles".
5. Existing copy still says "simulated", "prototype" and "fit" (slice 5 and 6).
6. "What else do you need from me?" is not recognised as its own kind of question; it falls into the ladder.
7. The pacing numbers are guesses. Tune `config.pacing` after trying it.
8. Tier 3 recovery always leaves the visitor a choice and never closes the chat.

## 8. How to test it (about 15 minutes)

Serve the folder, then open it:

```bash
cd northstar && python3 -m http.server 8000
```

Open `http://localhost:8000`, click **Chat with Northstar**, and type by hand (no suggested replies).

| Try | Expect |
|---|---|
| Click "I'm exploring…", then type nonsense three times (for example `zzz`, `qqq`, `xxx`) | Three different replies; the third moves on to the next question |
| Type `ok`, `hmm`, `maybe`, `not sure`, `sure`, `go on` | No reply repeats in a row |
| While a reply is on its way, type two more messages quickly | Both show greyed as "waiting", then are answered in order; a third is held in the box |
| Press Restart mid-reply | Everything clears; nothing arrives afterward |
| Ask `Why do you need to know that?` at a question | The reason for that question, then a different line if you ask again |
| Type `I don't know`, then `I'd rather not say` at a question | Accepted warmly; it moves on and does not ask again |
| Type `That's not what I asked` four times | Different replies; the fourth offers a person |
| Type `This is frustrating, I'm fed up`, then keep typing | The hold; each line is different |
| Type `Let me talk to someone` | The person path, as before |
| Turn on "reduce motion" in your system settings | Replies arrive in about a fifth of a second |

Automatic checks:

```bash
./northstar/test/run.sh
./northstar/eval/run.sh > northstar/eval/after.md
./intent-agent-v2/conformance/run_all.sh "$PWD/northstar"
```

## 9. Decisions I need from you

1. **Slice 4:** may I fix the routing false positives (the "sales rep" keyword, "review", and target-aware frustration), measured only on the existing conformance cases?
2. **Gap 4:** how should the word-list rewrite deal with the three conformance cases that expect "evidence" or "fit" in a reply? Changing cases changes the baseline hash and must be recorded deliberately.
3. **Slice 3:** may I start the short design pass for the ask engine, and merge the data model branch first so the field ids match?
4. **Approvals** that unblock slice 5: knowledge entries K01 to K12, supported languages, restricted countries.
5. **The workspace session:** when you share the code and screenshots, slice 6 can be planned properly.
6. **Pacing and baselines:** try the pacing, and say whether to record the conformance baselines.
