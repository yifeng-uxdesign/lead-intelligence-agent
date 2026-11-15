# Northstar ICP: research and draft definition

Status: **draft hypothesis for the owner to decide. Not a statement of fact about Northstar's market.** Written 2026-11-15.

**How to read this.** Part 1 says what Northstar is, as the owner described it. Part 2 is the evidence I found, graded for reliability.
Part 3 is the draft ICP (accounts, people, triggers, disqualifiers). Part 4 is a score sketch for the "lead score bar". Part 5 maps the ICP to what
the widget can and cannot learn. Part 6 explains the demo's small-volume rule. Part 7 lists decisions only the owner can make. Part 8 lists sources and what I could not verify.

---

## 1. What Northstar is, for ICP purposes

From the owner (2026-11-15): Northstar is an **API product that integrates with any CRM**. The conversational widget and the lead operational workspace are
**demos** that show the agent's behavior and how it collaborates with humans. They are not the product being sold.

What that means for the ICP:

1. **There are two audiences.** The *customer* (the company that would integrate Northstar into its inbound flow) and the *demo audience* (the people who judge it from the widget and workspace). Usually the same roles, so one ICP serves both.
2. **"Any CRM" changes the stack criterion.** It is not "uses HubSpot or Salesforce". It is "has a system of record with an API or webhooks that Northstar can write to". A shared inbox with no system of record has nowhere to write, which is why the demo already treats "no CRM" as a weak signal.
3. **An API product adds a technical evaluator.** The person who will integrate it (RevOps engineer, solutions or sales engineer, a developer) has a say alongside the person who owns the sales outcome. Evaluation guides say API connectors add latency and a maintenance job that RevOps ends up owning (single vendor-authored source, see 2.4), so integration effort is a buying criterion, not a footnote.
4. **A possible second customer type, not researched:** consultancies, agencies or platforms that embed Northstar for their own clients. An API product often sells this way. I did not research it. It is a decision for the owner (Part 7).

---

## 2. Evidence, graded

Grades: **A** primary or independent; **B** secondary summary of a primary study; **C** vendor-authored or single-source.
**I found no A-grade evidence.** All of it came from web search summaries; the direct page fetches were blocked by this session's network settings (Part 8).

### 2.1 Why response speed matters (what the product is for)
- The widely quoted figures come from one 2007 study (InsideSales and MIT, "Lead Response Management"): odds of contacting a lead at 5 minutes were about **100 times** those at 30 minutes, and odds of qualifying about **21 times**. Search summaries say it covered more than 15,000 web leads and 100,000 call attempts. **Grade B.**
- Caveats from the same summaries: one source says it rested on six companies; many articles misattribute it to Harvard Business Review; a later 2011 audit of 2,241 companies is cited for the "7 times" and "60 times" figures; a 2026 vendor-run study (n=28,400) reports 41% qualification within 5 minutes versus 1.9% after 24 hours (**Grade C**, a cross-check only). **Verify the original before quoting any exact multiplier.**
- **Use in the ICP:** slow or inconsistent first response is a *pain signal*, not a number to promise. The agent must never quote these figures to a visitor as a result Northstar delivers (R13).

### 2.2 Capacity: when manual triage stops working
- Published rules of thumb put an inbound SDR at about **15 leads per day**, roughly **300 a month**. Another model gives 50 to 100 a week and warns that quality drops above about 60 a week per rep. A routing vendor says that at **30 or more inbound leads a day**, manual oversight is not operationally realistic. **Grade C.** None cite a large-sample study.
- Conversion differs hugely by intent (about 5 to 10% for ebook or webinar leads versus 75 to 80% for demo requests), so volume alone is a weak signal.
- **Use in the ICP:** volume is best read against *the team's capacity and response time*, not as a single number. See Part 6.

### 2.3 Funnel benchmarks disagree
- MQL to SQL medians are quoted as **13 to 15%** by some sources and **30 to 40%** by others. The difference is mostly each source's definition of an MQL. **Grade C.**
- I found **no usable benchmark for monthly inbound lead volume by company size.**
- **Use in the ICP:** do not hard-code a conversion benchmark. Qualification definitions belong to the buyer; one guide says to keep qualification separate from routing for exactly this reason (2.4).

### 2.4 Who buys, and how they evaluate
- One guide profiles the primary buyer as a **sales operations or RevOps leader with budget influence**, at a mid-market B2B SaaS company with roughly **25 to 150 reps**. **Grade C, single source.**
- Evaluation criteria in that kind of guidance: native two-way CRM sync ranked first; routing on territory, account ownership, rep capacity and lead source; lead-to-account matching for complex CRMs; spending more evaluation time on **exceptions** than on happy-path demos; **keeping qualification separate from routing, because the buyer defines what "qualified" means**; and checking whether persona and ICP fit are built into the logic. **Grade C.**
- **Use in the ICP:** the demo should show exception handling (refusals, conflicts, unknowns, handoffs), which is exactly what the evaluation scenarios test.

### 2.5 The competitive field
- Conversational qualification vendors such as Qualified and Drift are described as targeting **mid-market and enterprise B2B** with significant inbound traffic and established SDR or sales-operations teams; one source adds deal sizes above about $20,000 for Drift and a Salesforce-native focus for Qualified. G2 reviewer data cited for Qualified shows about 70% from mid-market companies. Reported pricing conflicts widely (about $3,000 to $20,000 or more a month in one source, $20,000 to $100,000 or more a year in another). **Grade C**, mostly written by competitors.
- A large low-end field of chatbot builders pitches "qualify and sync to HubSpot, Salesforce, Pipedrive or any CRM" through native connectors, webhooks or Zapier. **Grade C.**
- **Use in the ICP:** "CRM sync" alone does not differentiate. What the owner has built (trust, honest limits, deterministic decisions, human collaboration) is the differentiator, so the ICP should favor buyers who care about *how* leads are handled, not only how many.

---

## 3. Draft ICP

Three bands: **Primary** (best fit), **Stretch** (fits with conditions), **Outside** (not now). These are proposals to react to.

### 3.1 Account (company) criteria

| Attribute | Primary | Stretch | Outside for now | Basis |
|---|---|---|---|---|
| **Motion** | B2B with inbound-led or hybrid sales (website forms, demo requests, webinars) | Inbound is one of several channels | Purely outbound, B2C or transactional, no inbound | 2.5; the product's purpose |
| **Industry** | B2B software and tech-enabled services | Professional services, IT services, fintech and B2B marketplaces without regulated data in the flow | Industries that need security or compliance evidence Northstar cannot yet show (health data, regulated financial data) | 2.5; the owner confirmed security and data topics are unverified |
| **Size** | About **100 to 1,000 employees** with an SDR or sales-ops function | 20 to 99 with heavy inbound; 1,000 to 5,000 if a security review can be passed | Under 20 employees, or no sales team | 2.4 and 2.5; a hypothesis, calibrate with real accounts |
| **Inbound volume** | About **300 or more qualifying inquiries a month**, or more than about 15 a day per inbound rep | **150 to 299** with slow first response | Under about 150 a month | 2.2; see Part 6 |
| **Response pain** | First response slow or inconsistent; reps sort leads by hand | Fast but inconsistent routing | No pain, or handled well by one person | 2.1 |
| **Stack** | Has a CRM or system of record with an API or webhooks (any CRM) | Spreadsheet or help desk that can accept API writes | **No system of record** (shared inbox only) | Part 1 |
| **Region and language** | Proposal: English-language inbound from the **United States, Canada and the United Kingdom** | EU and EEA once a data-handling position is verified | Everywhere else, for now | Not researched; see Part 7 |
| **Deal value** | High enough that a qualified conversation is worth a rep's time | Unknown | Very low value per deal | 2.5 (Drift cited above about $20,000); **no basis for a Northstar number** |

### 3.2 People (buying group)

| Role | Part in the decision | Titles |
|---|---|---|
| **Economic buyer** | Owns the revenue outcome and the budget | VP or Head of Sales, CRO, VP Revenue, Head of Growth |
| **Champion and primary evaluator** | Runs the evaluation, defines what "qualified" means | Director or VP of Sales Operations or RevOps, Marketing Operations lead |
| **Technical evaluator** (specific to an API product) | Judges the integration and its maintenance | RevOps engineer, solutions or sales engineer, developer |
| **Influencers** | Feel the pain every day | SDR or BDR manager, demand generation lead |
| **Gatekeepers** | Can stop the deal | Security or IT, procurement, legal |

This is what the accept criterion "reachable decision-maker" means in practice: the contact is the economic buyer, or is a champion with a path to one (R45, 4.5 of `CONVERSATION_DESIGN.md`).

### 3.3 Triggers (why now)

Hypotheses from the evidence and general sales practice, not measured: an inbound volume spike (campaign, webinar or launch), slow response noticed by leadership, a hiring freeze or SDR headcount pressure, a CRM migration or new CRM, rep complaints about junk leads, expansion into a new product or region, or a failed earlier tool. The widget listens for these as intent signals; it does not ask about them directly.

### 3.4 Disqualifiers (owner's list)

| Disqualifier | Reads as, in ICP terms | Note |
|---|---|---|
| Unsupported geography | Region outside the supported list | Ask before taking contact details |
| Invalid contact details | No working business email or phone | One gentle retry, then continue without |
| No buying authority | No authority **and** no path to someone with it | A champion with a path is not disqualified |
| Active customer or open deal | Already in the CRM as a customer or open opportunity | Found on the team's side; never revealed (R38); routes to the account owner |
| **No budget or timeline** | **Disqualify (owner decision, 2026-11-15)** | Only on an **explicit** statement ("we have no budget", "no plans to buy"). "Unknown" or "not yet decided" is not a "no" (R39). The horizon for "no timeline" needs defining (Part 7). |

---

## 4. A score sketch for the "lead score bar" (illustrative, to calibrate)

The owner's accept criterion 3 is a combined behavioral and firmographic score crossing an agreed bar. The backend stores a 0 to 100 lead score that a rep can set; there is no scoring model yet, and the widget's rules are demo heuristics. Below is a **transparent starting model**, not research. Weights are guesses to be replaced by real outcome data.

| Part | Points | Components |
|---|---|---|
| **Firmographic** | 40 | Industry 10 · size 10 · stack with an API 10 · region 5 · volume 5 |
| **Behavior and intent** | 40 | Asked about pricing, a pilot or a demo 10 · stated a timeline 10 · described the pain in their own words 10 · compared options or came back 5 · asked for a person 5 |
| **Readiness** | 20 | Path to a decision-maker 10 · budget status known and workable 5 · compliance needs identified 5 |

Proposed bands: **60 or more** (with a valid contact, a reachable decision-maker and no disqualifier) offer a person; **40 to 59** keep nurturing; **under 40** keep helping and do not push. Disqualifiers always override the score. The visitor never sees a score (V2, R15).

---

## 5. What the widget can and cannot learn

| ICP attribute | Can the widget learn it? | How (from `CONVERSATION_DESIGN.md` 4.4) |
|---|---|---|
| Motion, response pain | Yes | Open prompts: how inquiries arrive, what is hardest |
| Industry | Yes | "What kind of business is this for?" (L1) |
| Size | Roughly | Range chips (L2); never ask for an exact headcount |
| Volume | Yes | Range chips (L2) |
| Stack | Yes | "What happens first when one arrives?", then confirm what was inferred |
| Region | Yes | One ask at L2, before any contact ask |
| Role, who decides | Yes | Cluster (L2), neutral reach (L3) |
| Timeline | If raised | Range chips |
| Budget | Only if the visitor says so | A person asks at L4 |
| Deal value, security maturity, integration depth | **No** | A person asks |
| Existing customer or open deal | **No** | CRM lookup on the team's side |

---

## 6. The demo's small-volume rule

`FIT.volume` in `northstar/scenarios.js` sets two numbers, **150** and **250** inquiries a month. Below 150 the engine tags the visitor `low_volume` (a negative
signal), at 250 or above `high_volume` (positive), and 150 to 249 is `mid_volume` (neutral). When negatives outweigh positives, the agent explains that
"at that scale a person answering each inquiry is likely better than software". The file says these are "illustrative, not the product's real scoring".

Under the rule of thumb in 2.2 (about 15 leads a day, roughly 300 a month per inbound rep), 150 is **about half of one rep's capacity** and 250 is about
**four fifths**. So the numbers are not unreasonable, but nothing here confirms them. My recommendation: capacity and response time, not a bare count, should drive this
(Part 3.1); until the owner approves a number, the agent should describe what the visitor said ("about 40 a month, read by one person") and let a person say where it starts to make sense.

---

## 7. Decisions only the owner can make

1. **Customer types:** direct B2B revenue teams only, or also consultancies, agencies and platforms that embed Northstar (not researched)?
2. **Size and industry bands** in 3.1: right starting point, or too narrow or wide?
3. **Supported regions.** I did not research this. It depends on where data is stored, which privacy rules apply (for example the EU's GDPR), language support, and whether a person covers the time zone. My placeholder is the US, Canada and the UK in English.
4. **Volume rule:** adopt the capacity-based reading, keep 150 and 250 as demo-only and unstated, or set other numbers?
5. **Score model:** accept the sketch as a starting point, or supply the weights and the bar?
6. **"No budget or timeline":** define the horizon (for example, "no plan to buy in the next 12 months"; my placeholder, not researched) and whether a stated "next fiscal year" counts.
7. **Deal value:** is there a minimum, and what is it?

---

## 8. Sources, and what I could not verify

All claims above come from web search summaries. I tried to open four primary pages and was blocked each time by this session's allowed-domain settings:
`workato.com`, `www.mortech.com` (the MIT study PDF), `www.qualified.com` and `revopscoop.com`. To verify, add those hosts under Network access in the
environment settings and ask me to continue. Search results came from vendor sites, review roundups and blogs; **none is an independent study.**

Pages returned by search (I did not open them):
- Response time: [callingly.com state of speed to lead](https://callingly.com/blog/state-of-speed-to-lead) · [Workato, B2B lead response times](https://workato.com/the-connector//lead-response-time-study) · [visionary-marketing.co.uk lead response time 2026](https://visionary-marketing.co.uk/blog/lead-response-time-statistics-2026) · [MIT study PDF](https://www.mortech.com/hs-fs/hub/25649/file-13535879-pdf/docs/mit_study.pdf)
- Capacity: [Kickscale, how many inbound leads can one SDR handle](https://kickscale.com/post/sales-capacity-model-how-many-inbound-leads-can-one-sdr-handle) · [Boomerang, SDR productivity benchmarks](https://getboomerang.ai/glossaries/sdr-productivity-benchmarks-2026)
- Funnel benchmarks: [Powered by Search](https://www.poweredbysearch.com/blog/b2b-saas-funnel-conversion-benchmarks/) · [Flighted, MQL to SQL](https://www.flighted.co/blog/mql-to-sql-conversion-rate-benchmarks-for-b2b-saas)
- Buyer and evaluation: [Rework, AI sales ops buyer persona](https://resources.rework.com/libraries/ai-for-sales-operations/ai-sales-ops-buyer-persona) · [RevOps Coop, guide to lead routing](https://revopscoop.com/post/revops-guide-to-lead-routing) · [ZoomInfo, lead routing buyers guide](https://pipeline.zoominfo.com/operations/buyers-guide-lead-routing-software) · [Leadhaste, RevOps software selection](https://leadhaste.com/blog/revops-software-selection)
- Competitors: [Abmatic, Qualified vs Drift vs Intercom](https://blog.abmatic.ai/qualified-vs-drift-vs-intercom-for-abm-2026) · [G2, Drift vs Qualified](https://www.g2.com/compare/drift-vs-qualified) · [ZoomInfo, conversational AI for sales](https://pipeline.zoominfo.com/sales/ai-chatbots-for-sales) · [Autobound, inbound lead qualification tools](https://www.autobound.ai/blog/inbound-lead-qualification-tools)
- Vendors pitching CRM sync: [Wonderchat](https://wonderchat.io/uses/conversational-ai-lead-generation) · [Voiceflow](https://www.voiceflow.com/ai/lead-qualification-routing)

**Better evidence to get next:** talk to 5 to 8 RevOps or sales leaders about how they run inbound today (the strongest evidence for an ICP by far);
read an analyst or review-site category report (Gartner, Forrester, G2) for independent segment data; and once there is real traffic, replace every guess in Parts 3 and 4 with outcomes.
