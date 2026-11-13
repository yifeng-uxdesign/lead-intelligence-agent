# Lead data model: what the agent gathers (draft v0.1)

Status: **draft for discussion**. Items marked **[ADDED]** are not in the Figma prompt pack. Items marked **[DECIDE]** need an owner decision.

## 1. Principles

1. **Every field earns its place.** A field exists only if it changes a decision: accept, nurture, reject, route, or what to say next.
2. **Every value carries provenance.** Source (customer-stated, agent-inferred, CRM, rep-provided), confidence, and the evidence event it came from. The rep must be able to open the evidence (Prompt 7).
3. **"Unknown" is a first-class value.** Unconfirmed means insufficient evidence, never "false". The agent does not guess to fill a gap.
4. **Ask once, ask when relevant.** Conversation memory (roadmap step 5) stops re-asking. Questions are paced to trust state: no interrogation before the customer has received value.
5. **Collect the minimum personal data.** No pressure language, and rep-internal notes never reach the customer (existing `soul.md` and `message_schema.yaml` rules).

## 2. The product context

Northstar sells an AI lead-qualification agent to B2B sales teams. A "lead" is a person at a company evaluating whether Northstar fits their sales process. So the questions below are about the *prospect company's* sales motion, not about their own customers. (The Sierra files in `intent-agent-v2/src/clients/sierra` are the example client config; the Northstar default is still an empty criteria set.) **[DECIDE: confirm this reading. The Figma fixture uses audit/compliance language that could also be read as a generic enterprise buyer.]**

## 3. Four layers of data

Layers map to the scorecard sections in the rep workspace.

### Layer A: Identity and context (who is this)

| Field | Business reason | How gathered | Status |
|---|---|---|---|
| Name, role/title, seniority | Routing, tone, and whether they can decide | Asked, or form/CRM | Prompt (header) |
| Company, size, industry | ICP fit, account matching | Inferred from email domain, CRM match, asked | Prompt (partial) |
| Contact method and consent to follow up | Required before any rep or agent outreach | Asked explicitly | **[ADDED]** |
| Source and entry point (page, campaign, referral) | Inquiry-to-lead metric and attribution | Captured automatically | **[ADDED]** |
| Existing CRM account or open opportunity | Avoid duplicate outreach; surfaces conflicts (the Dan Whitfield case) | CRM lookup | Prompt (implicit) |
| Language and timezone | Rep handoff timing, reply language | Inferred | **[ADDED]** |

### Layer B: Fit, "automatically confirmed" (should we talk to them at all)

The prompt defines four: **Business need · Product fit · Pain · Active intent**. Proposed definitions so they are measurable:

| Signal | Means | Evidence examples |
|---|---|---|
| Business need | They have a qualification or intake problem Northstar addresses | Describes manual triage, slow response, missed leads |
| Product fit | Their situation matches Northstar's ICP and has no hard disqualifier | Inbound volume, B2B motion, a CRM we integrate with |
| Pain | A cost or risk of the status quo, in their words | Lost deals, rep time wasted, audit exposure |
| Active intent | They are evaluating now, not browsing | Asks about pricing, pilot, timeline, or names alternatives |

Supporting facts the agent collects to *derive* these (all **[ADDED]** unless noted):

- **Lead volume** per month and **team size** (reps, SDRs). Northstar's value and pricing scale with these. Today `high_support_volume` is "not extractable", so this must be asked.
- **Current process and tools:** how leads are qualified today, which CRM or marketing automation. Determines integration fit and the displacement story.
- **Use case / segment:** inbound web leads, event leads, partner leads.
- **Alternatives considered:** competitors, in-house build, "do nothing". Already tracked as a context trigger.
- **Hard disqualifiers** (honest "not a fit" paths): e.g. no inbound flow, purely outbound motion, region or data-handling constraint we cannot meet. Must be defined for Northstar; the Sierra list is not reusable. **[DECIDE]**

### Layer C: Opportunity readiness (can a rep convert this)

The prompt defines four, shown as n/4: **Budget · Timeline · Economic buyer · Decision process**. Proposed field shape:

| Field | Value shape | Notes |
|---|---|---|
| Budget | Amount or range, owner, status | Prompt example: $240k confirmed |
| Timeline | Target date or quarter, driver | Q3 confirmed |
| Economic buyer | Person, role, how identified | Conflict example: customer says Sarah, CRM says Dan Whitfield |
| Decision process | Steps, approvers, procurement path | |

**[ADDED]** Two requirements that already appear in the prompt's queue (Priya Raman: data residency; Maya Chen: approval-authority conflict) but have no home in the scorecard:

- **Compliance and security requirements** (data residency, security review, DPA). Often a gating step, and the agent must not answer them without approval. Proposed as a fifth readiness field, or as a "Requirements" list below the score. **[DECIDE]** which, since it changes "n/4" to "n/5".
- **Stakeholder map:** champion, economic buyer, technical evaluator, blockers. Needed to interpret the economic-buyer field and to suggest who to multi-thread.

### Layer D: Conversation and handoff state (system-owned, not asked)

Lead mode, activity state, open interventions, trigger history, pending drafts, decision trace, next-step commitments **[ADDED: what we promised the customer and by when]**, and customer preferences about talking to a human (already in `session_state`).

## 4. Field status model

Every Layer B and C field uses one of: **Confirmed · Unconfirmed · Low confidence · Conflicting evidence** (the four treatments in Prompt 3), plus provenance:

`value · source (customer-stated | agent-inferred | CRM | rep-provided) · confidence (High | Medium | Low) · evidence event id · last updated`

Rules: a rep-provided value outranks other sources but keeps the conflicting evidence visible. A customer-stated value never silently overwrites CRM; it creates a Conflicting state until the rep resolves it.

## 5. Decisions the data must support

| Decision | Needs |
|---|---|
| Keep talking / qualify | Layer B, no hard disqualifier |
| Hand off to a rep now | Strong intent or an intervention trigger (existing taxonomy), contact consent |
| Accept: create opportunity | Fit 4/4 plus readiness threshold **[DECIDE: all four, or three with a named gap?]** |
| Nurture | Fit confirmed but readiness gaps with no near-term timeline |
| Reject | Hard disqualifier or explicit not-interested; restart on re-engage |
| Route to which rep | Region, segment, account owner **[ADDED]** |

## 6. Gaps against the current code

- `LeadSignals` and `_prospect_signals_from_lead` map to Sierra keys. A Northstar signal set (Layers B and C) needs a per-client mapping (roadmap step 6).
- Layer C (budget, timeline, economic buyer, decision process) has no extractor fields today.
- No provenance or confidence per field; the decision trace records signals per turn, not field history.
- Disposition and feedback (what happened after routing) has no data model yet; see the five-stage framing in `PLANNING_LOG.md`.

## 7. Open questions

1. Is the lead always someone evaluating Northstar itself (reading in section 2)?
2. Readiness: four fields, or add compliance and security as a fifth?
3. What is the minimum for Accept?
4. Which hard disqualifiers does Northstar want to enforce?
