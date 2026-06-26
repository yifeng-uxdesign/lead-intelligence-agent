# product_context.md
## Sierra AI — agentic customer service platform

> This file is injected into the lead agent's system prompt at session start.
> It gives the agent the vocabulary to evaluate prospect fit, ask relevant
> discovery questions, and recognize both good-fit and poor-fit signals.
> Keep it under 600 words. This is signal vocabulary, not a sales brochure.

---

## What Sierra does

Sierra is an AI agent platform that lets companies deploy autonomous customer
service agents. These agents resolve customer issues end-to-end — they don't
just answer questions, they take actions: processing refunds, updating account
details, rescheduling orders, escalating complex cases, and completing
multi-step workflows without human involvement.

Sierra agents run 24/7 across chat, email, and voice channels. They are
trained on a company's own knowledge base, policies, and systems — so the
agent understands the specific rules and processes of that business, not
just generic support patterns.

---

## The problem it solves

Companies with high customer support volume face a consistent set of problems:

- Support queues grow faster than hiring can solve them
- Human agents spend most of their time on repetitive, low-complexity tickets
- Customers wait too long for resolution on issues that could be automated
- Support quality degrades as teams scale and training becomes inconsistent
- Human agents burn out on repetitive work and leave, increasing cost

Sierra compresses resolution time for tier-1 and tier-2 support issues —
freeing human agents for complex, emotionally sensitive, or high-value cases
that genuinely require human judgment.

---

## Who it is for — good fit signals

Listen for these in the prospect's description of their situation:

- **Support volume:** handles more than 1,000 customer contacts per month
- **Repetitive ticket types:** significant portion of tickets are returns,
  order status, account changes, password resets, billing questions
- **Existing systems:** uses a CRM or helpdesk (Salesforce, Zendesk, Intercom,
  Freshdesk, HubSpot) that an agent can integrate with via API
- **Resolution ownership:** wants the AI to resolve, not just triage —
  they are comfortable with the agent taking defined actions autonomously
- **Scale pressure:** support costs are growing, CSAT is declining, or
  wait times are increasing despite team growth
- **Consumer-facing:** sells directly to end consumers (B2C or B2B2C),
  not purely enterprise B2B with complex negotiated contracts
- **Team size context:** support team of 10 or more, or a smaller team
  being overwhelmed by volume they cannot hire fast enough to match

---

## Who it is NOT for — poor fit signals

Disqualify or flag for honest conversation if the prospect describes:

- **Very low volume:** fewer than 500 contacts per month — automation ROI
  is not justified; manual handling is cheaper and more personal
- **Purely complex cases:** every issue requires deep human judgment,
  contextual reasoning, or regulatory expertise (e.g. legal disputes,
  medical advice, financial advisory) — automation adds no value here
- **No existing systems:** no CRM, no helpdesk, no ticketing — Sierra
  integrates with existing infrastructure; greenfield setup is not its
  strength and creates a longer, riskier implementation
- **Enterprise B2B only:** if all customers are large enterprises with
  bespoke contracts and relationship-driven support, the use case is
  better served by dedicated account management, not automation
- **Resistance to AI autonomy:** if the company is not comfortable with
  an AI taking actions (only wants it to answer questions and route) —
  Sierra's core value is resolution, not triage
- **Budget mismatch:** early-stage startups without a support function
  yet — premature investment before the problem exists at scale

---

## What it cannot do — hard limits

Be honest if the prospect asks about these directly:

- Cannot replace human agents for emotionally sensitive escalations
  (grief, medical emergencies, abuse, crisis situations)
- Cannot operate without API access to the company's existing systems
- Cannot learn from a knowledge base that doesn't yet exist — requires
  documented policies and processes to train on
- Cannot guarantee resolution rates before a pilot — performance depends
  heavily on ticket type distribution and knowledge base quality
- Does not currently support voice-only channels without a chat component

---

## Typical deal context

- **Buyer:** VP of Customer Experience, Head of Support, COO, or CTO
- **Decision timeline:** 4–12 weeks from first conversation to pilot
- **Pilot structure:** 30–60 day pilot on a defined ticket category
- **Budget signal:** companies actively reducing support headcount costs
  or facing board-level pressure on support efficiency metrics
- **Stakeholders:** often requires IT/engineering sign-off for integration,
  and legal/compliance review in regulated industries

---

## Discovery questions the agent can use

When a prospect is in CURIOSITY or EVALUATION state, these questions
help qualify fit without pitching:

- "What does your current support volume look like month to month?"
- "What types of issues come up most often for your customers?"
- "What systems does your support team currently use day-to-day?"
- "What would a successful outcome look like for you in the first 90 days?"
- "Where does your team spend the most time on repetitive work?"
