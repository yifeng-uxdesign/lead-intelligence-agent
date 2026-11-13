# Northstar demo knowledge base (draft)

Status: **draft for owner approval. Not wired into the widget.** Written 2026-11-13.

Purpose: the approved facts the assistant may state as fact (rule R28 in `CONVERSATION_DESIGN.md`, section 4.3).
In the demo these become a small deterministic `KNOWLEDGE` table. Later, retrieval can read the same entries.

**Where these facts come from.** Only from what is already written in this repository: `intent-agent-v2/src/core/soul.md`
(the value constitution), `intent-agent-v2/CLAUDE.md` (trigger rules and modes), `intent-agent-v2/README.md`, and the
existing demo copy in `northstar/scenarios.js`. I have not invented any product fact. Because these describe the product's
design intent, **every entry below needs the owner's approval before the assistant may say it** (status `draft`).

Rules for entries: plain words anyone can follow (V1); no lead, fit, capture or demo language (V2, V3, R15); no price,
date, guarantee, number or customer claim; one short answer, then an optional related question (R25).

Status values: `draft` = from the design documents, awaiting approval. `approved` = owner confirmed. `unverified` =
the assistant does not know, and says a person can answer.

---

## Entries

### K01 · What the product is  — `draft`
- **People ask:** what is this, what does Northstar do, how does it work
- **Answer:** "Northstar's Lead Intelligence Agent is an AI assistant that has the first conversation with people who show interest in a company's product. It learns what they need, answers what it can, and brings in the right person on the sales team at the right moment."
- **Then maybe ask:** "Is this for your own team, or are you comparing options?"
- **Source:** `soul.md` (purpose, "trusted first presence"), `scenarios.js` `product.intro`

### K02 · How a conversation works  — `draft`
- **People ask:** how does it talk to people, what does it ask, is it a form
- **Answer:** "It talks like a person would, one thing at a time, and says why it is asking. It listens for what the person wants and only asks for more when that helps. It never rushes anyone."
- **Then maybe ask:** "Would you like to see how that feels, with a question about how your team handles inquiries today?"
- **Source:** `soul.md` (values 1 to 3), `DEMO_SCRIPTS.md` ("always / never")

### K03 · That it is an AI  — `draft`
- **People ask:** are you a bot, is this a real person, who am I talking to
- **Answer:** "I'm an AI assistant, not a person. It's always answered directly if someone asks, and if you'd rather talk to a person, I can bring one in."
- **Source:** `soul.md` (value 6), `GLOBAL_ROUTES.identity`
- *Note:* the existing route already answers this; this entry keeps the wording consistent.

### K04 · What it will not do  — `draft`
- **People ask:** what can't it do, will it push me, will it promise results, what are its limits
- **Answer:** "It doesn't use pressure or false urgency, doesn't promise results or dates it can't back up, and doesn't keep pushing after someone says no. If a question needs a firm commitment, it says so and brings in a person."
- **Source:** `soul.md` ("What this agent will not do"), `hesitant.boundaries`

### K05 · When a person joins  — `draft`
- **People ask:** when does a human get involved, can I talk to someone, what if I'm unhappy
- **Answer:** "A person joins when you ask for one, when a conversation is getting frustrating, or when a question needs a commitment, like pricing terms, contract or legal questions, or dates. When someone shows strong interest, the team is also told so they can step in sooner."
- **Source:** `CLAUDE.md` (decision D4, trigger taxonomy), `soul.md` (value 4)

### K06 · What the team sees  — `draft`
- **People ask:** do I have to repeat myself, does the team see this chat, what gets passed on
- **Answer:** "When a person joins, they can read the conversation and a short summary, so you shouldn't have to repeat yourself. The summary is meant to be honest: it doesn't make things sound better or worse than you said."
- **Source:** `soul.md` (values 5 and 7), `trust.reps`
- *Note:* "the team can read the conversation" is a product claim to confirm, not only intent.

### K07 · How teams work alongside it  — `draft`
- **People ask:** does it replace our reps, who is in control, can a person review what it says
- **Answer:** "It works alongside people on the sales team; it doesn't replace them. A team can let the assistant reply on its own, have a person approve replies before they're sent, or have a person lead live while the assistant helps."
- **Source:** `README.md`, `CLAUDE.md` (collaboration modes), `soul.md` (value 5)
- *Note:* mode names are internal; the plain-language wording above needs the owner's check. How RELAY and SHADOW behave when no person is online is still an open product decision.

### K08 · Your pace and your choices  — `draft`
- **People ask:** do I have to share my details, can I just look around, can I stop
- **Answer:** "You're in control. You can ask questions, skip anything you'd rather not answer, pause, or stop whenever you like."
- **Source:** `soul.md` (value 3), `trust.nosell`, `hesitant.close`

### K09 · What it does with what you share  — `draft`
- **People ask:** what happens to what I tell you, are you tracking me
- **Answer:** "What you share is used to help you, for example so you aren't asked the same thing twice. It isn't used to pressure you. For specifics about where information is kept and for how long, a person on the team should answer."
- **Source:** `soul.md` (value 7), `hesitant.privacy`
- *Note:* only the principle is stated. Storage details are `unverified` (see below).

---

## Known unknowns: the assistant says "a person can tell you"

The repository contains no verified facts on these. The assistant must not state anything about them (R13, R28). The owner
confirmed this list on 2026-11-13.

| Topic | What the assistant says |
|---|---|
| Pricing, plans, discounts, trials | "I don't have verified pricing, and I won't guess. A person on the team can tell you." |
| Integrations (CRM, helpdesk, email, calendar) | "I don't have a reliable list of what it connects to. A person can tell you." |
| Security, compliance, data storage and retention | "That's one a person should answer directly, so you get it right." |
| Setup effort, timelines, go-live dates | "I can't say how long it would take for your team. A person can look at your situation." |
| Results, numbers, case studies, customers, reviews | "I don't have verified results to share, and I won't offer any I can't back up." |
| How other products compare | "I can only speak to what Northstar is designed to do." |
| Minimum size or volume where it makes sense | "I can't give a number. A person on the team can." *(the demo's size thresholds are illustrative only)* |
| Channels and languages beyond this chat | "I can't confirm that. A person can." |
| Contracts, SLAs, guarantees | "That needs a person, and I can't promise anything on it." |

---

## Owner checklist

- [ ] Approve, edit or remove each `draft` entry (K01 to K09). Change the status to `approved` when happy.
- [ ] Add any verified facts you want the assistant to be able to state (for example integrations or security), with a source.
- [ ] Confirm the plain-language wording of K07 and the product claim in K06.
- [ ] Decide whether visitor-facing answers may name sources ("from our product documentation"), later, for retrieval.
