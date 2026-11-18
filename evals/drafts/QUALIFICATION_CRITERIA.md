# Qualification criteria and ground-truth labels (DRAFT)

Per your instruction: criteria are written **independently of the agent's scorecard** (no use of `fit_criteria.py` scores or the 0–100 score bar as a label source), drafted from your docs, and each is flagged for whether it is **observable from a conversation**. Labels: **[docs]** from your docs (file cited), **[code]**, **[proposed]**. Anything ambiguous is listed in Open Questions at the end; none was resolved by guessing.

## 1. Labels (three separate, plus a case type) [docs: your instruction]
| Label | Meaning [proposed wording] |
|---|---|
| `qualified` | Meets all required criteria below (Q-1…) and no disqualifier; should be handed to a rep with company-domain contact |
| `disqualified` | Meets any disqualifier (D-1…) on an explicit statement or verified fact |
| `needs_human_handoff` | A real trigger requires a person regardless of fit (human request, frustration, commitment demand, pricing negotiation, contract/legal ask, per `trigger_catalog.py:47–55` **[code]**). Independent of qualified/disqualified |
| case type `reengagement_after_disqualification` | A previously disqualified visitor returns; expected behavior is a separate scenario (Q-open: see §5) |
These are labels on a *scenario's ground truth*, not agent output. A scenario can carry `needs_human_handoff` together with `qualified` or `disqualified`; the combination is recorded, not collapsed (Open Question A).

## 2. Disqualifiers (D) — from `ICP_DRAFT.md` 3.4 and `PLANNING_LOG.md` 2026-11-14/15 **[docs]**
| ID | Criterion | Observable from conversation? |
|---|---|---|
| D-1 | Region outside EMEA and the Americas ("AMS" read as Americas, unconfirmed) | Yes, if the visitor states it; else unknown |
| D-2 | Invalid contact details (no working business email/phone, one retry) | Partly: format is observable, deliverability is not |
| D-3 | No buying authority **and** no path to someone with it | Yes, only on explicit statement; "champion with a path" is not disqualified |
| D-4 | Active customer or open deal | **No** — lives in the team's CRM; not observable from a conversation. Needs a fixture field on the scenario |
| D-5 | No budget or no plan to buy within 6 months | Yes, only on an **explicit** statement; "unknown/not yet decided" is not a "no" (ICP_DRAFT 3.4, R39 in design) |

## 3. Qualification criteria (Q) — from the "five criteria to accept a lead" (`PLANNING_LOG.md` 2026-11-14) and `ICP_DRAFT.md` 3 **[docs]**
| ID | Criterion | Observable? | Note |
|---|---|---|---|
| Q-1 | Data validity and reachability: a company-domain contact captured (your success-event wording) | Yes (email domain vs free-mail) | "Company-domain" rule itself is new text from your reply; the ICP draft says "work email preferred" |
| Q-2 | ICP fit: B2B, inbound-led or hybrid; has a CRM/system of record with API; size or inbound load vs capacity (≈50–1,000 employees, smaller with heavy inbound; ≥~300 inquiries/month or > ~10–12 per rep per day) | Partly: motion, stack and load are statable; size/volume numbers are placeholders (ICP_DRAFT 3.1, 6) |
| Q-3 | Score threshold (≥60, or 45–59 with a strong intent action) | **Excluded as ground truth** — depends on the agent's scorecard, which you said not to use. No scoring model exists anyway (ICP_DRAFT 4) **[docs]** |
| Q-4 | Intent and timing: pain stated, asked for pricing/pilot/person, plan within 6 months | Yes, from visitor statements |
| Q-5 | Reachable decision-maker: economic buyer, or a champion with a path to one (ICP_DRAFT 3.2) | Yes, from statements; "who decides" is one of the five readiness fields |
Five readiness fields (budget, timeline, who decides, decision process, security and compliance) **[docs: PLANNING_LOG 2026-11-15]** feed Q-4/Q-5/D-3/D-5; *security and compliance* has no accept/disqualify rule written, so it is recorded but not labelled.

**Proposed rule:** `qualified` = Q-1, Q-2 (motion + stack + load/band not "Outside"), Q-4 and Q-5 true, no D; Q-3 omitted. Ambiguity on any criterion → label is `unknown_criterion`, and the scenario is excluded from precision/recall until you rule (Open Question C).

## 4. Annotation protocol **[proposed, from your reply]**
1. You label ground truth **before** running the agent on a case; labels are frozen in the dataset file with a timestamp.
2. A second annotator labels a sample of 20–30 cases blind; report Cohen's kappa (per label) and the disagreement list. Threshold for "labels usable" is not set (Open Question D).
3. LLM output is never ground truth. LLMs may be used only to *suggest* candidate scenarios, which you label.
4. Rep acceptance and opportunity conversion are long-term outcome measures; **not used in evals now** (SUCCESS_METRICS Group 4 marked deferred).

## 5. Case types [proposed]
`qualified`, `disqualified` (one case per D-n), `needs_human_handoff` (one per trigger), `informational_only` (product Q&A, no handoff), `reengagement_after_disqualification` (visitor returns after D-n; what should happen is **undefined in your docs**, Open Question E), plus boundary cases for "unknown is not a no".

## Open Questions (this file)
- **A.** When a scenario is both `qualified` and has a human trigger (e.g. asks for a person), is the expected terminal outcome "qualified-and-handed-to-rep" or "handed to a human on a real trigger"? SUCCESS_METRICS treats them as distinct terminals; one handoff must not count twice.
- **B.** "Company-domain contact": is a free-mail address (gmail) a Q-1 failure, a D-2 invalid contact, or acceptable with a note? ICP draft only says "work email preferred".
- **C.** Not observable from a conversation: D-4 (customer/open deal), the score threshold, email deliverability, security-and-compliance readiness. Provide a scenario fixture field for D-4, or exclude it?
- **D.** Agreement threshold and who the second annotator is.
- **E.** Expected agent behavior on re-engagement after disqualification (polite same decline, reconsider on changed facts, route to a person?). Not defined in your docs.
- **F.** Is the "no timeline = nothing within 6 months" horizon final? It is marked "decided" in ICP_DRAFT 3.4, while PLANNING_LOG 2026-11-14 records the opposite (nurture) and 2026-11-15 supersedes it. Confirm the later entry stands.
- **G.** Size/volume bands (50–1,000 employees; 150/250/300 inquiries a month; $15K ACV) are placeholders in your doc. Are they labels or only guidance?
- **H.** "AMS" = Americas? (unconfirmed in PLANNING_LOG 2026-11-16.)
