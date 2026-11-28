# Northstar ICP: research and draft definition

Status: **draft hypothesis for the owner to decide. Not a statement of fact about Northstar's market.** Written 2026-11-15; evidence re-checked against the source pages the same day after the network settings were changed.

**How to read this.** Part 1 says what Northstar is, as the owner described it. Part 2 is the evidence, and says for each claim whether I opened the source.
Part 3 is the draft ICP (accounts, people, triggers, disqualifiers). Part 4 is a score sketch for the "lead score bar". Part 5 maps the ICP to what
the widget can and cannot learn. Part 6 explains the demo's small-volume rule. Part 7 lists decisions only the owner can make. Part 8 lists sources and what I could not verify.

---

## 1. What Northstar is, for ICP purposes

From the owner (2026-11-15): Northstar is an **API product that integrates with any CRM**. The conversational widget and the lead operational workspace are
**demos** that show the agent's behavior and how it collaborates with humans. They are not the product being sold.

What that means for the ICP:

1. **There are two audiences.** The *customer* (the company that would integrate Northstar into its inbound flow) and the *demo audience* (the people who judge it from the widget and workspace). Usually the same roles, so one ICP serves both.
2. **"Any CRM" changes the stack criterion.** It is not "uses HubSpot or Salesforce". It is "has a system of record with an API or webhooks that Northstar can write to". A shared inbox with no system of record has nowhere to write, which is why the demo already treats "no CRM" as a weak signal.
3. **An API product adds a technical evaluator.** The person who will integrate it (RevOps engineer, solutions or sales engineer, a developer) has a say alongside the person who owns the sales outcome. Evaluation guides say API connectors add latency and a maintenance job that RevOps ends up owning (search-summary source only, see 2.4), so integration effort is a buying criterion, not a footnote.
4. **A possible second customer type, not researched:** consultancies, agencies or platforms that embed Northstar for their own clients. An API product often sells this way. I did not research it. It is a decision for the owner (Part 7).

---

## 2. Evidence

**Method.** On 2026-11-15 I opened six source pages directly (the MIT/InsideSales study, the Workato study, Qualified's home page, the RevOps Co-op routing guide, a
Kickscale capacity page and Rework's buyer-persona page). Every claim below says whether I **opened** the source or only saw it in a **search summary**.
Nearly every source is a **vendor or a vendor-sponsored blog**, so none is independent evidence; I note who ran or paid for each.

### 2.1 Why response speed matters (what the product is for)

**Opened: the InsideSales.com / MIT "Lead Response Management" study (presented 2007).**
- It examined **3 years of data from six companies**, covering **over 15,000 web leads and over 100,000 call attempts**, run by InsideSales.com (a sales-software vendor) with an MIT faculty fellow.
- Findings it states: the odds of **contacting** a lead called in 5 minutes versus 30 minutes drop **100 times**; the odds of **qualifying** drop **21 times**. The odds of contacting fall by over 10 times, and of qualifying by over 6 times, in the first hour.
- What it measured: **phone call attempts to web-form leads.** It says it "did not address close ratios", and each company defined "qualified" its own way (often an appointment set). It says nothing about chat, email or an AI agent.
- **Corrections to what circulates.** The Workato article (below) attributes the figures to "the Harvard Business Review" and says odds fall "400% when response time goes from 5 to 10 minutes". The study I opened is not HBR's, and it contains no 5-versus-10-minute figure. Treat both as errors in secondary writing.

**Opened: Workato, "B2B Lead Response Times: What We Learned from 114 Companies" (19 March 2026; Workato sells integration and automation software).**
- Method: the authors submitted **demo requests to 114 B2B companies** and watched the responses.
- Findings: more than **99% did not respond within 5 minutes**. Email: 1 of 114 sent a personalized email within 5 minutes, the average took **11 hours 54 minutes**, and nearly 1 in 5 sent none. Phone: only **31%** called, on average after **14 hours 29 minutes**, none within 5 minutes, and 42% of those who called did so within the hour. Companies using a lead-routing tool averaged **3 hours 32 minutes**; those without one nearly **13 hours**.
- **Use in the ICP:** slow response is close to universal, so on its own it does **not** separate a good account from a poor one. It is a pain signal to combine with volume and motion. The agent must never quote any of these figures to a visitor as a result Northstar delivers (R13).

### 2.2 Capacity: when manual triage stops working
- **Opened (Kickscale, a revenue-software and consulting firm):** "An SDR can process about **15 new Marketing Qualified Leads per day**." It cites no study. That is about 300 a month.
- **Search summary only:** a wider band of 50 to 100 leads a week with quality falling above about 60, and a routing vendor's claim that at 30 or more inbound leads a day manual oversight is unrealistic. Unverified.
- Conversion differs by intent (reported at 5 to 10% for ebook or webinar leads and 75 to 80% for demo requests; search summary only), so a bare volume count is a weak signal.

### 2.3 Funnel benchmarks disagree (search summaries only)
- MQL to SQL medians are quoted at 13 to 15% by some sources and 30 to 40% by others, mostly because each defines an MQL differently. The best-known source page returned an access error (403), so I could not open it.
- I found **no usable benchmark for monthly inbound lead volume by company size.**

### 2.4 Who buys, and how they evaluate
- **Opened (Rework, "AI sales ops buyer persona"; Rework sells software).** This persona is for **AI sales operations** (forecasting and scoring), a neighbouring category, not specifically lead-conversation tools. It describes: title **VP Sales Operations, Director of RevOps or Senior Sales Ops Manager with budget influence**; mid-market B2B SaaS, usually Series A to C; **25 to 150 reps**; **ACV $15K to $150K** with 30 to 90 day sales cycles; **Salesforce (most common) or HubSpot**; trigger moments such as a missed forecast, rep attrition from admin burden, or a CRO asking for pipeline visibility; **30 to 90 days from trigger to vendor selection**; a **champion** (RevOps lead) who runs the evaluation and an **approver** (CRO or CFO) who signs; top objections "our data isn't clean enough", "reps won't trust it" and "we don't have bandwidth to implement". It also says companies with **fewer than 10 dedicated reps** should wait.
- **Opened (RevOps Co-op, "A Tactical RevOps Guide to Smarter Lead Routing", August 2025; sponsored by RevenueHero, a routing vendor).** It says lead routing is a RevOps job and tells readers to check whether **"persona and ICP fit [is] built into your logic"**, to build **strong lead-to-account matching**, to write **clear rules for leads tied to existing customers**, to use **ownership lookups** (if an AE or CSM already owns the account, route back to them, not to the BDR queue), and to use capacity limits in round-robin.
- **Search summaries only:** criteria such as native two-way CRM sync ranked first, evaluating exceptions more than happy paths, and keeping qualification separate from routing because the buyer defines "qualified".
- **Use in the ICP:** the objections above are the ones the evaluation scenarios already test (S1 "reps ended up ignoring the scores", S5 "we can't afford to disrupt our routing"). The ownership-lookup rule supports routing an existing customer to the account owner instead of rejecting them (4.5).

### 2.5 The competitive field
- **Opened (Qualified home page).** Qualified now markets **"Piper the AI SDR Agent"** to **marketers**: it greets website visitors, captures leads, and converts qualified buyers by video, voice or chat, plus email follow-up and meeting booking. It claims "hired by over 500 companies", ranks itself #1 on Salesforce AppExchange, and shows testimonials from a **CMO, VP of Marketing, VP of Demand Gen, Chief AI Officer and CEO** (including "does the work of 13 SDRs" at Sinch and a multilingual use case). All of these are the vendor's own claims.
- **Search summaries only:** Drift is described as mid-market and enterprise with established SDR teams and deal sizes above about $20,000; reported pricing for this class ranges from thousands of dollars a month into six figures a year; a large low-end field of chatbot builders pitches "qualify and sync to any CRM".
- **Use in the ICP:** the category language has moved to **"AI SDR agent"**, and the economic buyer for website-conversation tools is often a **marketing leader**, not only sales or RevOps. "CRM sync" alone does not differentiate; what Northstar builds (honest limits, deterministic decisions, human collaboration) does.

---

## 3. Draft ICP

Three bands: **Primary** (best fit), **Stretch** (fits with conditions), **Outside** (not now). These are proposals to react to.

### 3.1 Account (company) criteria

| Attribute | Primary | Stretch | Outside for now | Basis |
|---|---|---|---|---|
| **Motion** | B2B with inbound-led or hybrid sales (website forms, demo requests, webinars) | Inbound is one of several channels | Purely outbound, B2C or transactional, no inbound | 2.5; the product's purpose |
| **Industry** | B2B software and tech-enabled services | Professional services, IT services, fintech and B2B marketplaces without regulated data in the flow | Industries that need security or compliance evidence Northstar cannot yet show (health data, regulated financial data) | 2.5; the owner confirmed security and data topics are unverified |
| **Company size** | About **100 to 1,000 employees** with an SDR or sales-ops function | 20 to 99 with heavy inbound; 1,000 to 5,000 if a security review can be passed | Under 20 employees, or no sales team | 2.4 and 2.5; a hypothesis, calibrate with real accounts |
| **Sales team** | **10 or more** dedicated reps or SDRs | 3 to 9 with heavy inbound | No dedicated reps | Rework says under 10 reps should wait, but for a neighbouring category (2.4) |
| **Inbound volume** | About **300 or more qualifying inquiries a month**, or more than about 15 a day per inbound rep | **150 to 299** with slow first response | Under about 150 a month | 2.2; see Part 6 |
| **Response pain** | First response slow or inconsistent; reps sort leads by hand | Fast but inconsistent routing | No pain, or handled well by one person | 2.1 |
| **Stack** | Has a CRM or system of record with an API or webhooks (any CRM). Expect **Salesforce and HubSpot** most often (2.4, 2.5) | Spreadsheet or help desk that can accept API writes | **No system of record** (shared inbox only) | Part 1 |
| **Region and language** | Proposal: English-language inbound from the **United States, Canada and the United Kingdom** | EU and EEA once a data-handling position is verified | Everywhere else, for now | Not researched; see Part 7 |
| **Deal value** | High enough that a qualified conversation is worth a rep's time. Placeholder: **about $15K ACV or more** | Unknown | Very low value per deal | Rework cites $15K to $150K ACV and a search summary cites above $20K, both for neighbouring categories (2.4, 2.5); **no basis for a Northstar number** |

### 3.2 People (buying group)

| Role | Part in the decision | Titles |
|---|---|---|
| **Economic buyer** | Owns the revenue outcome and the budget | VP or Head of Sales, CRO, VP Revenue, Head of Growth |
| **Champion and primary evaluator** | Runs the evaluation, defines what "qualified" means | Director or VP of Sales Operations or RevOps, Marketing Operations lead |
| **Marketing owner of the website** | Often the buyer for website-conversation tools (2.5) | CMO, VP Marketing, VP or Head of Demand Generation |
| **Technical evaluator** (specific to an API product) | Judges the integration and its maintenance | RevOps engineer, solutions or sales engineer, developer |
| **Influencers** | Feel the pain every day | SDR or BDR manager, demand generation lead |
| **Gatekeepers** | Can stop the deal | Security or IT, procurement, legal |

This is what the accept criterion "reachable decision-maker" means in practice: the contact is the economic buyer, or is a champion with a path to one (R45, 4.5 of `CONVERSATION_DESIGN.md`).

### 3.3 Triggers (why now)

From the Rework persona (2.4): a missed forecast, rep attrition driven by admin burden, and a CRO asking for pipeline visibility, with 30 to 90 days from trigger to vendor selection. Hypotheses from general sales practice, not measured: an inbound volume spike (campaign, webinar or launch), slow response noticed by leadership, a hiring freeze or SDR headcount pressure, a CRM migration or new CRM, rep complaints about junk leads, expansion into a new product or region, or a failed earlier tool. The widget listens for these as intent signals; it does not ask about them directly.

### 3.4 Disqualifiers (owner's list)

| Disqualifier | Reads as, in ICP terms | Note |
|---|---|---|
| Unsupported geography | Region outside the supported list | Ask before taking contact details |
| Invalid contact details | No working business email or phone | One gentle retry, then continue without |
| No buying authority | No authority **and** no path to someone with it | A champion with a path is not disqualified |
| Active customer or open deal | Already in the CRM as a customer or open opportunity | Found on the team's side; never revealed (R38); routes to the account owner |
| **No budget or timeline** | **Disqualify (owner decision, 2026-11-15)** | Only on an **explicit** statement ("we have no budget", "no plans to buy"). "Unknown" or "not yet decided" is not a "no" (R39). The horizon for "no timeline" needs defining (Part 7). Typical evaluations run 30 to 90 days from a trigger (2.4), so a horizon of 6 months may be more realistic than 12. |

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

`FIT.volume` in `leadwise/scenarios.js` sets two numbers, **150** and **250** inquiries a month. Below 150 the engine tags the visitor `low_volume` (a negative
signal), at 250 or above `high_volume` (positive), and 150 to 249 is `mid_volume` (neutral). When negatives outweigh positives, the agent explains that
"at that scale a person answering each inquiry is likely better than software". The file says these are "illustrative, not the product's real scoring".

Under the rule of thumb in 2.2 (Kickscale's claim of about 15 new leads a day, roughly 300 a month per inbound rep), 150 is **about half of one rep's capacity** and 250 is about
**four fifths**. So the numbers are not unreasonable, but nothing here confirms them. My recommendation: capacity and response time, not a bare count, should drive this
(Part 3.1); until the owner approves a number, the agent should describe what the visitor said ("about 40 a month, read by one person") and let a person say where it starts to make sense.

---

## 7. Decisions only the owner can make

1. **Customer types:** direct B2B revenue teams only, or also consultancies, agencies and platforms that embed Northstar (not researched)?
2. **Size and industry bands** in 3.1: right starting point, or too narrow or wide?
3. **Supported regions.** I did not research this. It depends on where data is stored, which privacy rules apply (for example the EU's GDPR), language support, and whether a person covers the time zone. My placeholder is the US, Canada and the UK in English.
4. **Volume rule:** adopt the capacity-based reading, keep 150 and 250 as demo-only and unstated, or set other numbers?
5. **Score model:** accept the sketch as a starting point, or supply the weights and the bar?
6. **"No budget or timeline":** define the horizon (my placeholder is 12 months; evaluations typically run 30 to 90 days, so 6 months may fit better) and whether a stated "next fiscal year" counts.
7. **Deal value:** is there a minimum, and what is it? My placeholder is about $15K ACV, drawn from neighbouring categories.
8. **Buyer:** should the ICP include marketing leaders (CMO, demand generation) as an economic buyer or champion, alongside sales and RevOps?
9. **Sales team size:** is "10 or more reps" the right primary band for an API product, or should smaller teams with heavy inbound count?

---

## 8. Sources, and what is still unverified

**Opened and read on 2026-11-15** (each fetched through the session proxy once the network settings were changed):
- [MIT / InsideSales.com Lead Response Management study (PDF copy)](https://www.mortech.com/hs-fs/hub/25649/file-13535879-pdf/docs/mit_study.pdf) (vendor-run)
- [Workato: B2B Lead Response Times, 114 companies](https://workato.com/the-connector/lead-response-time-study/) (vendor)
- [Qualified home page](https://www.qualified.com/) (vendor)
- [RevOps Co-op: A Tactical RevOps Guide to Smarter Lead Routing](https://revopscoop.com/post/revops-guide-to-lead-routing) (sponsored by a vendor)
- [Kickscale: how many inbound leads can one SDR handle](https://www.kickscale.com/post/sales-capacity-model-how-many-inbound-leads-can-one-sdr-handle) (consultancy)
- [Rework: AI sales ops buyer persona](https://resources.rework.com/libraries/ai-for-sales-operations/ai-sales-ops-buyer-persona) (vendor)

**Seen only in search summaries, not opened:** the Powered by Search funnel benchmarks (the page returned a 403 error), Flighted, callingly.com, visionary-marketing.co.uk, Abmatic, G2, ZoomInfo,
Autobound, Leadhaste, Wonderchat and Voiceflow. Anything attributed only to those is unverified.

**Not independent.** I found no analyst report or independent study. **Better evidence to get next:** talk to 5 to 8 RevOps, sales or marketing leaders about how they run inbound today
(the strongest ICP evidence by far); read a Gartner, Forrester or G2 category report for independent segment data; and once there is real traffic, replace every guess in Parts 3 and 4 with outcomes.
