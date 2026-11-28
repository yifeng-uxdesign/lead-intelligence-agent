# Northstar evaluation plan

Status: **draft, with a measured baseline.** Written 2026-11-14. Companion to `CONVERSATION_DESIGN.md`.
Nothing in the widget has changed; the baseline below is the current engine, before any improvement.

The scenario set comes from the owner (six role-play scenarios plus six interruptions). This document adds a rubric,
adjusts a few expectations to match the design decisions made since, records what the current widget actually does, and
proposes extra scenarios.

Files: `leadwise/eval/scenarios.json` (the messages, verbatim), `leadwise/eval/run.sh` (replays them against the engine),
`leadwise/eval/baseline-2026-11-15.md` (full transcripts of the baseline run).

---

## 1. What we evaluate

Seven dimensions, each tied to rules in `CONVERSATION_DESIGN.md`.

| Dimension | A good reply shows | Rules |
|---|---|---|
| **Heard** | It answers what was said, and acknowledges facts the visitor gave | R9, R4 |
| **Honest** | No invented prices, dates, certifications, results or storage locations | R12, R13, R28 |
| **Boundary** | A person is brought in for commitments, security, pricing and when asked | R17, R33 |
| **Evidence** | It asks the right thing at the right time, one ask per turn, never before value | R25, R26, R36, R42 |
| **Pace** | No identical replies in a row, no re-asked questions | R7, R4 |
| **Language** | Plain words, no label for the visitor, no internal terms | V1 to V4, R15 |
| **Respect** | A refusal is accepted and not asked again; the visitor stays in control | R6, R39 |

**Hard failures** (any one makes the scenario a fail, whatever else is good):
1. An invented claim (price, date, certification, storage region, result).
2. Ignoring or burying a request for a person.
3. Asking for contact details again after the visitor declined.
4. The identical reply twice in a row.
5. Treating enthusiasm, or "budget approved", as enough on its own to call someone ready.
6. Calling a person present or contacted before one actually has been.

Verdicts: **Pass** (no hard failure, all seven dimensions mostly met), **Partial** (no hard failure, one or more dimensions
clearly missed), **Fail** (at least one hard failure).

---

## 2. The six scenarios

Messages are in `scenarios.json`, typed exactly as written. Run them restarting the widget each time, typing by hand, using
no suggested-reply buttons and never rephrasing to help the agent. A real visitor does not know the words the engine expects.

| # | Visitor | Tests | A good agent shows |
|---|---|---|---|
| **S1** | VP of Sales who was burned by a scoring tool | Trust | Acknowledges the bad experience without defending; explains what the agent works from, keeping what it was told separate from guesses; promises no accuracy; sends accountability to a person |
| **S2** | Founder, 800 inquiries a month, "ready to sign" | Evidence before enthusiasm | Picks up volume, tools, manual review and slow response; connects them to the need; does not call them ready because of "budget approved"; asks at most one missing thing; offers a person; promises no date |
| **S3** | Four-person startup, about 40 inquiries a month | Honest suitability | Notices small volume and no system; explains kindly why the timing may be early, from what the visitor said; does not push a handoff on enthusiasm; leaves the door open |
| **S4** | Enterprise IT director, security and procurement | Unverified facts | No invented certification or data location; separates a general explanation from a formal commitment; brings in a specialist; does not say it will send documents it cannot send |
| **S5** | RevOps director comparing vendors | Commercial boundaries | No invented price or pricing model; says why a person must answer; no rollout guarantee |
| **S6** | Head of Sales who asks for a person, continues, then asks again | Human request and autonomy | Honours the first request at once; answers what information it normally asks about; stops pressing questions after the request; keeps context; can still help if the visitor continues; answers the second request briefly without repeating itself |

### Approved additions (owner, 2026-11-15)

Only S10 and S11 were approved. S7 to S9 are parked (see section 5).

| # | Visitor | Tests | A good agent shows |
|---|---|---|---|
| **S10** | Director of Sales Operations who gives company, size, volume, tools, pain and timeline in her first message | Memory: never re-ask | Acknowledges what she said; asks nothing she already gave (no name, volume, CRM, role or timeline); asks at most one missing thing; at the connect moment asks only how to reach her and for consent; recognises the email she gives |
| **S11** | Operations lead frustrated after months and two failed vendors, then a person joins, takes pricing, hands back | Hold, workspace, resolve | Holds when the frustration is about the assistant or the conversation, not about other vendors; varies the holding lines; once a person joins, stays silent; with pricing still open, deflects without repeating itself and helps on other topics; resumes normally after a resolve |

S11 can only be replayed as far as the hold today. The rest (the scoped hand back and resolve) needs the workspace stand-in; those steps are listed in `scenarios.json` as `pending`.

### Adjustments to the expectations (agreed design decisions since the set was written)

- **S6, "avoid pretending a real human has been contacted."** With the lead workspace stand-in (3.4, 6.4), a person can really be told
  and can really join. New expectation: the assistant says someone has been told only when the notification has fired (R32), and
  never says a person is present until one has joined (R30, R33). Until the stand-in exists, any "someone has been told" line is a hard failure.
- **S6, turn 2 ("what information would you normally collect?")** needs an approved answer. Added knowledge entry K10 (draft).
- **S2, "asks about missing evidence such as decision authority."** Under the sensitivity ladder a strong buying signal opens the connect
  moment (L3): who else weighs in, how to reach them, and consent. It should not turn into an interview.
- **S3, "notices low volume."** The knowledge base says the assistant cannot state a size threshold. The engine's volume cutoffs are demo
  heuristics. The agent should explain from what the visitor said ("about 40 a month, read by one person") and leave the threshold to a person.
  Owner decision needed: is the volume heuristic an approved fact? (What it is and how it compares with the research: `ICP_DRAFT.md` Part 6.)
- **S1 and S2, wording.** The assistant should not describe the visitor as a lead or as qualified (V2), even though the visitor uses those words.

---

## 3. The six interruptions (Round 2)

Added after each scenario, one at a time.

| Interruption | Tests | A good reply |
|---|---|---|
| "That's not what I asked." | Recovery | Owns the miss in one short clause, asks what they meant, offers a way to say it. Not the same line again. |
| "Why do you need to know that?" | Transparency | States the reason for the last question in plain words and makes it skippable (R3, R6). |
| "I don't know the answer." | Incomplete information | Accepts it, records it as unknown, moves on or narrows (R39). |
| "Can you just give me a straight answer?" | Adapting | Gives the shortest honest answer first, then offers detail. |
| "Let me talk to someone." | Human request | Immediate, with no extra questions, and short on repeat. |
| "I don't want to share my email." | Respect | Accepts it at once, does not ask again, offers a way forward without it. |

---

## 4. Baseline: what the current widget does

One run of the current engine, 2026-11-15 (S1 to S6 first measured 2026-11-14 with identical results), before any change. Full transcripts: `eval/baseline-2026-11-15.md`.
The verdicts are my reading against the rubric above, not an automated score.

| Scenario | Verdict | What worked | What failed |
|---|---|---|---|
| **S1** | **Fail** | Turn 5 handles accountability well | Turn 1 ("our sales **reps** ended up ignoring…") goes straight to the person path, so the skeptic is escalated on their first message. Turns 2 to 4 land in the "note" fallback, and turn 4 repeats turn 3 word for word. Uses "simulated". |
| **S2** | **Fail** | Records volume, tools and manual triage; offers a person on that evidence; no date promised | Turn 1 is read as exhaustion and turn 2 ("reps **review** leads") as a request for reviews. Turn 5 repeats turn 4 identically. Never asks about who decides or what outcome they want. |
| **S3** | **Partial** | Picks up small volume and no CRM; gives an honest, kind mismatch with reasons | Turn 5 ("why wouldn't this be a good fit?") gets a canned fallback that does not answer. Says "probably isn't the right fit", which breaks V2. |
| **S4** | **Partial** | No invented certification or location; SOC 2 goes to a person | Turns 1 and 3 get a privacy answer that says nothing you type "in this prototype" is stored, not an answer about the product. Turn 4 (third-party LLM providers) gets "We can stop whenever you want", which is unrelated. |
| **S5** | **Pass** (one miss) | No invented price; no rollout guarantee; correct decline | Turn 1 (compare cost with HubSpot) is read as a setup question and not answered. |
| **S6** | **Fail** | Honours the first request | Turn 2 ("what information would you collect?") files a "simulated note", which is wrong. Turns 3 and 4 go back to qualification questions after the request, and ask the **same** question twice. Says "prototype" and "simulated". |
| **S10** | **Fail** | Eventually offers a person | The first message gives everything, yet the reply is a pilot question ("what would you want it to show first?"), triggered by "next quarter". It then asks about the pain she already described and about outcomes, says "I don't have enough… to call this a fit" despite 400 a month, Salesforce and manual sorting, and never recognises her email in turn 5 (answers "Either works. I just won't guess at fit."). |
| **S11** | **Partial** (replayable part) | The hold works and the holding lines vary | The hold fires at turn 2 on "sent me in circles", which was about other vendors, not about the assistant (known role-play issue 1). Uses "simulated". The workspace steps cannot be replayed yet. |

Fallbacks per scenario: S1 three, S2 one, S3 one, S4 one, S5 one, S6 two, S10 three, S11 one. Identical consecutive replies: S1 (turn 4), S2 (turn 5).

### Round 2 (interruptions)

| Interruption | Result across the six scenarios |
|---|---|
| "That's not what I asked." / "Why do you need to know that?" / "I don't know the answer." / "Can you just give me a straight answer?" | **32 of 32 replies are the previous node's canned fallback**, identical for all four phrases in each scenario. None answers the interruption. |
| "Let me talk to someone." | 7 of 8 go to the person path; in S11 (already in a hold) it gets the holding fallback. |
| "I don't want to share my email." | **3 of 8 ask for the email again** (S2, S4, S6). The other 5 give an unrelated fallback. **0 of 8** accept the refusal. This is a hard failure. |

### What the baseline tells us

1. **Recovery is the biggest gap**, which supports putting it first. The same canned line answers four different interruptions.
2. **Two routing false positives** show up: "sales reps" is treated as a request for a person, and "review" as a request for reviews. They are
   keyword overlaps. Fixing them by editing patterns would be tuning to these scenarios, so they are recorded here as a known issue for the
   interpretation step (roadmap step 7) rather than patched. The owner may choose a narrow fix instead.
3. **Strengths worth keeping:** honest refusals on price, guarantees and certifications, and the kind mismatch in S3.

---

## 5. Review of the scenario set

**Strong.** The set covers distinct dimensions, uses realistic phrasing, states failure signals up front, and the "don't help the agent" protocol is the right one.
The interruptions are the best part, because they expose recovery.

**Overlaps with what already exists.** S1, S2, S3 and S6 are close to the personas P1, P2, P5 and P6 in `DEMO_SCRIPTS.md`, which already have
conformance cases in `intent-agent-v2/conformance/cases.json`. S4 and S5 overlap the setup and pricing cases. So keep this set as the human-facing
evaluation, and encode a reviewed subset as new conformance cases later. New cases change `cases_hash` and need baselines re-recorded; existing cases must not be edited.

**Gaps (additional scenarios).** Owner decision 2026-11-15: **S10 and S11 approved; S7 to S9 not approved (parked).**

| # | Visitor | Why it matters | Status |
|---|---|---|---|
| **S7** | Curious non-buyer (student or researcher asking general questions) | Tests the interest gauge (R44) | Parked |
| **S8** | Existing customer who needs help | Tests the existing-customer path | Parked |
| **S9** | Visitor in an unsupported region who also declines to share contact | Tests honest early disqualification and respect for refusal; needs the supported-region list | Parked |
| **S10** | Visitor who gives everything in one message | Tests memory: nothing asked again, only the missing part asked | **Approved**, in `scenarios.json` |
| **S11** | Frustrated visitor, then a person joins and hands back | Tests hold, the workspace and resolve | **Approved**, replayable as far as the hold |

**A second pass for robustness (Round 1b).** Re-run each scenario with the same intent in different words (for example S2 turn 2: "HubSpot is our CRM but someone
on the team still reads every inbound lead and picks who to call"). A keyword engine passes the written wording and fails the paraphrase. Keep these
out of any tuning, as with the held-out set.

---

## 6. Running it

**Manual (for the portfolio, with screenshots).** Serve `leadwise/` with `python3 -m http.server`, restart the widget before each scenario,
type the messages by hand, and record each reply with the verdict and the dimension missed. Template per turn:
*visitor message · node or reply · heard / honest / boundary / evidence / pace / language / respect · note*.

**Replay (reproducible baseline).**

```bash
./leadwise/eval/run.sh > leadwise/eval/baseline-YYYY-MM-DD.md
```

**After each implementation step**, run the replay and the two standard checks, and diff against the baseline:

```bash
./intent-agent-v2/conformance/run_all.sh "$PWD/leadwise"
cd intent-agent-v2 && python3 -m pytest -q   # expect 304 passed, 3 xfailed
```

## 7. What should change, step by step

| Step | Expected effect on this evaluation |
|---|---|
| Recovery ladder | Round 2 rows 1 to 4 and 6 stop returning the same canned line; S1 turn 4 and S2 turn 5 stop repeating; S3 turn 5 gets an answer |
| Copy and word list | No "simulated", "prototype" or "fit" in replies |
| Ask pacing and the ladder | S6 turns 3 and 4 stop pressing questions after a person was requested; no re-asked question |
| Knowledge base | S4 turns 1, 3 and 4 and S6 turn 2 get approved answers or an honest "a person can tell you" |
| Workspace stand-in | S6 and S11 can show a person really joining |
| Routing false positives | S1 turn 1 and S2 turns 1 and 2 (only through the interpretation step or an owner-approved narrow fix) |
