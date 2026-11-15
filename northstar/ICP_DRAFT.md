# Northstar ICP: research and draft definition

Status: **draft hypothesis for the owner to decide. Not a statement of fact about Northstar's market.** Written 2026-11-15; evidence re-checked the same day, and
corrected again on 2026-11-16 using the separate source-verification report (`ICP_SOURCES_VERIFICATION.md`) plus my own spot checks.

**How to read this.** Part 1 says what Northstar is, as the owner described it. Part 2 is the evidence, with what was opened and what was not. Part 3 is the draft ICP
(accounts, people, triggers, disqualifiers, partners). Part 4 is the score bar. Part 5 maps the ICP to what the widget can and cannot learn. Part 6 explains the demo's
small-volume rule. Part 7 lists owner decisions (made and still open). Part 8 lists sources.

**Owner decisions recorded here (2026-11-16):** marketing leaders are a buyer or champion; smaller teams with heavy inbound count; "no timeline" means no plan to buy within **6 months**;
supported regions are **EMEA and the Americas** (written "AMS", read as Americas: please confirm); Northstar **also sells to partners**; **the score bar placeholder is accepted**; **the demo has no partner path**; **the deal-value placeholder (about $15K ACV) is accepted**.

---

## 1. What Northstar is, for ICP purposes

From the owner: Northstar is an **API product that integrates with any CRM**, and it **sells to partners as well as to direct customers**. The conversational widget and the lead
operational workspace are **demos** that show the agent's behavior and how it collaborates with humans. They are not the product being sold.

What that means for the ICP:

1. **Two audiences.** The *customer* (the company that integrates Northstar into its inbound flow) and the *demo audience* (the people who judge it from the widget and workspace). Usually the same roles.
2. **"Any CRM" changes the stack criterion.** It is not "uses HubSpot or Salesforce". It is "has a system of record with an API or webhooks that Northstar can write to". A shared inbox with no system of record has nowhere to write, which is why the demo already treats "no CRM" as a weak signal.
3. **An API product adds a technical evaluator** (RevOps engineer, solutions or sales engineer, a developer) next to the person who owns the sales outcome. It is a reasonable hypothesis that integration effort and maintenance are a buying criterion; **no source I opened says so** (the verification report found none).
4. **A second customer type: partners.** Consultancies, agencies and platforms that deploy or embed Northstar for their own clients. See 3.5. I did not research partner programs.

---

## 2. Evidence

**Method.** Sources were opened directly where possible; each claim says whether it was **opened** (by me, or by the verification session) or seen only in a **search summary**.
Nearly every source is a **vendor, an agency or a vendor-sponsored blog**. **No independent (A-grade) study was found for response-time effects at today's companies, SDR capacity,
inbound volume by company size, or MQL to SQL rates.** The line-by-line record is in `ICP_SOURCES_VERIFICATION.md`.

### 2.1 Why response speed matters (what the product is for)

**Opened: the InsideSales.com / MIT "Lead Response Management" study (presented 2007).**
- **Three years of data from six companies**, over 15,000 web leads and over 100,000 call attempts, run by InsideSales.com (a sales-software vendor) with an MIT faculty fellow.
- It states that the odds of **contacting** a lead called in 5 minutes versus 30 minutes drop **100 times** and the odds of **qualifying** drop **21 times**; contact odds fall over 10 times, and qualifying odds over 6 times, in the first hour.
- It measured **phone call attempts to web-form leads**, "did not address close ratios", and let each company define "qualified" (often an appointment). It says nothing about chat, email or AI.

**Reported by the verification session (secondary sources; the article itself was not opened): a related 2011 *Harvard Business Review* article**, "The Short Life of Online Sales Leads" (Oldroyd, McElheran, Elkington; the third author ran InsideSales).
It reports an **audit of 2,241 US companies** (37% replied within an hour, 23% never replied, an average of about 42 hours among those who did) and a **separate study of 1.25 million leads from 42 companies**:
contacting within an hour made qualifying nearly **7 times** as likely as an hour later and over **60 times** as likely as after 24 hours.

**Two things that circulate wrongly.** The 100x and 21x figures are the **2007 study's, not HBR's**, and a "400% drop from 5 to 10 minutes" figure (on the Workato page) appears in **neither** source.

**Opened: Workato, "B2B Lead Response Times: What We Learned from 114 Companies" (19 March 2026; Workato sells integration software).** The authors submitted demo requests to 114 B2B companies. More than **99%** did not respond within 5 minutes.
Email: 1 of 114 within 5 minutes; average **11 hours 54 minutes**; nearly 1 in 5 sent none. Phone: only **31%** called, averaging **14 hours 29 minutes**. Companies with a routing tool averaged **3 hours 32 minutes**, those without nearly **13 hours**.

**Search summary (via the verification session): Visionary Marketing (UK agency), 28,400 leads across 184 client accounts, Q1 2026.** Median first touch **1h 42m**, rising with company size: 38 minutes under 10 employees, 1h 47m at 50 to 200,
2h 38m at 200 to 1,000, 4h 12m at 1,000+. Agency clients only; method for selecting accounts not stated.

**Use in the ICP.** Slow response is close to universal, so on its own it does **not** separate a good account from a poor one; it is a pain signal to combine with volume and motion. The size table hints that the pain grows with company size.
The agent must never quote any of these figures to a visitor as a result Northstar delivers (R13).

### 2.2 Capacity: when manual triage stops working
- **Opened (Kickscale, a revenue-software firm; verification report):** "An SDR can process about **15 new MQLs per day**" (author's opinion, no study; assumes leads are already verified by marketing). A second Kickscale page gives a model of **50 to 100 leads a week** with quality falling above about 60 (again no study). Together that is roughly **240 to 300 leads a month per inbound SDR**.
- **Crunchbase** (a data vendor; verification report) says the same "15 a day, about 300 a month" with no source.
- **A correction to my earlier draft:** I wrote that a routing vendor says manual oversight is unrealistic at 30 or more leads a day. **That is wrong.** ZoomInfo (which I opened) uses "30 leads a day" only as a worked example: "if each SDR handles 30 leads a day and each lookup takes five minutes, that's two and a half hours a day". It sets no threshold.
- **Conversion by intent:** Crunchbase (via Operatix, an outsourced-SDR agency) says 5 to 10% for ebook or webinar leads and 75 to 80% for demo requests, with **no source**. The 5 to 10% is **lead to meeting**; the stage for 75 to 80% is not defined. Neither is opportunity or closed-won.
- **Use in the ICP:** volume is best read against the team's capacity and response time, not as a single number (Part 6).

### 2.3 Funnel benchmarks (do not hard-code)
- MQL to SQL figures vary from **13%** to **39 to 51%**. These are **averages, not medians**. The 13% traces to an agency's (First Page Sage's) cross-industry client data; the 39 to 40% (Powered by Search, an agency, no methodology) appears to be the same data cut for B2B SaaS by channel. Channel alone moves the rate from 26% (paid search) to 51% (organic). A third figure (18 to 22%, Flighted, an agency) has no source. A claim that HubSpot's report gives 13% is **not on HubSpot's own page**.
- **No usable benchmark for monthly inbound volume by company size.** The nearest data are the response-time table above and RevenueHero's meeting and disqualification rates by size (vendor; volume not given).
- **Use in the ICP:** qualification definitions belong to the buyer (2.4). Use the customer's own funnel, not an outside number.

### 2.4 Who buys, and how they evaluate
- **Opened (Rework, "AI sales ops buyer persona"; Rework sells software).** A persona for **AI sales operations** (forecasting and scoring), a neighbouring category: title **VP Sales Operations, Director of RevOps or Senior Sales Ops Manager with budget influence**; mid-market B2B SaaS, usually Series A to C; **25 to 150 reps**; **ACV $15K to $150K**, 30 to 90 day cycles; **Salesforce (most common) or HubSpot**; triggers such as a missed forecast, rep attrition from admin burden, or a CRO asking for pipeline visibility; **30 to 90 days from trigger to vendor selection**; a champion (RevOps lead) and an approver (CRO or CFO); top objections "our data isn't clean enough", "reps won't trust it", "we don't have bandwidth to implement". It says companies with **fewer than 10 dedicated reps** should wait. **The owner has decided smaller teams with heavy inbound count**, so this size rule is not adopted.
- **Opened (RevOps Co-op, routing guide, August 2025; sponsored by RevenueHero, a routing vendor).** Lead routing is a RevOps job; check whether **"persona and ICP fit [is] built into your logic"**; build **lead-to-account matching**; write **clear rules for leads tied to existing customers**; use **ownership lookups** (if an AE or CSM already owns the account, route back to them, not to the BDR queue); use capacity limits in round-robin.
- **Confirmed by the verification session (LeadHaste, an outbound agency):** spend more evaluation time on **exceptions** than on happy paths; **keep qualification separate from routing**, because the buyer defines "qualified".
- **A correction to my earlier draft:** I wrote that native two-way CRM sync is "ranked first" among criteria. **No source ranks it first**; ZoomInfo's guide lists it sixth of seven.
- **Use in the ICP:** the objections above are the ones the evaluation scenarios already test (S1, S5). The ownership-lookup rule supports routing an existing customer to the account owner instead of rejecting them.

### 2.5 The competitive field
- **Opened (Qualified home page).** Qualified markets **"Piper the AI SDR Agent"** to **marketers** (greets visitors, converts them by video, voice or chat, follows up by email, books meetings); claims "hired by over 500 companies" and #1 on Salesforce AppExchange; testimonials from a **CMO, VP Marketing, VP Demand Gen, Chief AI Officer and CEO**. All vendor claims.
- **Independent-ish (G2, a review site whose placements vendors buy; verification report):** Qualified reviewers are about **70% mid-market** (9% small business, 21% enterprise); Drift reviewers about **52% mid-market** (26% small business, 23% enterprise). It shows who writes reviews, not who buys. G2 has an **"AI SDRs"** category (485 products) with Qualified as Leader; Gartner published an "Innovation Insight" note on AI SDR agents (February 2025; abstract only).
- **Drift is being sunset.** Clari + Salesloft announced in March 2026 a gradual sunset of Drift and a referral of its customers to **1mind** (a press release the verification session read; I could not open the original, which returned 403, but trade-press search results agree). The live comparisons are therefore **Qualified (Piper), 1mind, Salesforce's and HubSpot's own agents**, not Drift.
- **A correction to my earlier draft:** the "deal sizes above about $20,000" attributed to Drift is **not in any source opened**. Reported pricing in this class is vendor-quoted and conflicts (for example $2,500 a month on G2 for Drift; $3,000 to $20,000+ a month for Qualified from a competitor with no source).
- **Use in the ICP:** the category language is now **"AI SDR agent"**, and the economic buyer for website-conversation tools is often a **marketing leader** (decided: included). "CRM sync" alone does not differentiate; honest limits, deterministic decisions and human collaboration do.

---

## 3. Draft ICP

Three bands: **Primary** (best fit), **Stretch** (fits with conditions), **Outside** (not now). Items marked **(decided)** are owner decisions; the rest are proposals.

### 3.1 Account (company) criteria

| Attribute | Primary | Stretch | Outside for now | Basis |
|---|---|---|---|---|
| **Motion** | B2B with inbound-led or hybrid sales (website forms, demo requests, webinars) | Inbound is one of several channels | Purely outbound, B2C or transactional, no inbound | 2.5; the product's purpose |
| **Industry** | B2B software and tech-enabled services | Professional services, IT services, fintech and B2B marketplaces without regulated data in the flow | Industries that need security or compliance evidence Northstar cannot yet show (health data, regulated financial data) | 2.5; the owner confirmed security and data topics are unverified |
| **Company size** | About **50 to 1,000 employees** | 20 to 49 with heavy inbound; 1,000 to 5,000 if a security review can be passed | Under 20 employees with light inbound | A hypothesis; calibrate with real accounts |
| **Inbound load vs sales capacity** *(decided: smaller teams with heavy inbound count)* | Inbound that **outstrips the team's capacity**, whatever the team's size: roughly more than 10 to 12 new inquiries per rep per day (the low end of the 12 to 15 a day capacity range in 2.2) | Near capacity, or fast but inconsistent routing | Inbound a person can read and answer comfortably; **or nobody who can take a handed-off conversation** | 2.2; replaces a headcount rule |
| **Inbound volume** | About **300 or more qualifying inquiries a month**, or the load above | **150 to 299** with slow first response | Under about 150 a month | 2.2; Part 6 |
| **Response pain** | First response slow or inconsistent; reps sort by hand | Fast but inconsistent routing | Handled well by one person | 2.1 (near-universal, so combine with volume) |
| **Stack** | Has a CRM or system of record with an API or webhooks (any CRM); expect Salesforce and HubSpot most often | Spreadsheet or help desk that accepts API writes | **No system of record** (shared inbox only) | Part 1; 2.4, 2.5 |
| **Region** *(decided)* | **EMEA and the Americas** | none yet | **Asia-Pacific and anywhere else, for now.** Also any country the business cannot legally serve (a legal decision) | Owner. See the notes below |
| **Deal value** | High enough that a qualified conversation is worth a rep's time. Placeholder: **about $15K ACV or more** | Unknown | Very low value per deal | Rework cites $15K to $150K for a neighbouring category; **no basis for a Northstar number** |

**Notes on the region decision.**
1. "AMS" is read as the **Americas**. Please confirm.
2. **A supported region is not a supported language.** EMEA is many languages; the widget speaks English. The owner needs to decide which languages are supported, and the agent should not imply otherwise.
3. **A supported region is not a compliance claim.** EMEA brings data-protection obligations (for example the EU's GDPR). Security and data handling are still an unverified topic, so the agent must say "a person can tell you" and must not claim compliance (R13).
4. **Restricted countries.** EMEA and the Americas include places under sanctions or export restrictions. Which of them to exclude is a legal decision, not something I can determine.
5. **Time zones.** EMEA plus the Americas covers most of the working day. The workspace stand-in can show who is on duty, but real coverage is an operational decision.

### 3.2 People (buying group)

| Role | Part in the decision | Titles |
|---|---|---|
| **Economic buyer** | Owns the revenue outcome and the budget | VP or Head of Sales, CRO, VP Revenue, Head of Growth |
| **Marketing owner of the website** *(decided: included)* | Often the buyer or champion for website-conversation tools (2.5) | CMO, VP Marketing, VP or Head of Demand Generation |
| **Champion and primary evaluator** | Runs the evaluation, defines what "qualified" means | Director or VP of Sales Operations or RevOps, Marketing Operations lead |
| **Technical evaluator** (specific to an API product) | Judges the integration and its maintenance | RevOps engineer, solutions or sales engineer, developer |
| **Influencers** | Feel the pain every day | SDR or BDR manager, demand generation lead |
| **Gatekeepers** | Can stop the deal | Security or IT, procurement, legal |

This is what the accept criterion "reachable decision-maker" means in practice: the contact is the economic buyer, or a champion with a path to one.

### 3.3 Triggers (why now)
From the Rework persona (2.4): a missed forecast, rep attrition driven by admin burden, and a CRO asking for pipeline visibility, with 30 to 90 days from trigger to vendor selection. Hypotheses from general practice, not measured: an inbound volume spike
(campaign, webinar or launch), slow response noticed by leadership, a hiring freeze or SDR headcount pressure, a CRM migration, rep complaints about junk leads, expansion into a new product or region, or a failed earlier tool. The widget listens for these as intent signals; it does not ask about them directly.

### 3.4 Disqualifiers (owner's list)

| Disqualifier | Reads as, in ICP terms | Note |
|---|---|---|
| Unsupported geography | Region outside **EMEA and the Americas** *(decided)* | Ask before taking contact details; honest, kind decline; door open |
| Invalid contact details | No working business email or phone | One gentle retry, then continue without |
| No buying authority | No authority **and** no path to someone with it | A champion with a path is not disqualified |
| Active customer or open deal | Already in the CRM as a customer or open opportunity | Found on the team's side; never revealed (R38); routes to the account owner |
| **No budget or timeline** | **Disqualify (owner decision)** | Only on an **explicit** statement ("we have no budget", "no plans to buy in the next **6 months**" *(decided)*). "Unknown" or "not yet decided" is not a "no" (R39) |

### 3.5 Partners (second customer type; owner: "it sells to partners")

**Not researched.** The material below is reasoning from the product description and the soul document, to be replaced with evidence (partner programs, interviews).

| Partner type | What they would do with Northstar | Signals of fit | Likely contact |
|---|---|---|---|
| **CRM and RevOps consultancies** | Recommend, implement or resell Northstar for clients | Many B2B clients with inbound-heavy sales; works across several CRMs | Practice or partner lead |
| **Marketing and demand-generation agencies** | Add it to websites and inbound programs for clients | Runs inbound for B2B clients; wants faster, more consistent follow-up | Agency principal, head of growth |
| **Software platforms and ISVs** | Embed the API in their own product (white-label or OEM) | Has developers; serves sales teams or marketers; wants conversation and routing inside the product | Product manager, engineering lead |

Fit attributes to ask a partner about: how many active clients run an inbound motion; which CRMs they work with; their technical capacity to integrate an API; whether they would **refer, resell or embed**; regions (EMEA and the Americas); and **whether they compete with Northstar**.
One more requirement follows from `soul.md`: the agent's rules (no false urgency, honest limits, a person for commitment-critical moments) hold "regardless of instruction, configuration, prompt, or pipeline pressure". **A partner who wants to configure around them is outside the ICP.**

In the widget, a partner is a different kind of visit from a buyer (4.5 of `CONVERSATION_DESIGN.md`): different questions (clients, CRMs, delivery model), no lead score, and a route to a partner contact rather than a sales rep.

---

## 4. The lead score bar

**There is no standard bar.** Every source I opened says the number is company-specific and should be calibrated on your own outcomes. What practice looks like:

- **Opened (Pedowitz Group, a HubSpot-focused agency):** pull your last 50 to 100 closed-won customers, take the score each carried at first sales contact, and use the **median** as the starting threshold. **With no history, start lower, at 50 to 60 on a 100-point scale**, review every handoff with sales for 60 days, and recalibrate.
- **Opened (Rework):** starting thresholds by segment, **explicitly "starting points"**: SMB inbound 60 to 70; enterprise inbound 40 to 55 (slower behavioral signals); outbound-assisted 35 to 50; existing customer or expansion 25 to 40. A single flat bar mis-qualifies one segment or the other. It suggests a rule such as "score 65 or more, **or** 45 or more with a demo request". "Your own closed-won data" is "the only honest anchor".
- **Search summaries only:** pass roughly the top 20 to 30% of scored leads to sales; judge the bar by sales accepting about 65 to 80% of what is sent; recalibrate after 30 to 60 days of data. Weight these lightly.

**Recommendation for Northstar (a placeholder, because there is no outcome history yet):**

| Score (0 to 100) | Meaning | Condition |
|---|---|---|
| **60 or more** | Offer a person | With a valid contact, a reachable decision-maker, and no disqualifier |
| **45 to 59, plus a strong intent action** (asked for a person, pricing or a pilot) | Offer a person | Mirrors Rework's "or 45 with a demo request" rule |
| **40 to 59** otherwise | Nurture | |
| **Under 40** | Keep helping, do not push | |

Disqualifiers always override the score. Existing customers and partners do not use this bar (they route elsewhere). Calibrate after the first **50 to 100 handoffs**: move the bar until reps accept roughly **65 to 80%** and about **15 to 30%** of conversations pass.
**Accepted by the owner, 2026-11-16.** The bar is a demonstration setting and the workspace should say so. The visitor never sees a score (V2, R15).

**The sketch that feeds it (my guesses, to be replaced by outcome data):**

| Part | Points | Components |
|---|---|---|
| **Firmographic** | 40 | Industry 10 · size or load 10 · stack with an API 10 · region 5 · volume 5 |
| **Behavior and intent** | 40 | Asked about pricing, a pilot or a demo 10 · stated a timeline 10 · described the pain in their own words 10 · compared options or came back 5 · asked for a person 5 |
| **Readiness** | 20 | Path to a decision-maker 10 · budget status known and workable 5 · compliance needs identified 5 |

The backend stores a 0 to 100 lead score that a rep can set; there is no scoring model yet.

---

## 5. What the widget can and cannot learn

| ICP attribute | Can the widget learn it? | How (from `CONVERSATION_DESIGN.md` 4.4) |
|---|---|---|
| Motion, response pain | Yes | Open prompts: how inquiries arrive, what is hardest |
| Industry | Yes | "What kind of business is this for?" (L1) |
| Size, inbound load | Roughly | Range chips (L2): inquiries a month and people handling them; never an exact headcount |
| Stack | Yes | "What happens first when one arrives?", then confirm what was inferred |
| Region | Yes | One ask at L2, before any contact ask; decline honestly outside EMEA and the Americas |
| Role, who decides | Yes | Cluster (L2), neutral reach (L3) |
| Timeline | If raised | Range chips; "no plan within 6 months" only when said |
| Budget | Only if the visitor says so | A person asks at L4 |
| Partner or reseller | Yes | Kind-of-visit gauge (R44); then clients, CRMs, delivery model |
| Deal value, security maturity, integration depth, languages | **No** | A person asks |
| Existing customer or open deal | **No** | CRM lookup on the team's side |

---

## 6. The demo's small-volume rule

`FIT.volume` in `northstar/scenarios.js` sets two numbers, **150** and **250** inquiries a month. Below 150 the engine tags the visitor `low_volume` (negative), at 250 or above `high_volume` (positive), and 150 to 249 is `mid_volume` (neutral). When negatives outweigh
positives the agent explains that "at that scale a person answering each inquiry is likely better than software". The file calls these numbers "illustrative, not the product's real scoring".

Under the rule of thumb in 2.2 (about **240 to 300 leads a month per inbound rep**, practitioner opinion only), 150 is **about half to two thirds of one rep's capacity** and 250 is **about 0.8 to 1.0 rep**. The numbers are not unreasonable, but nothing here confirms them.
Because the owner has decided that **smaller teams with heavy inbound count**, a bare monthly count is the wrong test: a three-person team with 200 inquiries a month may be at its limit. My recommendation: judge **inquiries per rep and response time**, and until the owner approves a number the agent should describe what the visitor said
("about 40 a month, read by one person") and let a person say where it starts to make sense.

---

## 7. Decisions

**Made (2026-11-16):** marketing leaders included; smaller teams with heavy inbound count; "no timeline" = no plan within 6 months; regions = EMEA and the Americas; Northstar sells to partners, with no partner path in the demo; score bar and deal-value placeholders accepted; no budget or timeline disqualifies (explicit statements only).

**Still open**
1. Confirm "AMS" means the **Americas**.
2. **Languages:** which are supported inside those regions?
3. **Restricted countries** inside the regions (a legal decision), and the **data-handling position** needed before saying anything about EMEA compliance.
4. ~~Score bar~~ **accepted** (Part 4). Real weights come from outcome data later.
5. **Volume rule:** adopt the per-rep reading, keep 150 and 250 internal and unstated, or set other numbers.
6. ~~Deal value~~ **accepted**: placeholder about $15K ACV.
7. **Partners:** **no partner path in the demo** (decided). The three partner types in 3.5 were not explicitly confirmed; they stay as drafted unless you say otherwise.
8. Whether the **ICP bands** in 3.1 (size, industry) are the right starting point.

---

## 8. Sources

Tags: **[opened]** I read the page; **[report]** the separate verification session read it (`ICP_SOURCES_VERIFICATION.md`); **[summary]** search summary only.

- Response time: [MIT / InsideSales.com Lead Response Management study (PDF copy)](https://www.mortech.com/hs-fs/hub/25649/file-13535879-pdf/docs/mit_study.pdf) [opened] · [Workato, 114 companies](https://workato.com/the-connector/lead-response-time-study/) [opened] · [Visionary Marketing, lead response time statistics 2026](https://visionary-marketing.co.uk/blog/lead-response-time-statistics-2026) [report] · [Callingly, state of speed to lead](https://callingly.com/blog/state-of-speed-to-lead) [report] · HBR 2011, "The Short Life of Online Sales Leads" [report; only the BYU ScholarsArchive record was opened]
- Capacity: [Kickscale, how many inbound leads can one SDR handle](https://www.kickscale.com/post/sales-capacity-model-how-many-inbound-leads-can-one-sdr-handle) [opened] · [Kickscale, inbound capacity planning](https://www.kickscale.com/amp/inbound-capacity-planning-for-sdr-teams) [report] · [Crunchbase, SDR metrics and KPIs](https://about.crunchbase.com/blog/sdr-metrics-and-kpis-what-to-expect-from-your-sales-development-team) [report] · [ZoomInfo, lead routing buyers guide](https://pipeline.zoominfo.com/operations/buyers-guide-lead-routing-software) [opened]
- Funnel benchmarks: [Powered by Search](https://www.poweredbysearch.com/learn/b2b-saas-funnel-conversion-benchmarks/) [report] · [Flighted](https://www.flighted.co/blog/mql-to-sql-conversion-rate-benchmarks-for-b2b-saas) [report]
- Buyer and evaluation: [Rework, AI sales ops buyer persona](https://resources.rework.com/libraries/ai-for-sales-operations/ai-sales-ops-buyer-persona) [opened] · [RevOps Co-op, lead routing guide](https://revopscoop.com/post/revops-guide-to-lead-routing) [opened] · [LeadHaste, RevOps software selection](https://leadhaste.com/blog/revops-software-selection) [report]
- Score thresholds: [Rework, MQL to SQL score thresholds](https://resources.rework.com/libraries/marketing-sales-alignment/mql-to-sql-score-thresholds) [opened] · [Pedowitz Group, HubSpot lead scoring](https://www.pedowitzgroup.com/blog/hubspot-lead-scoring-blog) [opened] · other lead-scoring guides [summary]
- Competitors: [Qualified](https://www.qualified.com/) [opened] · [G2, Drift vs Qualified](https://www.g2.com/compare/drift-vs-qualified) [report] · [ZoomInfo, conversational AI for sales](https://pipeline.zoominfo.com/sales/ai-chatbots-for-sales) [report] · [Abmatic, Qualified vs Drift vs Intercom](https://abmatic.ai/blog/qualified-vs-drift-vs-intercom-for-abm-2026) [report; a competitor] · [Autobound](https://www.autobound.ai/blog/inbound-lead-qualification-tools) [report] · Drift sunset: [Clari + Salesloft press release](https://www.businesswire.com/news/home/20260306534285/en/) [report; I got a 403] and trade-press coverage such as [DestinationCRM](https://www.destinationcrm.com/Articles/CRM-News/CRM-Across-the-Wire/Clari---Salesloft-Partners-with-1mind-173786.aspx) [summary]
- Vendors pitching CRM sync: [Wonderchat](https://wonderchat.io/uses/conversational-ai-lead-generation) · [Voiceflow](https://www.voiceflow.com/ai/lead-qualification-routing) [report]

**Not independent.** I found no analyst report or independent study. **Better evidence to get next:** talk to 5 to 8 RevOps, sales or marketing leaders, and 3 to 5 prospective partners, about how they run inbound today; read a Gartner, Forrester or G2 category report;
and once there is real traffic, replace every guess in Parts 3 and 4 with outcomes.
