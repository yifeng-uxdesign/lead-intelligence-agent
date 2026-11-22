# Plan: handoff model, knowledge-first answering, and the missing-feature backlog

Written 2026-11-22 after the first config A eval (`REPORT_A.md`). Goal of this plan: make the behavior layer's structure and rules clear and gap-free before any LLM is added.
Labels: **from your message** (your 2026-11-22 decisions), **from code** (cited), **from the eval** (`REPORT_A.md`, `MAPPING.md`), **proposed** (mine, for you to accept or change). Nothing here changes source or the YAML; it is a plan.

---

## 1. Handoff: the model you described, made concrete

### 1.1 Your intent (from your message)
- The agent's job is to turn an inquiry into a **qualified lead** and hand it to an AE to close. That is the ultimate goal, even if the success rate is low (for example because of security and compliance).
- Handoff has two modes: **ALERT** (a human is needed: usually a human request) and **RELAY** (the agent thinks the signals it collected are not enough to decide whether the lead is qualified, so it seeks help from a human rep).
- Many of the signals that define "qualified" are not defined or collected yet.

### 1.2 Proposed model: three kinds of handoff, one field
**Proposed:** add one trace field `handoff_type` with three values, so "handoff" stops being a boolean.

| `handoff_type` | When (proposed) | Mode | Customer sees | Rep gets | Who decides |
|---|---|---|---|---|---|
| `qualified` | All required qualification signals present and meet the criteria; no disqualifier | AUTONOMOUS → handoff to AE | Warm bridge ("connecting you with …"), context carried | Qualified-lead brief: signals, evidence, summary | Rules (deterministic) |
| `alert` | An intervention-class need: human request, frustration at the agent, commitment demand, pricing negotiation, contract/legal ask, **or a knowledge miss on a high-stakes topic (section 2)** | ALERT | Approved holding copy only | Alert with trigger and SLA | Rules |
| `relay` | The agent cannot tell whether the lead is qualified: required signals missing after the agent has asked, or signals conflict | RELAY | Agent keeps conversing under rep oversight (draft-approve), or says a person will review (**your choice, Q-H2**) | A "decide this lead" request: what is known, what is missing | Rules raise it; a human decides |
| none | Everything else, including notice-only triggers (competitor, stakeholder, pricing interest) | AUTONOMOUS | Normal reply | Notice (once per lead) | Rules |

A `disqualified` outcome is **not** a handoff (no person is involved); it is a terminal outcome (see `QUALIFICATION_CRITERIA.md`).

### 1.3 Where this differs from the code today
- **RELAY today is an approval gate, not "uncertain qualification".** From code: RELAY is set only when `awaiting_approval` is true and no handoff is open (`src/collaboration/mode_state_machine.py:89-92`); in RELAY the agent's draft goes to the rep and the customer receives nothing (`delivery_policy.py`, roadmap in `CLAUDE.md`). Nothing in the code makes the agent choose RELAY because it is unsure about a lead.
- **Your RELAY needs a new input:** a deterministic "qualification uncertain" condition (requires the qualification state, M2 below). **Proposed:** keep the existing mechanics (rep reviews before the customer sees anything) and add the new reason as a second way into RELAY. Confirm that is what you mean (Q-H1).
- **ALERT for a human request already matches** your model (`mode_state_machine.py:83-87`). The YAML's `mode: RELAY` for a human request (GD-S6 turns 1 and 6) therefore contradicts your model; **proposed:** change those two expectations to ALERT in a v1 YAML (not edited here).
- **A qualified handoff to an AE has no code at all** (no qualification state, no brief for it): the success path of your ultimate goal is the biggest gap (M2, M8).

### 1.4 What `handoff: true` should mean in the eval
**Proposed:** replace the boolean by `handoff_type` and let each case state which type it expects. "Notified versus takes over" then maps cleanly: `alert` and `relay` involve a person acting; notice-only triggers are `none` with a rep notice, not handoffs. This removes the ambiguity measured in REPORT_A section 1d.

---

## 2. Knowledge first, alert when it can't answer

### 2.1 Your rule (from your message)
For accountability, security and compliance, and pricing interest: build a knowledge base; the agent retrieves first; if it cannot deal with the question, it sends an alert to human reps.

### 2.2 Proposed flow (deterministic in config A)
1. **Topic router** classifies the message into a known topic (accountability, security/compliance, pricing interest, implementation timeline, what-we-collect, product basics …). In config A this is keyword/phrase rules; in config C an LLM may propose the topic label from the frozen set, rules still decide.
2. **Retrieve** the topic's KB entry. Entries have a status: `approved` (may be stated), `draft`, `unverified` (the agent must not state it).
3. **Answer** only from an `approved` entry, using approved wording (template with the entry text). The answer passes the invariants (no certification, price, date or residency claim unless the entry is `approved` and says so).
4. **Miss** (no entry, only `draft`/`unverified`, or the topic is outside scope) → **alert**: honest message that a person will answer, plus a rep alert. **Decision needed (Q-K1):** does a miss *hold* the conversation (intervention class, ALERT) or notify and let the agent continue (attention class)? **Proposed:** hold only for commitment-type topics (certifications, data processing, contracts); notify-and-continue for the rest (accountability, pricing interest), so one unknown does not silence the agent.
5. **Pricing negotiation, contract/legal, commitment demands** stay as today: always intervention (`trigger_catalog.py:46-53`); the KB is not consulted for them.

### 2.3 What exists and what does not
- **From docs:** `northstar/KNOWLEDGE_BASE.md` has 15 draft entries (K01–K15) and a "known unknowns" table (pricing, integrations, security/compliance, setup effort, results, comparisons, minimum volume, languages, contracts/SLAs). **All are `draft`; none is approved.** The known-unknowns table already says: security, compliance and pricing → "a person can tell you".
- **From code:** no KB module, no retrieval, no topic router in `intent-agent-v2/src`. Replies are static templates; `NOTICE_TOPIC_PHRASES` (`orchestrator.py:239-244`) is a stopgap, not a KB.
- **Consequence (inferred):** with today's approved content, security, compliance and pricing questions would **always miss** and alert. That is correct and safe, and it makes the "alert fallback" the main path for those topics until you approve real answers. Accountability is the topic where a real answer can exist soonest (`soul.md` values 5 and 7).

### 2.4 Effect on the eval cases (proposal for a v1 YAML; v0 is not edited)
Expectations become conditional on a **golden KB fixture** (a small `kb_fixture_v0` the eval loads, so tests are deterministic and independent of content you later approve).

| Case / turn | v0 expectation | Proposed v1 expectation |
|---|---|---|
| GD-S1 t5 accountability | handoff, `accountability_moment` | If KB has an approved accountability entry: answered, `handoff_type: none`. If not: notice + honest "a person will follow up". Add a case for each |
| GD-S4 t1–t5 security/compliance | handoff every turn | KB miss → per Q-K1; assert the **reply contains no claim** and an alert/notice was raised; no loop-breaker |
| GD-S5 t2 "How much does it cost?" | handoff, `pricing` | KB: pricing = unverified → honest "a person can tell you" + notice (attention); **not** `alert` unless negotiation words appear |
| GD-S5 t3 pricing model, t4 timeline, t5 rollout guarantee | handoff | t3/t4 KB miss → notice; t5 "guarantee … two weeks" is commitment → `alert` |
| GD-S6 t1, t6 human request | `mode: RELAY` | `mode: ALERT`, `handoff_type: alert` |
| GD-S2 t5 "ready to sign today" | handoff, qualification not_qualified | Decision (Q-H3): `relay` if qualification signals are missing, `qualified` if they are present, never `alert` unless commitment words appear |
| GD-S3 (small startup) | `disqualified` | Needs the poor-fit rule (M5); until then mark expected-fail |

---

## 3. Every missing feature, in one list

IDs are new (M1…). "Eval evidence" is from `REPORT_A.md`. Size is a **proposed** rough estimate: S ≈ a day or less, M ≈ a few days, L ≈ a week or more.

| ID | Missing feature | Layer | Why it matters (from the eval / your goal) | Depends on | Size |
|---|---|---|---|---|---|
| M1 | **Handoff taxonomy**: `handoff_type` (qualified / alert / relay / none) in trace and result | Handoff | Removes the main ambiguity in the eval (REPORT_A 1d); required by your model | Your decision on section 1 | S |
| M2 | **Qualification evaluator + signal fields**: required signals (budget, timeline, authority, volume/load, stack/CRM, region, pain, decision process, security/compliance need), criteria from `QUALIFICATION_CRITERIA.md`, outputs `qualified` / `disqualified` / `uncertain` | Extraction, state, gates | Your ultimate goal; 34 of 44 scenario signals have no field; all 32 state-layer failures; invariants INV-NO-QUALIFIED-ON-ENTHUSIASM and INV-NO-HANDOFF-ON-INTENT-ALONE not evaluable | Q4 criteria signed off | L |
| M3 | **Conversation memory**: persist signals given and questions asked | State | `context_preserved` fails everywhere; stops re-asking (your R1/R2); prerequisite for M2 | none | M |
| M4 | **Knowledge base + topic router + retrieve-first rule** (section 2) | Reply, gates | Accountability, security, pricing cases (GD-S1 t5, S4, S5 t2–t4); canned loop-breakers on those turns | Approved KB entries (your work); Q-K1 | M |
| M5 | **Poor-fit / disqualification rule** (volume, process maturity, region) and terminal `disqualified` | Gates | GD-S3 cannot pass; hard disqualifiers in your docs are not wired (`orchestrator.py:105-116`) | M2 | M |
| M6 | **Relay trigger**: "qualification uncertain" → RELAY (reason code, rep request) | Mode, handoff | Your RELAY meaning does not exist today (section 1.3) | M2, M1 | M |
| M7 | **Terminal outcome record**: `qualified_handoff` / `disqualified` / `handoff` / `informational_only`, turns-to-outcome, fallback count | Trace | Your session-success definition cannot be computed today | M1, M2 | S |
| M8 | **Contact capture and "unknown" signal state**: company-domain email, decline handling, `unknown` ≠ guessed | Extraction, state | PERT-3 and PERT-6 (not evaluable); success event requires a company-domain contact | M3 | M |
| M9 | **Question policy** (what to ask next, one at a time, never repeat) | Reply | `next_question_targets_any_of` fails; GD-S2 t4; loop-breaker chains | M2, M3 | M |
| M10 | **Verified-claims allowlist** (the approved KB entries double as the allowlist) | Invariants | INV-NO-FABRICATED-CLAIMS is checked only by a template-bank proxy | M4 | S |
| M11 | **Human-request withdrawal / resolve path** for open interventions | Handoff | GD-S6 t5; an intervention can only be resolved by a rep today (`session_state.py:130`) | your decision | S |
| M12 | **Response contract + deterministic validator** (roadmap step 4) | Reply | Required before config B; also formalises INV text checks | M4 | M |
| M13 | **Eval-side fixtures**: golden KB fixture, scenario fixtures for facts not observable from conversation (active customer, region), structured-injectable fields for M2/M3 signals, YAML v1, re-baselined results | Eval | Without them new features cannot be tested in structured mode | M1–M4 | M |

Fixes to **existing** features (not missing, but on the same list):

| ID | Fix | Evidence | Size |
|---|---|---|---|
| F-a | Human-request phrases ("Let me talk to someone", "I still want to talk to someone") | Never recognized in 6 of 6 runs (EV-A1); the most serious safety item | S |
| F-b | Keyword false alarms: "budget", "approved"/"approve", "HubSpot" | EV-A2, EV-A3 | S |
| F-c | Repetition: follow-up holding copy and loop-breaker selection | EV-A4, EV-A5; known gap POL-26 | S–M |
| F-d | COMMITMENT without a buying signal: code vs `soul.md:197` | `trust_state_machine.py:56-60` | S (after your decision) |
| F-e | Frustration action consistency TODO | `rep_assist_engine.py:21-25` | S |

---

## 4. Prioritization

**Method (proposed):** priority = (does it block your ultimate goal or a safety rule?) first, then how many failures/metrics it unblocks, then cost. Dependencies are respected.

| Rank | Item(s) | Why here |
|---|---|---|
| 1 | **Decisions** (section 6): handoff taxonomy, RELAY meaning, KB-miss behaviour, qualification criteria sign-off. Start **KB content approval** in parallel (long pole, no code) | They define bugs vs features for ~120 failures; KB content is owner work |
| 2 | **F-a, F-b** (and M1 once decided) | Smallest changes; F-a is a missed-intervention safety failure; measured on the held-out set to avoid overfitting (`CLAUDE.md`) |
| 3 | **M3 memory → M2 qualification evaluator → M7 terminal outcome** (the "qualification spine") | Delivers your ultimate goal (qualified handoff) and makes the success metric computable; unblocks M5, M6, M8, M9 and 32 state failures |
| 4 | **M4 KB + router (+ M10)** | Resolves accountability, security and pricing behaviour with the retrieve-then-alert rule; needs approved content from step 1 |
| 5 | **M6 relay trigger, M5 poor-fit, M8 contact/unknown, M9 question policy** | Build on the spine; complete the scenario set |
| 6 | **F-c, F-d, F-e, M11** | Quality items once structure is in place |
| 7 | **M13 fixtures + YAML v1 + re-run config A; freeze baseline** | Needed from step 3 on (each feature ships with its fixtures); the freeze is the gate before any LLM |
| 8 | **M12 contract + validator**, then **config C** (LLM extraction into the frozen labels) and **config B** (phrasing) | Only after the config A baseline; the LLM's real jobs are paraphrase detection in the topic router and signal extraction |

**Exit criteria per step (proposed, measurable with the existing runner):** step 2: PERT-5 passes in all scenarios, GD-S1 t3/GD-S2 t2/t4 no longer fire false triggers, held-out result not worse; step 3: state-layer failures from 32 to 0, `terminal.outcome` present on every session; step 4: GD-S4 and GD-S5 t2–t4 replies contain no claim, a notice/alert is raised on each miss, no loop-breaker on those turns; step 7: config A baseline recorded with zero invariant violations.

---

## 5. How this changes the picture (relationship summary)
- Your RELAY and the qualified handoff both depend on **one thing that does not exist**: a qualification state (M2) built on remembered signals (M3). That is why it is the spine.
- The knowledge base is the **front door** to the ALERT path for accountability, security and pricing: retrieve first, alert on a miss. It also supplies the verified-claims list that the invariants lack (M10).
- Existing rules (human-request detection, keyword triggers) are the **safety floor** under everything; fixing them is cheap and independent.

---

## 6. Decisions and Open Questions

Please answer or redirect; I will not assume them.

- **Q-H1.** Is RELAY as "the agent is unsure whether the lead qualifies, so a rep reviews" compatible with today's RELAY mechanics (rep approves drafts; customer sees nothing until approved)? Or should the agent keep talking to the customer while the rep is asked to decide?
- **Q-H2.** In `relay`, what does the customer see: a continued conversation, or "a person will review this"?
- **Q-H3.** "Ready to sign today" (GD-S2 t5) with signals missing: `relay` (rep decides) or keep collecting signals first (question policy, M9) up to N turns?
- **Q-H4.** Should an explicit human request during `relay` (or any state) always win and become `alert`? (Proposed: yes, `human_request` is unconditional today, `handoff_manager.py` docstring.)
- **Q-K1.** Does a KB miss hold the conversation (ALERT) or notify and continue? (Proposed above: hold only for commitment-type topics.)
- **Q-K2.** Who approves KB entries, and what is the minimum entry format (topic, approved wording, source, status, last reviewed)? Which of K01–K15 are approved now?
- **Q-K3.** May the KB answer accountability questions from `soul.md` principles ("a person reviews before any commitment", honest summaries)? That is a product claim.
- **Q-Q1.** Which qualification signals are **required** for `qualified`, and which are optional? (`QUALIFICATION_CRITERIA.md` has a draft: please confirm or edit.)
- **Q-Q2.** How many turns/questions may the agent spend collecting signals before it declares `uncertain` and relays?
- **Q-Q3.** Should the agent ever tell the customer they are not a fit (`disqualified` outcome), or only stop pursuing and offer resources?
- **Q-S1.** Which items of section 3 do you want to drop from scope for now (the YAML cases they feed would be marked expected-fail)? My suggestion: nothing is dropped, but M12 and the LLM steps wait.

## 7. What I can do next (not started)
1. Write the golden KB fixture format and the topic list (no source changes).
2. Draft `scenarios_v1.yaml` as a **new file** with the section 2.4 changes, for your review (v0 stays untouched).
3. Update the visualization to the three-handoff model and the backlog IDs.
