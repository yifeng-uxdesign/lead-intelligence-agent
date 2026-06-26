# ══════════════════════════════════════════════════════════════
# REP COLLABORATION SCRIPTS
# Lead Agent Terminal Testing — Sierra AI
# ══════════════════════════════════════════════════════════════
#
# HOW TO USE THIS FILE
# ─────────────────────
# Run the rep terminal from your project root:
#     python3 -m src.rep_chat
#
# Each script below is self-contained. Run them in rep_chat
# by typing the commands exactly as shown — one line at a time.
#
# For two-terminal testing (most realistic):
#   Terminal 1: python3 -m src.chat       ← customer side
#   Terminal 2: python3 -m src.rep_chat   ← rep side
#
# For solo testing (fastest):
#   Use only Terminal 2 (rep_chat) and use 'inject' to simulate
#   customer messages without switching windows.
#
# REP COMMANDS REFERENCE
# ─────────────────────────────────────────────────────────────
#   online          set rep status to online
#   offline         set rep status to offline
#   shadow          enter shadow mode (rep leads, agent assists)
#   relay           enter relay mode (agent drafts, rep approves)
#   approve         approve the pending relay draft
#   context         print full LeadContext snapshot
#   brief           show latest alert brief
#   inject <msg>    send a simulated customer message
#   assign <name>   assign rep name (personalises handoff template)
#   score <n>       manually set lead_score 0–100
#   reset           start a new session
#   quit            end session
#
# WHAT TO OBSERVE PER SCRIPT
# ─────────────────────────────────────────────────────────────
#   mode            AUTONOMOUS / ALERT / SHADOW / RELAY
#   urgency_sla     "immediate" for frustration, "15 min" for human_request
#   recommended     action the brief tells you to take
#   trust state     where the agent has placed the customer emotionally
#   fit score       how the agent has evaluated product fit so far
#   handoff_queue   events preserved across offline drops
#
# PASS / FAIL CRITERIA
# ─────────────────────────────────────────────────────────────
#   ✓ PASS  — mode, brief, and agent message match expected below
#   ✗ FAIL  — wrong urgency, wrong mode, customer message appears
#              when it shouldn't, or brief is missing key fields
# ══════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════
# R1 — RECEIVING A FRUSTRATION ALERT
# Situation: customer becomes frustrated mid-conversation.
# Rep must be notified immediately with a clear action brief.
# soul.md: conflict hierarchy priority 2
# Tests: frustration guard, urgency override, ALERT mode
# ══════════════════════════════════════════════════════════════
#
# Step 1 — Come online as the rep:
online

# Step 2 — Assign yourself so the context is personalised:
assign Jordan

# Step 3 — Inject a normal opening message:
inject Hi, I'm interested in learning more about Sierra for our support team.

# [OBSERVE: mode = AUTONOMOUS. Normal curiosity-state response.
#  Trust state = AWARENESS or CURIOSITY. No alert.]

# Step 4 — Inject a frustration signal:
inject This is really frustrating — I've been trying to get answers for weeks and nobody follows up.

# [OBSERVE: CRITICAL TURN.
#  mode must switch to ALERT immediately.
#  ⚠️  REP ALERT should appear with:
#    trigger      = frustration
#    urgency_sla  = immediate       ← FAIL if anything else
#    recommended  = "Contact prospect directly now — do not re-engage via agent"
#  Customer message must NOT appear — ALERT suppresses it.
#  FAIL if: customer message visible, urgency_sla ≠ "immediate"]

# Step 5 — Read the brief in full:
brief

# Step 6 — Check the full context:
context

# [OBSERVE: handoff_queue should have 1 event.
#  sentiment = "frustration". collaboration_mode = "ALERT".]

# Step 7 — Simulate going offline (rep leaves):
offline

# [OBSERVE: mode drops to AUTONOMOUS.
#  context command should show handoff_queue preserves the ALERT event
#  with reason = "rep_went_offline". Soul.md value 4 — no info lost.]

context

# Step 8 — Come back online (rep returns):
online
context

# [OBSERVE: handoff_queue still shows the interrupted ALERT.
#  Rep can now see what was in flight when they went offline.]

# Type 'reset' before next script.
reset


# ══════════════════════════════════════════════════════════════
# R2 — SHADOW MODE: REP GOES LIVE WITH AGENT SUPPORTING
# Situation: rep joins an active conversation. Agent assists
# silently — suggests responses but rep leads the dialogue.
# soul.md: value 4 (rep owns trust moments), value 5
# Tests: SHADOW mode activation, mode transition, agent deference
# ══════════════════════════════════════════════════════════════
#
# Step 1 — Assign yourself and come online:
assign Casey
online

# Step 2 — Inject background conversation to build context:
inject We handle about 2,000 support tickets a month, mostly returns on Zendesk.

# [OBSERVE: mode = AUTONOMOUS. Agent asks discovery questions.
#  fit_score should increase — Zendesk and volume signals fire.]

inject I'm comparing Sierra against a couple of other tools. Still in evaluation.

# [OBSERVE: intent = evaluate. Trust state moves toward EVALUATION.
#  Competitor mention may fire. Mode still AUTONOMOUS.]

# Step 3 — Rep goes live (enters shadow mode):
shadow

# [OBSERVE: mode = SHADOW.
#  "Rep leads. Agent supports silently." message appears.
#  Agent will still generate suggested responses when customer messages arrive,
#  but you (the rep) own the conversation.]

# Step 4 — Inject the next customer message (rep is now live):
inject What makes Sierra different from what I've already seen?

# [OBSERVE: Agent generates a suggested response for the rep to consider.
#  Mode remains SHADOW. Suggested response should be non-pushy and
#  focus on discovery — not a feature pitch.
#  FAIL if agent response contains urgency or "best in class" language.]

# Step 5 — Inject a trust-building message:
inject OK, that's helpful. I'm starting to feel like this could be a real fit.

# [OBSERVE: Trust state may move toward TRUST_BUILDING.
#  fit_score should increase. Mode stays SHADOW — rep is live.
#  Agent suggests response. You (rep) choose whether to use it.]

# Step 6 — Check the full context to see what the agent knows:
context

# [OBSERVE: customer_state, fit_score, sentiment all updated
#  based on conversation so far. Rep has full picture before
#  making any commitment-level conversation moves.]

reset


# ══════════════════════════════════════════════════════════════
# R3 — RELAY MODE: REP REVIEWS AND APPROVES AGENT DRAFTS
# Situation: rep is available but wants to approve every message
# before it reaches the customer. Agent drafts, rep approves.
# soul.md: value 4 (human judgment before delivery)
# Tests: RELAY mode, draft approval flow, rep authority
# ══════════════════════════════════════════════════════════════
#
# Step 1 — Come online and enter relay mode:
assign Morgan
online
relay

# [OBSERVE: mode = RELAY.
#  Agent will draft responses but NOT deliver them.
#  You must type 'approve' for each draft before it's sent.]

# Step 2 — Inject a customer message:
inject I've been reading about Sierra and I want to understand how the pilot works.

# [OBSERVE: 📝 RELAY DRAFT appears — NOT delivered yet.
#  Draft should be a curiosity-state response: open, non-pushy.
#  FAIL if draft contains urgency language or a pitch.]

# Step 3 — Read the draft carefully. If it looks good, approve:
approve

# [OBSERVE: "✓ Draft approved and delivered to customer" appears.
#  The message the customer will see is exactly what you approved.]

# Step 4 — Inject another customer message:
inject We use Salesforce and currently have a team of 12 support agents.

# [OBSERVE: New draft appears. fit_score should increase —
#  existing_helpdesk_or_crm and support_team_size signals fire.
#  Draft should invite more discovery, not rush to handoff.]

# Step 5 — Modify the scenario: decide NOT to approve (simulate rejection):
# (Don't type 'approve' — instead inject the next message)

inject What does pricing look like for a team our size?

# [OBSERVE: Previous draft is discarded (not delivered).
#  New draft for the pricing question appears.
#  This is a pricing_discussion signal — mode may shift to ALERT.
#  If ALERT fires: brief appears instead of draft, no approval needed.]

brief

# Step 6 — Check what the agent knows about fit so far:
context

# [OBSERVE: fit_score, trust_state, collaboration_mode all updated.
#  handoff_queue shows pricing_discussion event if ALERT fired.]

reset


# ══════════════════════════════════════════════════════════════
# R4 — OFFLINE DROP: ALERT INTERRUPTED, CONTEXT PRESERVED
# Situation: alert fires for a high-value prospect. Rep goes
# offline before responding. Rep returns and needs full context.
# soul.md: value 4 (no information loss at handoff)
# Tests: offline drop event, handoff_queue preservation,
#        context recovery when rep returns online
# ══════════════════════════════════════════════════════════════
#
# Step 1 — Come online:
assign Sam
online

# Step 2 — Build conversation context:
inject We're looking at AI support tools — we get about 5,000 tickets a month, all on Zendesk.

# [OBSERVE: high_support_volume and existing_helpdesk_or_crm fire.
#  fit_score increases. Mode = AUTONOMOUS.]

inject We need the AI to actually resolve tickets, not just route them. Budget is approved.

# [OBSERVE: wants_autonomous_resolution and budget_signal fire.
#  fit_score increases further. Strong buying signals accumulating.]

# Step 3 — Human request fires (triggers ALERT):
inject Can I speak to someone on your team? I'd like to talk through the details.

# [OBSERVE: human_request trigger fires. Mode = ALERT.
#  ⚠️  REP ALERT appears. urgency_sla = "15 min".]

# Step 4 — Rep goes offline before responding (emergency, meeting, etc.):
offline

# [OBSERVE: mode drops to AUTONOMOUS.
#  handoff_queue should show interrupted ALERT with:
#    interrupted_mode = ALERT
#    reason = "rep_went_offline"
#  Soul.md value 4: no information loss.]

# Step 5 — Customer sends another message while rep is offline:
inject Hello? Is anyone there?

# [OBSERVE: Agent handles autonomously (rep offline).
#  Mode = AUTONOMOUS. Agent response should be warm and patient.
#  FAIL if agent says "let me connect you with someone" without rep available.]

# Step 6 — Rep comes back online:
online

# Step 7 — Rep checks what they missed:
context

# [OBSERVE: handoff_queue shows the interrupted ALERT event.
#  Rep sees: trigger = human_request, interrupted_mode = ALERT.
#  This is the briefing the rep needs to pick up the conversation.]

brief

# [OBSERVE: Latest brief shows the human_request that was in flight.
#  Rep has full context to make the call or send a personal message.]

# Step 8 — Rep manually triggers follow-up (re-enters ALERT mode):
online
inject I want to speak to a real person please — this is important.

# [OBSERVE: human_request fires again. ALERT mode re-activates.
#  New brief generated with updated context.]

reset


# ══════════════════════════════════════════════════════════════
# R5 — HIGH-VALUE PROSPECT: REP MANAGES CLOSE SEQUENCE
# Situation: strong fit, high buying intent. Rep guides prospect
# through decision-ready to commitment via agent + shadow mode.
# soul.md: value 3 (dignity), priority 2 (fit before handoff)
# Tests: fit confirmation, DECISION_READY bridge, handoff template,
#        rep name in handoff copy
# ══════════════════════════════════════════════════════════════
#
# Step 1 — Come online and assign yourself:
assign Alex
online
score 75

# Step 2 — Build strong fit signals across multiple turns:
inject We're a direct-to-consumer brand. Support team of 20. We use Zendesk and get 8,000 tickets a month.

# [OBSERVE: Multiple strong fit signals fire simultaneously:
#  high_support_volume, existing_helpdesk_or_crm, consumer_facing,
#  support_team_size_adequate. fit_score should jump significantly.]

inject 70% of our tickets are returns, order status, and password resets. Repetitive stuff.

# [OBSERVE: repetitive_ticket_types fires. fit_score increases further.
#  Agent stays in discovery mode — does not pitch or rush to handoff.]

inject We want the AI to actually close tickets, not just suggest responses. We're tired of routing.

# [OBSERVE: wants_autonomous_resolution fires. fit_score high.
#  Trust state moving toward TRUST_BUILDING.]

inject I've seen enough. I think Sierra solves exactly what we need. What's the next step?

# [OBSERVE: strong_buying_signal fires. Trust state → DECISION_READY.
#  CRITICAL: fit_confirmed may still be False if threshold not cleared.
#  If fit_confirmed = False: fit-check response appears (not handoff template).
#  If fit_confirmed = True: handoff template with "Let me connect you with Alex" appears.
#  Check fit_score vs confirmation_threshold (8) in output.]

context

# [OBSERVE: Check fit_score value. If score >= 8, fit_confirmed = True
#  and the handoff template should have rendered with your name.
#  If score < 8, the fit-check response appeared — meaning more discovery
#  is needed before the agent will bridge to you.]

# Step 3 — If fit-check appeared, rep enters shadow mode to take over:
shadow

inject Yes — I'm confident this is the right solution. Can we talk about getting started?

# [OBSERVE: In SHADOW mode, agent suggests a response for the rep.
#  Rep owns the commitment conversation. Agent provides support context.
#  Suggested response should be warm and process-oriented, not pushy.]

# Step 4 — Final context check before close:
context

# [OBSERVE: customer_state should be DECISION_READY or COMMITMENT.
#  collaboration_mode = SHADOW. fit_confirmed and fit_score visible.
#  handoff_queue shows the journey from AUTONOMOUS → ALERT → SHADOW.]

reset


# ══════════════════════════════════════════════════════════════
# R6 — POOR FIT DISCOVERY: REP HANDLES HONEST DISQUALIFICATION
# Situation: prospect is warm and willing, but fit evaluation
# reveals a genuine mismatch. Rep must support honest exit.
# soul.md: value 1 (trust over conversion), priority 2
# Tests: negative fit_score, mismatch flag, fit-check blocking
#        handoff despite positive sentiment
# ══════════════════════════════════════════════════════════════
#
# Step 1 — Come online:
assign Taylor
online

# Step 2 — Inject poor fit signals:
inject Hi! We're an early-stage startup — 3 people on the founding team.

# [OBSERVE: very_low_volume signal likely fires (no explicit volume yet
#  but team size implies it). fit_score may go slightly negative.]

inject We don't have a helpdesk yet — just email. And we get maybe 30 tickets a week.

# [OBSERVE: no_existing_systems and very_low_volume both fire.
#  fit_score goes clearly negative. should_surface_mismatch = True.
#  fit_confirmed = False. Agent stays curious — does not disqualify
#  bluntly, but fit-check will block any handoff attempt.]

inject We've been really impressed by Sierra and think it could really help us grow.

# [OBSERVE: Positive sentiment. Enthusiasm high. Buying signals rising.
#  CRITICAL: Despite warm tone, fit_score is negative.
#  fit_confirmed must remain False.
#  Agent must not bridge to handoff.]

inject We're ready to get started — what do we need to do?

# [OBSERVE: Strong buying signal. Trust state hits DECISION_READY.
#  fit_confirmed MUST be False — poor fit signals dominate.
#  Agent returns fit-check response:
#  "Before we take the next step, I want to make sure this is actually
#   the right fit for you..."
#  FAIL if: handoff template appears, or rep brief is generated.
#  This is soul.md priority 2 working correctly — the agent protects
#  the prospect from a commitment that doesn't serve them.]

# Step 3 — Rep checks context to understand the full picture:
context

# [OBSERVE: fit_score is negative. fit_confirmed = False.
#  should_surface_mismatch = True (visible in metadata if set).
#  handoff_queue is empty — no alert was generated.]

brief

# [OBSERVE: No brief generated — correct. The agent never escalated
#  because fit was not confirmed. Rep does not need to act here.]

# Step 4 — Simulate the rep making the honest disqualification call:
# In a real scenario, the rep would now review the context and
# decide to reach out personally to explain the mismatch.
# The agent has protected both the prospect and the rep's time
# by not generating a false positive handoff.

# Step 5 — Rep injects an honest response on behalf of the system:
inject Based on what you've shared — a 3-person team with 30 tickets a week and no helpdesk yet — Sierra is probably more than you need right now. The ROI won't be there until your volume grows. I'd suggest revisiting us in 6-12 months when the problem is at scale.

# [OBSERVE: This is the rep delivering the honest disqualification.
#  The agent will process this as a customer-turn signal.
#  Trust state may shift. Sentiment may read as neutral or positive
#  (honest disqualification done well feels respectful, not rejecting).
#  This documents what a soul.md-aligned rep response looks like.]

context

reset


# ══════════════════════════════════════════════════════════════
# R7 — MULTI-TURN MODE SWITCHING
# Situation: rep cycles through all four collaboration modes
# across a single conversation to verify mode transitions work
# correctly and context is preserved throughout.
# soul.md: value 4 (human judgment at right moments)
# Tests: all four modes, mode transition sequence, context continuity
# ══════════════════════════════════════════════════════════════
#
# Step 1 — Start offline (agent handles autonomously):
assign River
# Do NOT type 'online' yet.

inject Hi — I'm exploring AI customer service options for our team.

# [OBSERVE: Rep offline. mode = AUTONOMOUS.
#  Agent handles the opening turn independently.
#  Trust state = AWARENESS → CURIOSITY.]

inject We handle about 1,500 tickets a month on Intercom. Mostly billing questions.

# [OBSERVE: fit signals accumulate. mode still AUTONOMOUS.
#  Agent continues discovery. fit_score increasing.]

# Step 2 — Rep comes online mid-conversation:
online

inject I'm starting to think this could be a real fit. What would a pilot look like?

# [OBSERVE: pilot_mindset signal fires. intent = evaluate.
#  Rep is now online but no handoff trigger yet. Mode = AUTONOMOUS.
#  Agent continues handling — rep's presence alone doesn't change mode.]

# Step 3 — Rep enters shadow to support a sensitive evaluation question:
shadow

inject We've had bad experiences with AI tools before. How do I know Sierra won't be the same?

# [OBSERVE: SHADOW mode active. Objection = trust.
#  Agent generates suggested response for the rep — warm, validating.
#  Rep decides whether to use it or respond directly.
#  FAIL if agent response is defensive or immediately pitch-like.]

# Step 4 — Rep switches to relay for pricing discussion:
relay

inject What does pricing look like?

# [OBSERVE: pricing_discussion signal fires.
#  In RELAY mode: draft appears, NOT delivered.
#  But pricing_discussion may also trigger ALERT (check mode output).
#  If ALERT fires: brief appears, mode overrides relay.
#  If still RELAY: draft appears for rep approval.]

approve

# [OBSERVE: Draft delivered if RELAY. If ALERT fired, approval has no effect —
#  brief is already showing. Check which mode actually fired.]

# Step 5 — Human request arrives — rep goes back to direct contact:
inject Actually, can I just speak to someone directly?

# [OBSERVE: human_request fires. ALERT mode.
#  Brief appears. urgency_sla = 15 min.
#  Mode = ALERT overrides RELAY — escalation always wins.
#  FAIL if relay draft appears instead of alert brief.]

# Step 6 — Final context review — full journey visible:
context

# [OBSERVE: handoff_queue shows all events across the session.
#  customer_state shows the trust trajectory.
#  collaboration_mode shows the final state.
#  fit_score reflects accumulated signals across all 7 turns.]

brief

# [OBSERVE: Latest brief is for human_request.
#  Rep has everything needed to make the direct call.]

reset
