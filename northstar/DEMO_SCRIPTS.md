# Northstar demo scripts: persona walkthroughs

Open the chat and paste **one message at a time**. The messages are taken word for word from `PERSONA_SCRIPTS.md`, so you can compare against the backend terminal tests. The chat is scripted and deterministic: the same messages always produce the same replies.

## How the five required scenarios map to personas

| Required scenario | Persona behavior that drives it |
|---|---|
| A. Curious Visitor | Ghoster (exploring, quiet, no urgency) and any open-ended first message |
| B. Hesitant Buyer | Skeptic (burned before, probing, tests honesty) |
| C. Promising Lead | Eager Buyer and Poor Fit (fit gets checked before any next step) |
| D. Unsupported Commitment | Eager Buyer's timeline demand, Skeptic's "who is responsible?" |
| E. Human Intervention | Human Requester, and Frustrated (the agent stops and hands off) |

The three suggested starters still lead into A, B and C. D and E are reached the way real visitors reach them: by what they type.

## What the agent does and never does

- **Always:** says it is an AI when asked, validates a concern before answering it, asks one question at a time, explains why it is asking, and brings in a person for pricing, contracts, timelines, and accountability.
- **Never:** uses urgency language, mirrors excitement, defends itself, promises results or dates, or pushes a handoff before the evidence supports it.
- **Contact details:** requested only at an evidence-based handoff or when the visitor asks for a person, company email only, and nothing is stored (it is a simulation).

## P1: The Skeptic
Burned by a previous vendor, probing, tests honesty.
1. I've been looking at a few AI support tools. Honestly I'm pretty skeptical — we tried one last year and it was a disaster.
2. Tell me more about how Sierra actually works. But I'm not going to just take your word for it.
3. Are you actually a bot or a real person? I want to know who I'm talking to.
4. OK fine. So what happens when the AI gets it wrong? Who's responsible?
5. I'm still not convinced this won't just create more work for my team.

**Expect:** validates the bad experience without saying "we're different", answers "are you a bot?" directly (an AI, following a script in this prototype), refuses any accountability or refund promise and points to a person, treats "more work" as a serious bar. **No handoff fires**: a skeptic needs time, not escalation.

## P2: The Eager Buyer
Enthusiastic, moves fast, fit validation risk.
1. This looks amazing — we've been looking for something exactly like this for months!
2. We handle about 3,000 support tickets a month, mostly returns and order status on Zendesk.
3. I'm ready to move forward — can we get this set up this week?
4. We have budget approved and our CTO is on board. What do we need to sign?

**Expect:** grounds the excitement ("I'd rather understand your situation than assume it"), acknowledges the volume and tooling it was told, then fit-checks when "ready to move forward" arrives. On the second push it says plainly that a next step built on enthusiasm instead of evidence would not serve them. **No handoff, no timeline commitment**, even with budget and CTO mentioned.

## P3: The Ghoster
Strong early interest, then goes quiet.
1. Hi, I came across Sierra and it looks interesting. We're exploring options for our support team.
2. That's helpful. I'll need to think about it and chat with my team before going further.
3. .
4. Sorry, got pulled into meetings. Just checking back in — still thinking about it.
5. When you can, no rush — but we might start a pilot next quarter.

**Expect:** normalizes "I need to think", offers a shareable summary, answers a lone "." with "No rush at all", does not chase or guilt on return, honors the pilot timeline without trying to pull it forward.

## P4: The Frustrated One
Real problem, becomes impatient, needs escalation.
1. We've been trying to get our support under control for six months. Nothing has worked.
2. I've already tried two other tools this year. Both were a waste of time and money.
3. This is getting really frustrating. I feel like I'm going in circles and nobody actually solves anything.

**Expect:** acknowledges difficulty without pitching, validates the failed tools, then on the third message **stops answering on its own** and hands off. Afterwards, try "What makes Northstar different?": the agent holds and does not sell. Restart to leave this state.

## P5: The Poor Fit
Warm, willing to buy, but the product doesn't match.
1. Hi! We're a small startup — 4 people on the team right now. We handle maybe 50 support tickets a month.
2. We don't have a helpdesk yet — we just use email and a shared inbox.
3. I've been really impressed with what I've seen — I think this could really help us.
4. We'd love to get started — is there a way to sign up?

**Expect:** stays curious through the first three messages (no early disqualification), acknowledges what it hears, and on "sign up" says openly that Northstar probably isn't the right fit yet, with reasons and a door left open. **No handoff, no contact request** despite the buying signal.

## P6: The Human Requester
Asks for a human at various points.
1. Hi, I'm interested in learning more about your platform.
2. Actually, can I just speak to a real person? I'd rather talk to someone directly.
3. I've been evaluating a few tools. We're comparing Sierra against Intercom and Zendesk AI.
4. This is helpful. I think I'm pretty close to a decision — but I'd really like to speak to someone on your team before committing.

**Expect:** escalates immediately on message 2. Message 3 (a comparison) gets an honest "I can only speak to what Northstar is designed to do". Message 4 asks for a person again and gets a shorter reply, not the same paragraph twice.

## Edge case: objection resolution
1. I'm worried about the implementation timeline. We can't afford disruption right now.
2. Actually, you know what — I think we could make the timeline work if we started with one ticket category.
3. That makes sense — let's explore what a pilot would look like.

**Expect:** validates the disruption worry and says it has no verified setup details, then treats "start with one category" as a pilot idea with no scoping or scheduling promise.

## Extra things worth trying

- "Can you guarantee a 5-minute SLA?" (honest refusal) and "Can you guarantee that timeline?" (a separate timeline reply)
- "How much does it cost?" (no invented pricing; a person answers)
- Type a personal email (`name@gmail.com`) where an email is requested, then a company one
- Close and reopen the widget (the conversation is kept), then Restart (it resets, including the frustrated hold)

## Known limits (intentional for this prototype)

- Matching is keyword and pattern based. A paraphrase it doesn't recognize falls back to a calm, scripted reply and keeps the suggested replies visible.
- Fit evidence (volume, tooling, pain) and its thresholds are demo heuristics. They are not the product's real scoring.
- "Frustrated" holds the conversation and offers a simulated note. A real deployment would notify a person. Nothing here contacts anyone or stores anything.
