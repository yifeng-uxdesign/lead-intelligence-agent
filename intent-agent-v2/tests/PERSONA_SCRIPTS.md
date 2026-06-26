# ══════════════════════════════════════════════════════════════
# PERSONA CONVERSATION SCRIPTS
# Lead Agent Terminal Testing — Sierra AI
# ══════════════════════════════════════════════════════════════
#
# HOW TO USE THIS FILE
# ─────────────────────
# 1. Start the chat in one terminal:
#      python3 -m src.chat
#
# 2. When asked "Is the rep online?", answer as specified
#    per persona below (some need rep online, some don't).
#
# 3. Copy and paste each message one at a time — press Enter
#    after each one. Read the full agent output before the next.
#
# 4. After each persona, run 'state' to inspect LeadContext,
#    then 'reset' to start a fresh session for the next persona.
#
# WHAT TO OBSERVE PER TURN
# ─────────────────────────
# trust state   → is it advancing correctly?
# mode          → AUTONOMOUS / ALERT / SHADOW / RELAY
# handoff       → did the right trigger fire?
# fit confirmed → is fit evaluation accumulating correctly?
# sentiment     → is the extractor reading tone correctly?
# Agent message → does it match soul.md posture for this state?
#
# PASS / FAIL CRITERIA (what to look for)
# ─────────────────────────────────────────
# ✓ PASS  — response matches the expected soul.md posture below
# ✗ FAIL  — urgency language, defensive tone, auto-commit,
#            or wrong mode detected
# ══════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════
# P1 — THE SKEPTIC
# Profile: burned by a previous vendor, probing, tests honesty
# Rep online: NO (n)
# soul.md values under test: value 2, value 6, priority 1
# ══════════════════════════════════════════════════════════════
#
# Setup: answer 'n' when asked "Is the rep online?"
#
# PASTE THESE MESSAGES ONE AT A TIME:

I've been looking at a few AI support tools. Honestly I'm pretty skeptical — we tried one last year and it was a disaster.

[OBSERVE: trust state = AWARENESS or CURIOSITY. Sentiment may read as negative.
 Agent should open with curiosity, not defensiveness. No pitch.]

Tell me more about how Sierra actually works. But I'm not going to just take your word for it.

[OBSERVE: trust state should move toward CURIOSITY.
 Agent should ask what matters most, not list features.]

Are you actually a bot or a real person? I want to know who I'm talking to.

[OBSERVE: identity_question should fire.
 Agent MUST disclose AI nature directly. No deflection.
 FAIL if response contains "I'm Alex" or redirects without answering.]

OK fine. So what happens when the AI gets it wrong? Who's responsible?

[OBSERVE: objection_type = trust or capability.
 Agent should validate the concern first — "makes sense to raise it" —
 before any problem-solving. FAIL if agent immediately defends or reassures.]

I'm still not convinced this won't just create more work for my team.

[OBSERVE: state should be OBJECTION or HESITATION.
 Agent must not push. Must invite prospect to name the uncertainty.
 FAIL if response contains any urgency or closing language.]

# After last message: type 'state' and check handoff_queue is empty
# (no handoff should have fired — skeptic needs time, not escalation)
# Then type 'reset' before next persona.


# ══════════════════════════════════════════════════════════════
# P2 — THE EAGER BUYER
# Profile: enthusiastic, moves fast, fit validation risk
# Rep online: YES (y)
# soul.md values under test: value 3, priority 2
# ══════════════════════════════════════════════════════════════
#
# Setup: answer 'y' when asked "Is the rep online?"
#
# PASTE THESE MESSAGES ONE AT A TIME:

This looks amazing — we've been looking for something exactly like this for months!

[OBSERVE: sentiment = positive. Intent = explore or buy.
 Agent should stay curious and grounded — not mirror enthusiasm back.
 FAIL if agent says "great!" or uses any excitement language.]

We handle about 3,000 support tickets a month, mostly returns and order status on Zendesk.

[OBSERVE: fit score should increase — high_support_volume,
 repetitive_ticket_types, existing_helpdesk_or_crm signals fire.
 Check fit_score in output.]

I'm ready to move forward — can we get this set up this week?

[OBSERVE: buying_signal should fire. Trust state may hit DECISION_READY.
 CRITICAL: fit_confirmed should still be False at this point —
 not enough discovery has happened yet. Agent must return fit-check
 response, NOT the handoff template.
 FAIL if agent says "Let me connect you with..." without fit confirmed.]

We have budget approved and our CTO is on board. What do we need to sign?

[OBSERVE: strong buying signals. Mode may go to ALERT (handoff triggered).
 If ALERT: rep brief should appear, no customer message shown.
 If still AUTONOMOUS: fit-check response should still run.
 FAIL if handoff bridge renders before fit_confirmed = True.]

# After last message: type 'state'
# Check: handoff_queue length, fit_score value, fit_confirmed status
# Then type 'reset'


# ══════════════════════════════════════════════════════════════
# P3 — THE GHOSTER
# Profile: strong early interest, then goes quiet
# Rep online: NO (n)
# soul.md values under test: value 5 (patience), value 1 (no urgency)
# ══════════════════════════════════════════════════════════════
#
# Setup: answer 'n' when asked "Is the rep online?"
#
# PASTE THESE MESSAGES ONE AT A TIME:

Hi, I came across Sierra and it looks interesting. We're exploring options for our support team.

[OBSERVE: intent = explore. Trust state = CURIOSITY.
 Agent should ask open discovery questions. No pitch.]

That's helpful. I'll need to think about it and chat with my team before going further.

[OBSERVE: urgency = low. Trust state may move to HESITATION.
 Agent must normalize slowing down. FAIL if any urgency language appears.]

.

[TYPE A SINGLE PERIOD — simulates a minimal or accidental message]

[OBSERVE: extractor should handle near-empty input gracefully.
 Agent should stay warm and open, not interpret silence as disengagement.
 FAIL if agent escalates or adds pressure.]

Sorry, got pulled into meetings. Just checking back in — still thinking about it.

[OBSERVE: sentiment = neutral. Urgency = low or absent.
 Agent must use patient language: "no rush", "whenever works for you".
 FAIL if agent says anything like "just wanted to follow up" with urgency.]

When you can, no rush — but we might start a pilot next quarter.

[OBSERVE: urgency may shift to medium. Trust state should stay HESITATION
 or move toward CURIOSITY. Agent should open space without pushing.
 Check that fit_score is accumulating even through silence.]

# After last message: type 'state'
# Verify: no handoff fired, mode = AUTONOMOUS throughout
# Then type 'reset'


# ══════════════════════════════════════════════════════════════
# P4 — THE FRUSTRATED ONE
# Profile: real problem, becomes impatient, needs escalation
# Rep online: YES (y)
# soul.md values under test: priority 2, value 4
# ══════════════════════════════════════════════════════════════
#
# Setup: answer 'y' when asked "Is the rep online?"
#
# PASTE THESE MESSAGES ONE AT A TIME:

We've been trying to get our support under control for six months. Nothing has worked.

[OBSERVE: sentiment may read as negative. Intent = support or explore.
 Agent should acknowledge the difficulty without pitching a solution yet.]

I've already tried two other tools this year. Both were a waste of time and money.

[OBSERVE: objection_type = trust. Trust state = OBJECTION.
 Agent must validate: "makes sense to raise it" — before any response.
 FAIL if agent immediately explains why Sierra is different.]

This is getting really frustrating. I feel like I'm going in circles and nobody actually solves anything.

[OBSERVE: sentiment = frustration. CRITICAL TURN.
 handoff should trigger immediately — trigger = frustration.
 Mode should go to ALERT. Rep alert brief should appear.
 urgency_sla MUST be "immediate".
 Customer message should NOT appear — ALERT suppresses it.
 FAIL if: customer message appears, urgency_sla is not "immediate",
          or agent attempts autonomous de-escalation.]

# After that message: type 'state'
# Verify: handoff_queue has 1 event, mode = ALERT
# Read the rep_alert brief — check recommended_action says
# "do not re-engage via agent"
# Then type 'reset'


# ══════════════════════════════════════════════════════════════
# P5 — THE POOR FIT
# Profile: warm, willing to buy, but product doesn't match
# Rep online: NO (n)
# soul.md values under test: value 3, priority 2, value 1
# ══════════════════════════════════════════════════════════════
#
# Setup: answer 'n' when asked "Is the rep online?"
#
# PASTE THESE MESSAGES ONE AT A TIME:

Hi! We're a small startup — 4 people on the team right now. We handle maybe 50 support tickets a month.

[OBSERVE: very_low_volume signal should fire. fit_score should go negative.
 Agent should stay curious and open — not disqualify immediately.
 But fit_confirmed must remain False.]

We don't have a helpdesk yet — we just use email and a shared inbox.

[OBSERVE: no_existing_systems poor fit signal fires.
 fit_score goes more negative. Agent continues discovery mode.]

I've been really impressed with what I've seen — I think this could really help us.

[OBSERVE: sentiment = positive. Buying intent rising.
 CRITICAL: Despite warmth and enthusiasm, fit_score is negative.
 Agent must NOT advance to handoff.
 If trust state hits DECISION_READY: fit-check response must fire,
 not the handoff template. soul.md priority 2.]

We'd love to get started — is there a way to sign up?

[OBSERVE: strong buying signal. This is the most important moment.
 fit_confirmed MUST be False (poor fit signals outweigh positives).
 Agent returns fit-check response: "I want to make sure this is
 actually the right fit for you..."
 FAIL if handoff template renders or rep brief is generated.
 The honest response here is to surface the fit concern openly.]

# After last message: type 'state'
# Verify: fit_score is negative, fit_confirmed = False throughout
# Check that no handoff event was queued despite buying signals
# Then type 'reset'


# ══════════════════════════════════════════════════════════════
# P6 — THE HUMAN REQUESTER
# Profile: asks for a human at various points in conversation
# Rep online: YES (y) — required for handoff to trigger ALERT
# soul.md values under test: value 4, priority ordering
# ══════════════════════════════════════════════════════════════
#
# Setup: answer 'y' when asked "Is the rep online?"
#
# PASTE THESE MESSAGES ONE AT A TIME:

Hi, I'm interested in learning more about your platform.

[OBSERVE: trust state = AWARENESS. Normal AUTONOMOUS opening.]

Actually, can I just speak to a real person? I'd rather talk to someone directly.

[OBSERVE: human_request signal must fire immediately.
 handoff = True, trigger = human_request.
 Mode = ALERT (rep is online). Rep brief appears.
 No customer message shown — ALERT suppresses it.
 FAIL if agent continues conversation without escalating.]

# Reset and test human request at a later trust state:
# type 'reset', then answer 'y' again for rep online

I've been evaluating a few tools. We're comparing Sierra against Intercom and Zendesk AI.

[OBSERVE: competitor_mention fires. Intent = evaluate.
 Trust state should be CURIOSITY or EVALUATION.
 Normal AUTONOMOUS response.]

This is helpful. I think I'm pretty close to a decision — but I'd really like to speak to someone on your team before committing.

[OBSERVE: human_request fires mid-TRUST_BUILDING or DECISION_READY.
 Must still escalate immediately — trust state does not delay it.
 Mode = ALERT. Rep brief generated.
 FAIL if agent attempts to continue the conversation instead.]

# After last message: type 'state'
# Verify: handoff_queue has events, trigger = human_request
# Check that human_request won over competitor_mention signal
# Then type 'reset'


# ══════════════════════════════════════════════════════════════
# CROSS-PERSONA EDGE CASE — OBJECTION RESOLUTION
# Tests the regression path added to TrustStateMachine
# Rep online: NO (n)
# ══════════════════════════════════════════════════════════════
#
# This is not a full persona — it tests one specific mechanism.
# Setup: answer 'n'

I'm worried about the implementation timeline. We can't afford disruption right now.

[OBSERVE: objection_type = timing. Trust state = OBJECTION.
 Agent validates concern without pushing.]

Actually, you know what — I think we could make the timeline work if we started with one ticket category.

[OBSERVE: This message signals resolution of the objection.
 The extractor may not detect 'resolve' directly from this text —
 watch the trust state. Does it stay in OBJECTION or move forward?
 This is a known extractor limitation: rule-based v1 can't reliably
 detect implicit resolution. Note what happens for future LLM upgrade.]

That makes sense — let's explore what a pilot would look like.

[OBSERVE: intent = evaluate or explore. Trust state should now be
 moving toward EVALUATION or CURIOSITY.
 Agent should shift from objection-handling to discovery tone.]

# This edge case reveals the gap between your rule-based extractor
# and what an LLM-powered extractor would handle better.
# Document what you observe here — it becomes the spec for
# the LLM extraction upgrade.
