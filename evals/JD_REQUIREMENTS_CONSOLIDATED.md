# Conversation-design job requirements, consolidated (living document)

Based on the three postings you pasted so far: **Genesys** (Staff UX Designer, Conversational AI), **1mind** (AI Conversation Designer), **Morgan Stanley** (Conversational AI Specialist, Vice President). Add rows and columns as you send more. No plan changes are made here, as you asked.

Labels: **from the JD** = stated in the pasted text; **implied** = not stated but follows from other requirements (my inference); **from the project** = cited file. Counts are out of the postings read so far, so they will shift. The postings differ in seniority and function (a UX leadership role, a prompt-and-agent-systems role, and a bank's GenAI evaluation and solutioning role), so a requirement common to all three is a strong signal.

## 1. Requirement themes across the three postings

Cell key: **E** explicit in the posting, **I** implied, **–** not present.

| # | Requirement theme | Genesys | 1mind | Morgan Stanley | Count | Evidence in the postings |
|---|---|---|---|---|---|---|
| 1 | **Evaluation and evidence-driven iteration**: diagnose from transcripts and real interactions, define quality methods, prove a fix worked | E | E | E | **3** | G: "conversation analysis, experimentation … production interaction data". M: "diagnosing problems from transcripts and explaining how you knew a fix worked". MS: "data driven methodologies for testing and evaluating", human evaluation and LLM-as-a-judge, F1, RAGAS, "human feedback analysis" |
| 2 | **Trust, safety, governance, risk**: responsible AI, compliance, no unsafe or ungrounded answers | E | E | E | **3** | G: trust, policies, control. M: "compliance", "decline an unsafe action". MS: governance and control, bias, factual accuracy, risk management |
| 3 | **Prompt design and context management for LLMs** | I | E | E | **3** (1 implied) | M: "optimal prompts and context management", API-level command. MS: "context-aware prompts", prompt engineering for GPT/Claude/Gemini. G: understanding of LLM implications for the experience |
| 4 | **Knowledge grounding and factual accuracy** (RAG, knowledge bases) | I | E | E | **3** (1 implied) | M: "RAG knowledge-base creation". MS: access to "knowledge, data and workflows", factual accuracy. G: context, tools |
| 5 | **Language and conversation craft**: tone, naturalness, recovery, hearing when something sounds scripted | E | E | E | **3** | G: understanding, recovery, tone, naturalness. M: "hear when a response sounds scripted, off-tone, or wrong". MS: coherence, user satisfaction |
| 6 | **Cross-functional collaboration and stakeholder alignment** | E | I | E | **3** (1 implied) | G: align design, product, engineering, data science "without formal authority". MS: tech partners, business owners, vendors. M: "teach others", cross-company enablement |
| 7 | **Documentation, frameworks and enabling others** | E | E | E | **3** | G: "reusable principles and frameworks", mentorship. M: "document your work and teach others". MS: "education on AI technologies to other departments" |
| 8 | **Human handoff, escalation and routing logic** | E | E | I | **2** (1 implied) | G: "human handoffs, context, tools, policies". M: routing: "answer directly … ask a clarifying question … use a tool, escalate to a human, or decline". MS: workflows, risk controls |
| 9 | **Prototyping and technical fluency** (code, APIs, console) | I | E | I | **1 explicit**, 2 implied | M: "light code (for example Python)", APIs, prototypes. G: prototyping methods, partner with engineers. MS: "integrates with technical infrastructure" |
| 10 | **Agentic and multi-agent design** (subagents, contracts, tools) | E | E | I | **2** (1 implied) | G: agentic systems. M: subagents, contracts (inputs, structured outputs, confidence, evidence, latency, failure handling). MS: automation tools |
| 11 | **Metrics, KPIs and performance monitoring** | I | – | E | **1 explicit**, 1 implied | MS: "track project performance metrics and KPIs". G: quantitative research |
| 12 | **User and customer research** | E | I | I | **1 explicit** | G: "lead research and discovery". M: "reviewing feedback". MS: user satisfaction |
| 13 | **Voice and multimodal interaction** | E | E | – | **2** | G: turn-taking, latency, interruption, pronunciation. M: "voice", multi-media prompting |
| 14 | **Program and project management, risk mitigation** | I | – | E | **1 explicit** | MS: manage multiple projects, mitigate risks, track delivery |
| 15 | **Seniority and scope** | E | E | I | n/a | G: 8+ years, Staff. M: 3–5 years. MS: VP title, years not stated in the pasted text |

## 2. Priority order (proposed, from frequency and strength of wording)

**Core (all three postings):**
1. Evaluation and evidence-driven iteration (theme 1)
2. Trust, safety, governance, risk (theme 2)
3. Prompt and context design for LLMs (theme 3)
4. Knowledge grounding, factual accuracy (theme 4)
5. Language and conversation craft (theme 5)
6. Cross-functional collaboration (theme 6)
7. Documentation, frameworks, enabling others (theme 7)

**Strong secondary (two of three):** human handoff, escalation and routing logic (8); agentic and multi-agent design (10); voice and multimodal (13).

**Role-specific:** prototyping fluency (9, explicit in 1mind), user research (12, Genesys), KPIs (11) and program management (14, Morgan Stanley).

Why ranking 1 first: it is the only theme where all three postings use concrete method words (transcripts, experimentation, LLM-as-a-judge, RAGAS, F1, human evaluation). It is also the one your project can show most credibly today.

## 3. How the project covers each theme today (quick read, no plan change)
Ratings: **Strong / Partial / Gap**. "From the project" cites files.

| # | Theme | Today | What exists | What is missing |
|---|---|---|---|---|
| 1 | Evaluation | **Strong on method, Partial on coverage** | Config A runner, failure classification, invariants, held-out set, iteration log (`evals/REPORT_A.md`, `ITERATIONS.md`, `conformance/`) | No LLM-as-a-judge run (rubric `inputs/judge_rubric_v0.yaml` exists, not used in config A); no human-eval agreement yet (protocol drafted in `drafts/QUALIFICATION_CRITERIA.md`); no F1/RAGAS-style metric; data is scenario-based |
| 2 | Trust, safety, governance | **Strong** | `soul.md`, invariants, holding copy, delivery policy that fails closed, KB-first rule (`PLAN_BEHAVIOR_LAYER.md`) | Verified-claims list; validator not built |
| 3 | Prompt and context design | **Gap** | A design for where an LLM goes and the contracts (`drafts/LAYER_MAP.md`) | **No LLM and no prompts exist in the code** (`requirements.txt:17-21` comments only). This is the largest gap against two of three postings |
| 4 | Knowledge grounding | **Partial** | 15 draft knowledge entries and the known-unknowns table (`northstar/KNOWLEDGE_BASE.md`); retrieve-then-alert design | No retrieval code; entries unapproved; no RAG |
| 5 | Language craft | **Partial** | Northstar copy rules, word list, recovery and repair work, rubric dimensions (`northstar/CONVERSATION_DESIGN.md`, `EVALUATION_PLAN.md`) | Backend replies are generic templates; loop-breakers found by the eval |
| 6 | Collaboration | **Partial** | Open-question lists and decision logs written for PM/engineering/legal | Solo project; no outcomes to show |
| 7 | Documentation, frameworks | **Partial** | Audit, layer map, invariants, taxonomy, plans, visual map | Principles not yet distilled to one page |
| 8 | Handoff and routing | **Strong in design, Partial in code** | Three handoff types, trigger catalog, modes, delivery matrix | Relay and qualified handoff not built |
| 9 | Prototyping and technical fluency | **Strong** | Python adapter, runner, eval report, backend integration, widget, workspace stand-in | None for the postings read |
| 10 | Agentic design | **Partial** | Layer boundaries and contracts as design; rep/agent collaboration modes | No subagents; no structured agent contracts in code |
| 11 | KPIs | **Partial** | Metric definitions (`drafts/SUCCESS_METRICS.md`) | Not computed on outcome data |
| 12 | User research | **Gap** | Your manual test rounds (F1–F9) | No participants beyond the author |
| 13 | Voice | **Gap** | Turn-taking and pacing rules in the widget (text) | Nothing for voice |
| 14 | Program management | **Partial** | Backlog, ranked plan, iteration log | Scope is one person |

## 4. What this suggests (for the tailoring step, not a plan yet)
- **The project is strongest exactly where all three postings overlap most** (evaluation, trust and governance, handoff logic, framework documentation).
- **The most important missing piece is prompting.** Two of three postings ask for hands-on LLM prompting, context management and API fluency, and the code contains no LLM. A small, honest LLM component (for example LLM extraction behind the frozen labels, and phrasing behind a validator, both evaluated against the config A baseline) would address themes 3 and 4 and strengthen theme 1 (LLM-as-judge, comparison across configs). This is in tension with your goal of finishing the rules first; it is a decision for the tailoring step.
- **Second gap: real interaction data** (themes 1 and 12). A small role-play study with people other than the author would help all three postings.
- **Voice** matters for Genesys and 1mind only; treat it as a design extension, not a build.

## 5. Open questions before tailoring
- **R1.** More postings to come: which roles do you rank as primary (UX leadership like Genesys, prompt/agent systems like 1mind, evaluation-heavy like Morgan Stanley)? The priority order above shifts with that choice.
- **R2.** Is a small LLM prototype acceptable in the portfolio before the rules are "finished"? (Rules still own all decisions; the LLM interprets or phrases under a validator.)
- **R3.** Should the principles page (themes 7, 2, 5) be written before more JDs arrive, or after the consolidation is final?
- **R4.** For Morgan Stanley's evaluation emphasis, do you want the judge rubric and an LLM-as-judge run on the config A text as an early exhibit?
