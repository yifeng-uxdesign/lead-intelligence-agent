# Demo fit: Genesys, Staff User Experience Designer, Conversational AI

Source: the job text you pasted (2026-11-22). Labels: **from the JD** (quoted or closely paraphrased), **from the project** (cited file), **proposed**, **inferred**. Rating of how well the project already shows each requirement: **Strong**, **Partial**, **Gap**. I do not know your resume, so nothing here claims years of experience or past influence; those need your own evidence.

## 1. What this role is, in one paragraph (from the JD)
A Staff UX designer who owns *experience direction* for conversational AI: how AI "understands, communicates, reasons, acts, recovers, and collaborates", connected to customer journeys, **human handoffs**, context, tools and policies; who turns research and **real interaction data** into **reusable principles and frameworks**; who aligns design, product, engineering and data science without formal authority; across voice and digital, moving from structured dialogue to generative and agentic systems.

**Inferred framing that makes your project relevant:** Genesys sells contact-center orchestration. Your agent's hard problem (when does AI hand to a person, with what context, under whose control) is the same problem as AI-to-agent escalation in a contact center. Present the lead-qualification agent as **one domain instance of a handoff and trust framework**, not as a sales tool.

## 2. Requirement-by-requirement
| JD requirement | What in the project shows it | Rating | What to add or say |
|---|---|---|---|
| Shape end-to-end direction for AI interactions across structured dialogue, generative and agentic | Layer map and LLM boundary: rules own decisions, LLM only interprets or phrases (`drafts/LAYER_MAP.md`, `CLAUDE.md:5-8`); configs A/B/C; **board 2 three-handoff diagram** | **Strong** | Lead with this. It is a direction, not a feature |
| Human handoffs, context, policies | Three handoff types (alert, relay, qualified), holding copy, context carried, delivery matrix (`delivery_policy.py`), invariants from `soul.md` | **Strong** | Show it in the workspace beside the chat (the rep's view is the other half of the handoff) |
| Reusable principles and frameworks across products | `soul.md` values, response-contract idea, invariants (`INVARIANTS.md`), 50 conversation rules (`northstar/CONVERSATION_DESIGN.md`), failure taxonomy | **Partial** | Distil a **one-page "Conversational AI principles"** from those, each tied to an eval check. Today the rules are scattered |
| Recovery, trust, context | Repair and recovery work in the Northstar widget; trust-state machine; honest "a person can tell you"; loop-breaker analysis (EV-A4) | **Strong** | Show a failure and its fix: the canned loop-breaker found by the eval, then removed |
| Turn-taking, interruption, pacing, latency, end-of-speech, tone (voice list) | Northstar: turn queue, interruption handling, bubble pacing (F1, F7); rubric dimension "Pace" (`northstar/EVALUATION_PLAN.md`) | **Partial** (text only) | One slide: "how each rule transfers to voice" (barge-in, latency budget, backchannel, spoken holding copy). Say plainly that voice is not built |
| ASR, NLU, TTS, LLM, streaming: translate capabilities and constraints into experience | Extraction-miss analysis: rule-based NLU misses "let me talk to someone" (0 of 6), and what that does to users; plan for LLM extraction against a baseline | **Partial** | Add an explicit "what the NLU limitation means for the customer" note per failure; no ASR/TTS content exists |
| Research and discovery that shapes product priorities | Your manual test rounds produced F1–F9; I classified them; the eval ranked the backlog by evidence | **Partial** | Be candid: findings so far come from you and synthetic scenarios. See section 4 for a small real-data step |
| Quantitative and qualitative evidence; conversation analysis; experimentation | `REPORT_A.md`, classification (missing feature / extraction miss / bad expectation), `ITERATIONS.md`, held-out set | **Strong** on method, **Partial** on data | Method is the exhibit. Label the data as scenario-based |
| Influence senior stakeholders and align teams without authority | Decision log, Open Questions lists written for PM/engineering/legal decisions (`AUDIT.md`, `PLAN_BEHAVIOR_LAYER.md`), a plan ranked by evidence | **Partial** (artifacts, not outcomes) | Show the artifacts as how you drive alignment. Do not claim influence the project cannot show |
| Storytelling, facilitation, systems thinking, prototyping | Architecture canvas (boards 1–5), working prototype of agent + workspace | **Strong** if the demo runs | Keep the narrative to one thesis (below) |
| Portfolio with UX leadership and complex problem solving | One whole project: agent behavior, rep workspace, evals | **Strong** | Case-study page, not a feature tour |
| Preferred: AI/agentic products, voice+digital, interaction data, frameworks adopted by teams | AI/agentic yes; voice+digital no; interaction data yes (synthetic); adopted frameworks no | **Partial / Gap** | Name the gaps honestly in the case study ("next: voice, real transcripts") |
| 8+ years, Staff-level scope | Not shown by the project | **Gap (yours to evidence)** | Put career evidence in the resume and the case-study intro, not the demo |

## 3. The thesis the demo should carry (proposed)
> "AI decisions about *when to hand a person in, with what context, and what to say when it does not know* should be explicit, testable rules; the language model's job is to understand and to phrase, never to decide. I designed that layer, built evals for it, and used the failures to decide what to build next."

Everything in the demo supports that sentence: the handoff model, the rep workspace, the knowledge-first honesty, the eval iterations.

## 4. Changes to the demo plan (`PLAN_DEMO_V2.md`) for this role
1. **Reframe scenario names around conversational concerns**, not sales: #1 *Escalation on request (human handoff, disclosure)*, #2 *Honest boundary (knowledge limits, policy)*, #3 *Uncertain decision (relay: AI asks a human to decide)*, #4 *Gradual discovery to warm transfer (context carried)*, #5 *Frustration, takeover and hand-back (recovery)*.
2. **Add a "principles" beat (2 minutes):** the one-page principles, each pointing to the eval check that enforces it.
3. **Add a "voice transfer" slide (1 minute):** how handoff, holding copy, interruption and pacing rules change in voice. Design thinking only; do not imply it is built.
4. **Add a small real-data step (proposed, optional):** run the five scenarios as role-play with 3–5 people who did not write them; keep their exact messages; classify them with the same failure classes; show how real wording differs from your scripts. This answers "real interaction data" and the same-author caveat on the held-out set. It needs participants and consent; I can prepare the script and a logging template.
5. **Keep the rep workspace visible throughout**, because "human handoffs" and "collaboration with customers" in the JD are about both sides of the exchange.
6. **Evals as research practice, not QA:** show the failure classification and one decision that changed because of it (for example, moving accountability questions from "handoff" to "answer from the knowledge base, alert on a miss").

## 5. Revised run of show (about 12 minutes)
1. 1 min: thesis and the three-handoff framework (board 2).
2. 6 min: scenarios #1, #2, #3, #4, chat and workspace side by side (90 seconds each). #5 as an optional extra.
3. 2 min: principles, each linked to an eval check.
4. 2 min: eval iterations (what changed, what moved, one thing the evals caught).
5. 1 min: voice transfer and next steps (real transcripts, LLM behind a validator).

## 6. Honest gaps to state, not hide
- Voice is not built; only transferred in design.
- Findings come from scenarios you authored and your own testing; no external participants yet.
- The agent is rule-based by design; LLM comparison is planned, not done.
- A solo project shows reasoning and artifacts, not cross-team outcomes.

## 7. Questions
- **G1.** Do you want the optional real-data step (3–5 role-play sessions)? It strengthens the research story most.
- **G2.** Are you comfortable calling the project a "handoff and trust framework applied to lead qualification", or do you want to keep it sales-first?
- **G3.** Do you have the principles list you would put your name on? I can draft one page from `soul.md`, `CONVERSATION_DESIGN.md` and the invariants for you to edit.
- **G4.** Remaining from `PLAN_DEMO_V2.md`: J2 (the multi-turn discovery wording), J3 (which workspace, and may I wire it to the backend), J5, J6.
