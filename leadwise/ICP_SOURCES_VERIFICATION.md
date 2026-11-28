# ICP sources: verification report

Status: **research only.** This file checks the sources behind `leadwise/ICP_DRAFT.md` (branch `claude/bold-heisenberg-lvt224`), mainly Part 2 (Evidence) and Part 8 (Sources). It does not change the draft. Checked 2026-11-15.

**Method.** Every listed source was opened with WebFetch, reached through a search-result link. Direct fetches of the listed URLs were refused by the session's allowlist. A curl fallback through the session proxy was tried for the HBR article and its Internet Archive copy, and the proxy refused both (HTTP 403). Quotes are kept short. Where a page's own numbers have no stated source, that is said. "Vendor" means the publisher sells a product in or next to this category.

**Verdicts used.** **CONFIRMED**: the source says what the draft says. **CORRECTED**: the source exists but says something different, and the correct reading is given. **UNSUPPORTED**: not found in the cited source or any page opened.

---

## 1. Source-by-source record

### 1.1 Powered by Search: "B2B SaaS Funnel Conversion Benchmarks"
- **URL:** https://www.poweredbysearch.com/learn/b2b-saas-funnel-conversion-benchmarks/. The `/blog/` URL gives the same article; the `/learn/` URL opened without a 403.
- **Publisher:** Powered by Search, a B2B SaaS marketing **agency**. Author Lauren O'Bryan. Last updated 16 March 2026.
- **Numbers.** MQL to SQL: **39%** for small to mid-sized B2B SaaS ($10M–$100M ARR) and **40%** for enterprise (+$1B ARR). By channel: **51%** for SEO and **26%** for PPC.
- **Method:** **none stated.** No sample, period or calculation. The only data link is to First Page Sage, at the benchmarks section.
- **Ebook, webinar or demo-request conversion:** none. Ebooks and webinars appear only as what a visitor trades contact details for.
- **Limits:** no methodology. The figures match First Page Sage's channel data as other sites quote it, so this is probably a re-publication, not a separate dataset.

### 1.2 Flighted: "MQL to SQL Conversion Rate Benchmarks for B2B SaaS (2026)"
- **URL:** https://www.flighted.co/blog/mql-to-sql-conversion-rate-benchmarks-for-b2b-saas
- **Publisher:** Flighted, a New York performance-marketing **agency** (Meta ads and landing pages for B2B SaaS). 6 May 2026.
- **Numbers.** "the average MQL to SQL conversion rate falls between 18–22%". The cross-industry average is about **13%** and the top quartile **25–35%**. By channel: organic search 45–51%, paid search 15–26%, Meta ads 10–18%, outbound SDR 8–15%. By deal size: under $5K 25–35%, $25K–$100K 12–20%, $100K+ 8–15%.
- **Method:** **none stated.** The MQL to SQL ranges have **no cited source**.
- **Lead-source split (ebook, webinar, demo):** not given.

### 1.3 Callingly: "State of speed to lead"
- **URL:** https://callingly.com/blog/state-of-speed-to-lead
- **Publisher:** Callingly, a **vendor** of lead call-back software. Published 10 August 2026, modified 12 November 2026. No author named.
- **Content.** A review of three "research anchors": the 2007 MIT/InsideSales study (100x contact odds and 21x qualify odds at 5 versus 30 minutes), the **2011 HBR article** (a 2,241-company audit, plus 1.25 million leads from 42 companies), and Salesforce State of Sales (reps spend 28% of the week selling).
- **Own data:** **none.** The page says vendor figures should not be treated as independent research.
- **Leads per rep, "30 or more a day", inbound volume:** **not mentioned.**

### 1.4 Visionary Marketing: "Lead Response Time Statistics 2026"
- **URL:** https://visionary-marketing.co.uk/blog/lead-response-time-statistics-2026
- **Publisher:** Visionary Marketing, a UK digital-marketing **agency** (Newcastle). Author Chris Coussons, founder. 31 May 2026.
- **Study:** **28,400 leads across 184 client accounts**, 1 January to 31 March 2026, with timestamps from GA4 and CRMs. A separate Pollfish survey of 900 practitioners.
- **Numbers.** Median first touch is **1h 42m**. 27.2% of leads get a reply within 1 hour and 14.6% within 5 minutes. **Median first touch rises with company size:** 38 minutes under 10 employees, 1h 47m at 50–200, 2h 38m at 200–1,000, and 4h 12m at 1,000+.
- **Limits:** these are **agency clients** ("agency-supported client portfolios"), and the page does not say how accounts were selected. Its headline "21x" is not computed the way its own table computes it. **No monthly lead volume by company size** and **no per-SDR capacity.**

### 1.5 Abmatic: "Qualified vs Drift vs Intercom for ABM 2026"
- **URL:** https://abmatic.ai/blog/qualified-vs-drift-vs-intercom-for-abm-2026 (the blog. subdomain redirects here)
- **Publisher:** Abmatic AI, a **competing vendor** that says its own product wins. First published 10 March 2025, updated 13 May 2026. Author Jimit Mehta.
- **Numbers.** Reported pricing: Qualified **$3,000 to $20,000+ a month**, Drift **$2,000 to $10,000+ a month**, Intercom **$500 to $3,000+ a month**. Who each fits: Qualified for "mid-market to enterprise B2B SaaS" with significant inbound, Drift for "growth-stage B2B SaaS".
- **Limits:** **no source** for any price. **No $20,000 deal-size figure** and no SDR-team criterion.

### 1.6 G2: Drift vs Qualified
- **URL:** https://www.g2.com/compare/drift-vs-qualified
- **Publisher:** G2, a **review site**. It is independent of these two vendors, but vendors buy placements on it. The page shows no date.
- **Numbers.** Drift: 4.4/5 from 1,255 reviews; reviewers are **25.5% small business, 51.7% mid-market, 22.8% enterprise**; Premium **"Starting at $2,500.00 Per Month"**. Qualified: 4.9/5 from about 1,541–1,555 reviews (the page shows both counts); reviewers are **9.0% small business, 69.6% mid-market, 21.4% enterprise**; price "Contact Us". Qualified sits in G2's **AI SDRs** category and Drift does not.
- **Limits:** the segment split describes who wrote reviews, not who buys.

### 1.7 ZoomInfo: "Best Conversational AI & Chatbot Platforms for Sales in 2026"
- **URL:** https://pipeline.zoominfo.com/sales/ai-chatbots-for-sales
- **Publisher:** ZoomInfo blog, a **vendor** that lists itself first. Updated 14 June 2026.
- **Content.** Drift: "Mid-market B2B running account-based strategies". Qualified: "B2B teams invested in Salesforce". HubSpot: SMB and mid-market, with a free tier.
- **Not in it:** any dollar deal size, any Drift sunset notice, any capacity figures.

### 1.8 ZoomInfo: "10 Best Lead Routing and Lead-to-Account Matching Software for 2026"
- **URL:** https://pipeline.zoominfo.com/operations/buyers-guide-lead-routing-software
- **Publisher:** ZoomInfo, a **vendor**, with the disclosure "ZoomInfo publishes this guide, and ZoomInfo is on the list." Updated 5 October 2026. Competitor prices were checked on each vendor's site in October 2026.
- **Seven criteria, in order:** fuzzy matching; account hierarchy; matching before routing; real-time dedup; intent and capacity routing; **native two-way CRM sync (6th)**; no-code configuration.
- **The "30 a day" sentence** is a hypothetical: "If each SDR handles 30 leads a day" and each lookup takes 5 minutes, that is 2.5 hours a rep a day. The page **does not** say manual oversight becomes unrealistic and sets **no volume threshold**.
- **Prices:** Chili Piper $1,250/month for up to 15 seats; Default Growth $1,250/month ($15,000/year); HubSpot Sales Hub Professional from $90 a seat a month. LeanData, Traction Complete and LeadAngel are "contact sales".

### 1.9 Autobound: "Best AI Tools for Inbound Lead Qualification (2026)"
- **URL:** https://www.autobound.ai/blog/inbound-lead-qualification-tools
- **Publisher:** Autobound, a **vendor** of signal data, an API and an MCP server. Dated 17 September 2025.
- **Content.** Drift is "Bundled into Salesloft plans". Qualified uses custom pricing across Premier, Enterprise and Ultimate. It quotes a 13% overall B2B MQL to SQL rate against about 40% with AI qualification, citing other blogs (data-mania, Kixie, verse.ai).
- **Not in it:** a $20K deal size, SDR targeting, capacity figures, or conversion by lead source.

### 1.10 LeadHaste: "RevOps Software: Choose the Layer After Outbound"
- **URL:** https://leadhaste.com/blog/revops-software-selection
- **Publisher:** LeadHaste, an outbound lead-generation **agency** (outsourced SDRs and RevOps consulting). Author Christian Sørensen, co-founder and CEO. 10 September 2026.
- **Content.** "Your evaluation should spend more time on exceptions." "Keep qualification separate from routing," with the buyer owning what "qualified" means. On sync it says: do not stop at "two-way" (test direction, match keys, conflict rules and errors).
- **Not in it:** any ranking of criteria, and anything about API connectors adding latency or maintenance.

### 1.11 Wonderchat: "Conversational AI for Lead Generation"
- **URL:** https://wonderchat.io/uses/conversational-ai-lead-generation
- **Publisher:** Wonderchat, a **vendor** of AI chat for support and lead capture.
- **Content.** It "integrates with any helpdesk and CRM system" and claims more than 5,000 integrations, but lists six CRMs. It has a free plan; another Wonderchat page says pricing "Starts at $0.02/message". Statistics such as a 75% resolution rate have no source.
- **Limits:** the page is pitched mostly at support teams.

### 1.12 Voiceflow: "AI Agents for Lead Qualification & Routing"
- **URL:** https://www.voiceflow.com/ai/lead-qualification-routing
- **Publisher:** Voiceflow, Inc., a **vendor** of an agent-building platform.
- **Content.** The fetched page shows logos of help-desk and contact-centre tools (Zendesk, Salesforce Service Cloud, Intercom and others). It shows no prices and no capacity or volume figures. The search snippet for the same URL says it connects with HubSpot and Salesforce, but that text was not in the fetched copy.

### 1.13 Kickscale: two pages
- **(a)** https://www.kickscale.com/post/sales-capacity-model-how-many-inbound-leads-can-one-sdr-handle. Author Gerald Zankl, founder and CEO of Kickscale (a **vendor** of an AI sales coach). Dated "09.04.2024". It says an SDR "can process about 15 new Marketing Qualified Leads per day" and does 10–30 manual activities an hour. **No study, data or sample is cited.** The figure assumes leads are already verified by marketing and are in the CRM.
- **(b)** https://www.kickscale.com/amp/inbound-capacity-planning-for-sdr-teams (the non-AMP URL returned only the blog index). No author named; updated 17 February 2023. It says every inbound SDR can handle "between 50-100 leads" a week, with an absolute maximum of 100. It also says "every number above 60 leads per week" lowers quality, and uses 60 a week (12 a day) as its realistic case, at about 38 hours of work. **No study cited.** It is the author's own model, with assumptions such as a 20% response rate.

### 1.14 Extra source found: Crunchbase, "SDR Metrics And KPIs"
- **URL:** https://about.crunchbase.com/blog/sdr-metrics-and-kpis-what-to-expect-from-your-sales-development-team
- **Publisher:** Crunchbase, a data **vendor**. Author Jaclyn Robinson, with contributor Catarina Hoch (VP Marketing, Operatix, an outsourced-SDR agency). Last updated 2 December 2025.
- **Content.** Each inbound rep "should be able to handle about 15 leads per day", so about **300 a month**. High-intent leads (demo requests, meeting inquiries) convert at **75–80%**, stage not defined. Low-intent leads (ebooks, webinars, whitepapers) convert at **5–10% from lead to meeting**.
- **Limits:** **no source** for these inbound figures. This page is the most likely origin of both the "15 a day / 300 a month" pairing and the "5–10% versus 75–80%" claim in the draft.

### 1.15 Extra source found: Drift sunset (primary press release)
- **URL:** https://www.businesswire.com/news/home/20260306534285/en/ (Clari + Salesloft press release, March 2026)
- **Content.** Clari + Salesloft announced "the gradual sunset of its Drift conversational marketing solution" and will refer existing Drift clients to 1mind as the successor. ZoomInfo's Drift vs Qualified page (https://pipeline.zoominfo.com/sales/drift-vs-qualified) adds that Salesloft is **no longer issuing new Drift contracts**. That second point comes from a vendor and was not seen in the press-release snippet.

---

## 2. Claim-by-claim verdicts for ICP_DRAFT.md

| # | Draft claim (section) | Verdict | What the sources say |
|---|---|---|---|
| 1 | An SDR processes about 15 new MQLs a day, and Kickscale cites no study (2.2, 6) | **CONFIRMED** | Kickscale (a) says this and cites nothing. Crunchbase says the same, also unsourced. Two practitioner opinions and no study. |
| 2 | That is about 300 a month (2.2, 6) | **CONFIRMED** | Crunchbase states 300 a month. Kickscale (a) does not, but 15 × 20 working days gives it. |
| 3 | 50 to 100 leads a week per SDR, with quality falling above about 60 (2.2) | **CONFIRMED** (source now identified) | Kickscale (b), 2023, the author's own model, no data. Note that 60 a week (12 a day) is lower than Kickscale (a)'s 15 a day (75 a week). Kickscale's own two pages imply roughly **240 to 300 leads a month per inbound SDR**. |
| 4 | A routing vendor says that at 30 or more leads a day manual oversight is unrealistic (2.2) | **CORRECTED** | ZoomInfo uses "30 leads a day" only as a hypothetical to show 2.5 hours a day of manual lookups. It does not call manual oversight unrealistic and sets no threshold. Other vendor pages put the breaking point at "50+ inbound leads per day" (Rework, seen in a search snippet only, not opened). No study. |
| 5 | Conversion is 5 to 10% for ebook or webinar leads and 75 to 80% for demo requests (2.2) | **CORRECTED** | The source is Crunchbase/Operatix, which cites nothing. The 5–10% is **lead to meeting**. The stage for the 75–80% is not defined (probably meeting). Neither figure is opportunity or closed-won. |
| 6 | MQL to SQL medians are 13 to 15% in some sources and 30 to 40% in others, mainly because MQL definitions differ (2.3) | **CORRECTED** | Most are **averages, not medians**. The 13% traces to First Page Sage's client data from 2019 to 2025, as at least three blogs report; I could not open First Page Sage itself. The 39–40% (Powered by Search) has no methodology and matches First Page Sage's channel data. So the two numbers are probably **the same agency's data cut two ways**: across all industries, and B2B SaaS by channel. Channel alone moves the rate from 26% (PPC) to 51% (SEO). Flighted's unsourced 18–22% sits between them. The claim, on one blog, that HubSpot's State of Marketing gives 13% is **not on HubSpot's own page**. |
| 7 | The best-known source page returned a 403 (2.3, 8) | **CORRECTED** | The `/learn/` URL opened. It has numbers but no methodology (1.1). |
| 8 | No usable monthly inbound-volume benchmark by company size (2.3) | **CONFIRMED** | Still none found. The nearest are response time by size (Visionary, agency clients) and meeting rate and disqualification rate by size (RevenueHero, from more than a million of its customers' form fills; SMB 63.2%/21.8%, mid-market 61.2%/28.1%, enterprise 70.1%/71.2%; volume not given). An oft-repeated "1,877 leads a month on average" figure is not broken down by size and its origin (DemandSage) was not traced. |
| 9 | Drift serves mid-market and enterprise with established SDR teams and deals above about $20,000 (2.5, 3.1) | **UNSUPPORTED** for the $20,000 figure | Not in Abmatic, either ZoomInfo page, Autobound or G2. Supported in part: G2 reviewers are 51.7% mid-market, and ZoomInfo says "Mid-market B2B". **More important:** Drift is **being sunset** (1.15), so the draft should not present it as a live competitor. |
| 10 | Pricing in this class runs from thousands of dollars a month into six figures a year (2.5) | **CONFIRMED** (vendor-reported) | G2 lists Drift from $2,500/month ($30K a year). Abmatic, a competitor with no source, gives Qualified $3K–$20K+/month, which is $36K to over $240K a year. Qualified publishes no prices. |
| 11 | A large low-end field of chatbot builders pitches "qualify and sync to any CRM" (2.5) | **CORRECTED** | The phrase was not found. Wonderchat says it "integrates with any helpdesk and CRM system", has a free plan, and another of its pages says "Starts at $0.02/message". The fetched Voiceflow page shows help-desk and contact-centre logos, not CRMs. The point holds in spirit for Wonderchat only. |
| 12 | Native two-way CRM sync is ranked first among evaluation criteria (2.4) | **CORRECTED** | LeadHaste ranks nothing and warns against stopping at "two-way". ZoomInfo lists native two-way sync **6th of 7**, after matching and dedup. |
| 13 | Evaluate exceptions more than happy paths (2.4) | **CONFIRMED** | LeadHaste. |
| 14 | Keep qualification separate from routing, because the buyer defines "qualified" (2.4) | **CONFIRMED** | LeadHaste. |
| 15 | API connectors add latency and a maintenance job RevOps owns (1, item 3) | **UNSUPPORTED** | Not in LeadHaste or any page opened. It is a reasonable hypothesis but has no source. |
| 16 | The category language has moved to "AI SDR agent" (2.5) | **CONFIRMED** (better source now available) | G2 has an "AI SDRs" category (485 products, November 2026) with Qualified as Leader. Gartner published "Innovation Insight: AI SDR Agents for Inbound and Outbound Sales Communication" (25 February 2025; abstract only, paywalled). |
| 17 | Workato's attribution to HBR is an error; the study I opened is not HBR's (2.1) | **CONFIRMED but incomplete** | The 2007 MIT/InsideSales figures (100x, 21x, 15,000 leads, 100,000 calls) are not HBR's. **But an HBR article by the same lead author does exist** (section 3). It reports different findings: about 7x and about 60x for contact within the hour. A "400% at 5 versus 10 minutes" figure appears in neither source as summarised. |

**Totals:** 17 claims checked. **9 confirmed, 6 corrected, 2 unsupported.** Plus one new finding that changes the competitive picture (Drift sunset).

Not re-checked in this pass (opened by the earlier session, not on this list): the MIT/InsideSales PDF, Workato, Qualified's home page, RevOps Co-op and Rework.

---

## 3. The HBR lead: "The Short Life of Online Sales Leads" (2011)

- **It exists.** BYU ScholarsArchive lists Oldroyd, McElheran and Elkington, *Harvard Business Review*, volume 89, issue 3, page 28, 2011, marked as a peer-reviewed article. Affiliations: Oldroyd at Brigham Young University, McElheran at Harvard Business School, and Elkington at Inside Sales.
- **Opened:** the BYU record only. hbr.org and ResearchGate were refused by the allowlist, and hbr.org and the Internet Archive were refused by the proxy (403). The content below comes from **secondary sources that agree with each other**, including a 2011 blog that quotes the article directly.
- **What it reports, per those sources:**
  1. An **audit of 2,241 US companies**, each sent a web test lead. 37% responded within an hour, 16% within 1 to 24 hours, 24% after more than 24 hours, and **23% never responded**. The average response, among firms that replied within 30 days, was **42 hours**.
  2. A **separate study of 1.25 million leads received by 42 US companies (29 B2C, 13 B2B)**. Firms that tried to contact a lead within an hour were nearly **7 times** as likely to qualify it as firms that tried an hour later, and over **60 times** as likely as firms that waited 24 hours or more. "Qualify" meant a meaningful conversation with a key decision-maker.
- **Is it the origin of "2,241 companies"? Yes.** Every source traces it to this audit. Two common errors to avoid: saying the 1.25 million leads came from the 2,241 companies (they came from a separate set of 42), and pinning the 100x/21x five-minute multipliers on HBR (those are the 2007 study's).
- **Independence:** partial. The lead author was an academic and the article is listed as peer-reviewed, but the third author ran InsideSales, a vendor in this market. The data is 15 years old and covers B2C as well as B2B.

---

## 4. Independent evidence found

| Source | Independent? | Useful for |
|---|---|---|
| HBR 2011 (section 3) | Partly (vendor co-author) | Slow response is common and long-standing. The within-the-hour effect. |
| G2 category and compare pages (1.6, section 2 row 16) | Review site, not a vendor; vendor-funded placements | Category naming ("AI SDRs"). Reviewer company size: Qualified about 70% mid-market, Drift about 52%. |
| Gartner "Innovation Insight: AI SDR Agents" (Feb 2025) | Analyst | Shows the category is recognised. Only the abstract was readable. |
| HubSpot State of Marketing 2026 (blog.hubspot.com/marketing/inbound-marketing-data) | **Vendor survey** (1,500+ marketers) | Says nothing on MQL to SQL, response time or volume by size. Only self-reported lead volume and quality trends (for example, 93.8% say lead quality improved). Not useful for the ICP. |
| Winning by Design, "The Rise of AI SDRs" (May 2025) | Consultancy | Claims AI SDRs beat humans at inbound qualification but shows no evidence on the page. |

**Bottom line:** no independent study was found for **SDR capacity**, **inbound volume by company size**, or **MQL to SQL rates**. Every number on those points comes from a vendor, an agency or a consultancy, and most give no method.

---

## 5. Recommended changes to ICP_DRAFT.md (not made here)

1. **2.5 and 3.1: remove the Drift "$20,000" figure** and add that Drift is being sunset (Clari + Salesloft, March 2026; existing clients are referred to 1mind). Name Qualified (Piper), 1mind, Salesforce Agentforce SDR and HubSpot's agents as the live comparisons. The $15K ACV placeholder then rests only on Rework (a neighbouring category).
2. **2.2: replace "a routing vendor's claim that at 30 or more leads a day manual oversight is unrealistic"** with what ZoomInfo actually says: 30 leads a day at 5 minutes each is 2.5 hours a day of lookups. Label it a worked example, not a threshold.
3. **2.2: give the 5–10% and 75–80% figures their source and stage:** Crunchbase/Operatix, **lead to meeting**, no cited data.
4. **2.2 and 6: cite both Kickscale pages** and give per-SDR capacity as a range of about **240 to 300 leads a month** (60 to 75 a week), practitioner opinion only. Part 6's arithmetic then becomes: 150 a month is about half to two thirds of one rep, and 250 is about 0.8 to 1.0 rep.
5. **2.3: rewrite the MQL to SQL paragraph.** Call them averages, not medians. Name First Page Sage as the probable source of both the 13% and the 39–51%. Say the gap is mostly scope (cross-industry versus B2B SaaS by channel), with definitions secondary. Drop any HubSpot attribution for 13%. Mark the 403 note as resolved.
6. **2.4: correct "native two-way CRM sync ranked first"** (no source ranks it first; ZoomInfo lists it 6th of 7). Keep "exceptions over happy paths" and "keep qualification separate from routing", now confirmed from LeadHaste.
7. **Part 1, item 3: mark "API connectors add latency and maintenance"** as a hypothesis with no source.
8. **2.5: soften "qualify and sync to any CRM"** to Wonderchat's actual wording ("integrates with any helpdesk and CRM system") and drop Voiceflow from that point.
9. **2.1: add the HBR 2011 article** as a source and change "treat as errors" to: HBR did publish related findings (2,241-company audit, 42-hour average, about 7x within the hour), but not the 100x/21x or 400% figures.
10. **Add to 2.3 or Part 6:** Visionary's response-time-by-company-size table (agency clients) and RevenueHero's meeting and disqualification rates by size (vendor), both labelled. They are the closest size-segmented data, though neither gives volume.
11. **Part 8:** move every source above from "search summaries only" to "opened", with its publisher type. Add Crunchbase, Kickscale (b), the Business Wire release, BYU ScholarsArchive and the G2 AI SDRs category.
