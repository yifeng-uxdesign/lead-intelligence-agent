# Failure taxonomy (DRAFT)

**Rule followed:** categories come **only** from your failure list so far (`northstar/FAILURE_LIST.md` Part 1, F1–F9, **[failures]**). I did not add categories from R1–R11 (found by me) or from my own guesses. The list is incomplete; the empty slots below are for you. Label: **[failures]** = from your list; **[proposed]** = my placement of it (layer, turn type) only.

Caveat: F1–F9 were observed on the Northstar widget (scripted demo, not the primary target). They are used here as input patterns; whether each also applies to the backend is **not asserted** (Q3).

| ID | Category | Definition (from your report) | Source | Likely layer [proposed] | Single / multi-turn [proposed] |
|---|---|---|---|---|---|
| FT-01 | Pacing: replies arrive all at once | A multi-bubble reply is delivered at once rather than one by one at a gentle pace | F1 | Presentation / delivery (outside layers 1–6) | single |
| FT-02 | Narration of the agent's own behaviour | Highlighted or explanatory lines about what the agent is doing that the customer cannot understand or has no reason to see | F2 | 6 Generation | single |
| FT-03 | Suggestion structure | Suggested replies undifferentiated: questions vs actions not distinguished ("Ask me things like" + actions) | F3 | 6 Generation / UI contract | single |
| FT-04 | Prototype/demo disclaimer in customer copy | Copy tells the customer it is a prototype/simulated instead of behaving as a real handoff | F6 | 6 Generation (copy) | single |
| FT-05 | Interruption ignored | Customer asks a new question mid-flow and the agent keeps pursuing its own previous question | F7 | 6 Generation + flow control (not a layer in LAYER_MAP; Q) | multi |
| FT-06 | Out-of-script question gets irrelevant answer or restart push | Question outside predefined scripts → irrelevant reply, "restart" prompt, no honest "I don't know" | F8 | 1 Extraction / 6 Generation | single and multi |
| FT-07 | Keyword false positive → false escalation | Ordinary phrase read as a request ("our sales reps…" read as a request for a person; "review" read as a request for reviews) | F9 | 1 Extraction | single (first turn) |

**Not taxonomy entries (delivery/process, not behavior):** F4 (stale local copy), F5 (PR/date confusion). Kept out; stated as "Explained" in your list.

## Room for new categories
| ID | Category | Definition | Source | Layer | Turn type |
|---|---|---|---|---|---|
| FT-08 | _(yours)_ | | | | |
| FT-09 | _(yours)_ | | | | |

## Mapping to metrics and invariants [proposed]
FT-07 → R3 false_escalation_rate, Q4 signal_extraction_accuracy. FT-06 → R7 fallback_rate, INV-07. FT-02/04 → INV-03, rubric "Language". FT-05 → multi-turn case type; needs trace field `turn.pending_question` (TRACE_SCHEMA). FT-01 → not measurable from the backend trace; needs a widget timing log.

## Open points
- Backend-side failures are largely absent from your list. The backend's own known gaps are in `v2/conformance/known_gaps.json` (POL-20 restricted after human request, POL-21 approval gate offline not unrestricted, POL-26 hold follow-ups not verbatim repeat) **[code]**; I have not promoted them to categories because they are not on your list (Q2).
- The Northstar rubric's six "hard failures" **[docs]** (`EVALUATION_PLAN.md`) could seed categories; not used pending your call (Q3).
