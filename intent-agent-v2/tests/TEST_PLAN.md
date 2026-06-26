# ══════════════════════════════════════════════════════════════
# LEAD AGENT — COMPLETE TEST PLAN
# Sierra AI — Agentic Customer Service
# ══════════════════════════════════════════════════════════════
#
# VERSION: Experiment stage (pre-LLM upgrade)
# STACK:   Rule-based extractor + hardcoded behavior engine
# TOOLS:   pytest, python3 -m src.chat, python3 -m src.rep_chat
#
# WHAT THIS PLAN COVERS
# ─────────────────────────────────────────────────────────────
# Four testing phases in order:
#
#   Phase 1 — Automated unit tests      (pytest, ~10 min)
#   Phase 2 — Automated behavior tests  (pytest, ~5 min)
#   Phase 3 — Manual persona tests      (terminal chat, ~60 min)
#   Phase 4 — Manual rep tests          (terminal rep, ~45 min)
#
# Run phases in order. A failing Phase 1 produces noise in
# Phase 3. Fix foundation first, then move up.
#
# WHAT "DONE" LOOKS LIKE
# ─────────────────────────────────────────────────────────────
# Phase 1: All 30 unit tests pass
# Phase 2: All 20 behavior tests pass (soul.md constraints hold)
# Phase 3: All 6 personas complete with no FAIL observations
# Phase 4: All 4 rep collaboration modes verified as working
# Overall: Extractor gap log has at least 10 documented entries
#          ready to become the LLM upgrade spec
# ══════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════
# PHASE 1 — AUTOMATED UNIT TESTS
# What: verify that all state machine logic, trigger rules,
#       and domain decisions work correctly in isolation
# Why:  these are the foundation — if state machines are wrong,
#       everything above them is wrong too
# Time: ~10 minutes
# Tool: pytest in terminal
# ══════════════════════════════════════════════════════════════

# ── GOAL ─────────────────────────────────────────────────────
# Confirm that every state transition, trigger priority, SLA
# value, and fit evaluation decision produces the correct output
# given known inputs. No ambiguity — these are deterministic.

# ── SETUP ────────────────────────────────────────────────────
# From project root (intent-agent-v2/):
source venv/bin/activate
pytest tests/ -v --tb=short

# ── TEST FILES AND WHAT EACH COVERS ──────────────────────────

# FILE: test_trust_state_transitions.py
# Covers: TrustStateMachine transitions forward and backward
#
# Tests and what they verify:
#   test_awareness_to_curiosity_on_explore_intent
#     → AWARENESS transitions to CURIOSITY when intent = "explore"
#   test_curiosity_to_objection_when_objection_flag
#     → CURIOSITY moves to OBJECTION when objection = True
#   test_curiosity_objection_wins_over_low_urgency_when_both
#     → OBJECTION beats HESITATION when both signals fire (priority order)
#   test_curiosity_to_hesitation_on_low_urgency
#     → CURIOSITY moves to HESITATION when urgency = "low"
#   test_evaluation_to_trust_building_on_high_trust_score
#     → EVALUATION moves to TRUST_BUILDING when trust_score >= 0.75
#   test_trust_building_to_decision_ready_on_buying_signal
#     → TRUST_BUILDING moves to DECISION_READY on strong_buying_signal
#   test_decision_ready_advances_to_commitment [GAP TEST]
#     → DECISION_READY → COMMITMENT only with positive signal
#   test_no_op_transition_when_rules_do_not_apply
#     → State holds when no matching transition rule fires
#   test_objection_resolves_back_to_evaluation [GAP TEST]
#     → OBJECTION → EVALUATION when resolve = True
#   test_hesitation_resolves_back_to_curiosity [GAP TEST]
#     → HESITATION → CURIOSITY when resolve = True
#   test_decision_ready_does_not_commit_when_objection_raised [GAP TEST]
#     → DECISION_READY holds when objection = True (soul.md priority 2)
#   test_decision_ready_does_not_commit_on_low_urgency [GAP TEST]
#     → DECISION_READY holds when urgency = "low"
#
# EXPECTED: all pass
# IF ANY FAIL: fix trust_state_machine.py before continuing

# ─────────────────────────────────────────────────────────────

# FILE: test_collaboration_mode_transitions.py
# Covers: ModeStateMachine transitions and offline drop events
#
# Tests and what they verify:
#   test_mode_transition_matrix (6 parametrized cases)
#     → All 6 mode combinations produce correct CollaborationMode
#     → offline → AUTONOMOUS regardless of other flags
#     → handoff + rep online → ALERT
#     → handoff + approval → ALERT wins (not RELAY)
#     → approval only → RELAY
#     → live session → SHADOW
#     → rep online idle → AUTONOMOUS
#   test_offline_drop_from_alert_emits_handoff_queue_event [GAP TEST]
#     → Going offline mid-ALERT writes event to handoff_queue
#     → Event contains interrupted_mode = ALERT, reason = rep_went_offline
#   test_offline_drop_from_relay_emits_handoff_queue_event [GAP TEST]
#     → Going offline mid-RELAY writes event to handoff_queue
#   test_offline_drop_from_autonomous_does_not_emit_event [GAP TEST]
#     → AUTONOMOUS → AUTONOMOUS drop writes no spurious event
#   test_offline_drop_from_shadow_emits_handoff_queue_event [GAP TEST]
#     → Going offline mid-SHADOW writes event to handoff_queue
#
# EXPECTED: all pass
# IF ANY FAIL: fix mode_state_machine.py context parameter

# ─────────────────────────────────────────────────────────────

# FILE: test_trigger_catalog.py
# Covers: SLA values, trigger mappings, frustration override
#
# Tests and what they verify:
#   test_sla_same_for_handoff_and_rep_brief_key
#     → pricing_discussion SLA = pricing SLA (no drift)
#     → strong_buying_signal SLA = buying_intent SLA (no drift)
#   test_rep_brief_mapping
#     → pricing_discussion maps to "pricing" in brief
#     → strong_buying_signal maps to "buying_intent" in brief
#   test_format_sla_display
#     → 15 minutes formats as "15 min"
#     → 120 minutes formats as "2 hours"
#   test_frustration_urgency_override_constant_is_immediate [GAP TEST]
#     → _FRUSTRATION_URGENCY_OVERRIDE = "immediate" (not catalog value)
#   test_frustration_alert_brief_urgency_is_immediate [GAP TEST]
#     → AlertBrief.urgency_sla = "immediate" for frustration trigger
#   test_frustration_alert_brief_action_instructs_direct_contact [GAP TEST]
#     → brief action contains "do not re-engage via agent"
#   test_frustration_alert_brief_overrides_catalog_action [GAP TEST]
#     → brief action = soul-level constant, not catalog value
#   test_angry_synonym_also_produces_immediate_urgency [GAP TEST]
#     → "angry" trigger maps to "frustration" and gets same override
#   test_catalog_frustration_sla_is_known_value [CANARY]
#     → catalog SLA for frustration = 30 min (alerts if catalog changes)
#
# EXPECTED: all pass
# IF ANY FAIL: fix rep_assist_engine.py frustration guard

# ─────────────────────────────────────────────────────────────

# FILE: test_handoff_triggers_and_sla.py
# Covers: HandoffManager priority ordering, fit_confirmed gate
#
# Tests and what they verify:
#   test_human_request_wins_over_later_rules
#     → human_request trigger beats pricing + buying_signal combined
#   test_pricing_discussion_when_no_human
#     → pricing_discussion triggers when human_request = False
#   test_frustration_from_signal_overrides_context_sentiment
#     → frustration in signals overrides neutral context sentiment
#   test_frustration_from_context_when_absent_in_signals
#     → frustrated context sentiment triggers even with empty signals
#   test_no_trigger_when_signals_clear
#     → no handoff fires when all signals are False/neutral
#   test_sla_minutes_by_trigger_type (8 parametrized cases)
#     → human_request = 15 min
#     → pricing_discussion = 120 min
#     → strong_buying_signal = 60 min
#     → frustration = 30 min (overridden to "immediate" in engine)
#     → unknown trigger = 60 min default
#   test_decision_ready_without_fit_confirmed_returns_fit_check [GAP TEST]
#     → fit_confirmed=False → _FIT_CHECK_RESPONSE (not handoff template)
#   test_decision_ready_with_fit_confirmed_true_renders_handoff [GAP TEST]
#     → fit_confirmed=True → handoff template with rep name
#   test_decision_ready_fit_confirmed_absent_defaults_to_false [GAP TEST]
#     → omitting fit_confirmed in signals → safe default (fit check runs)
#   test_decision_ready_fit_confirmed_false_with_no_rep [GAP TEST]
#     → fit check fires even without assigned rep
#   test_decision_ready_fit_confirmed_true_no_rep_uses_generic [GAP TEST]
#     → fit confirmed + no rep → generic handoff copy (not named rep)
#
# EXPECTED: all pass
# IF ANY FAIL: fix behavior_engine.py _decision_ready_bridge

# ── HOW TO RUN PHASE 1 ────────────────────────────────────────

# Run all unit tests at once:
pytest tests/test_trust_state_transitions.py \
       tests/test_collaboration_mode_transitions.py \
       tests/test_trigger_catalog.py \
       tests/test_handoff_triggers_and_sla.py -v

# Run with coverage (see which lines aren't tested):
pytest tests/test_trust_state_transitions.py \
       tests/test_collaboration_mode_transitions.py \
       tests/test_trigger_catalog.py \
       tests/test_handoff_triggers_and_sla.py \
       --cov=src --cov-report=term-missing

# ── PHASE 1 PASS CRITERIA ────────────────────────────────────
# ✓ All tests show PASSED
# ✓ No FAILED or ERROR lines
# ✓ Coverage > 80% on:
#     src/customer_layer/trust_state_machine.py
#     src/collaboration/mode_state_machine.py
#     src/rep_layer/rep_assist_engine.py
#     src/collaboration/handoff_manager.py


# ══════════════════════════════════════════════════════════════
# PHASE 2 — AUTOMATED BEHAVIOR TESTS
# What: verify that agent OUTPUT respects soul.md values
# Why:  unit tests verify logic; behavior tests verify the agent
#       says the right things in the right situations
# Time: ~5 minutes
# Tool: pytest in terminal
# Prerequisite: Phase 1 must pass first
# ══════════════════════════════════════════════════════════════

# ── GOAL ─────────────────────────────────────────────────────
# Confirm that soul.md constraints are enforced in the actual
# text the agent produces — not just in the logic that produces
# it. Five constraint categories, each tested exhaustively.

# ── HOW TO RUN ────────────────────────────────────────────────
pytest tests/test_behavior_soul_compliance.py -v

# ── TEST CATEGORIES AND WHAT EACH COVERS ──────────────────────

# CATEGORY B1 — Identity honesty (soul.md value 6)
# Tests: 6 parametrized identity question phrasings
# Goal: agent never deflects or evades a direct identity question
# Key assertion: response contains "ai" or "assistant"
# Key assertion: response does NOT contain "i'm alex", "great question",
#                "part of the team", or other deflection patterns
# PASS: all 6 phrasings get an honest disclosure
# FAIL: any phrasing gets a deflection

# CATEGORY B2 — No fake urgency (soul.md value 1)
# Tests: all 8 trust states × all urgency-forbidden patterns
# Goal: no response branch ever contains urgency or scarcity language
# Key assertion: "limited time", "expires soon", "act now",
#                "last chance", etc. never appear in any response
# PASS: zero urgency patterns across all states
# FAIL: any state produces urgency language

# CATEGORY B3 — Fit check before handoff (soul.md value 3 + priority 2)
# Tests: fit_confirmed=False blocks bridge, True allows it,
#        absent defaults to False, internal fields never leak
# Goal: DECISION_READY never renders handoff template without fit_confirmed
# Key assertion: fit_confirmed=False → _FIT_CHECK_RESPONSE exactly
# Key assertion: CRM IDs, lead scores, internal notes never in customer text
# PASS: fit gate holds in all conditions
# FAIL: handoff template appears without fit_confirmed=True

# CATEGORY B4 — Frustration escalates immediately (priority 2)
# Tests: all 3 frustration trigger variants × urgency and action
# Goal: every frustration path produces immediate escalation
# Key assertion: urgency_sla = "immediate" for all frustration triggers
# Key assertion: action contains "do not re-engage via agent"
# PASS: immediate escalation across all variants
# FAIL: any frustration path produces non-immediate urgency

# CATEGORY B5 — Summary honesty (soul.md value 7)
# Tests: 6 known softening patterns, clean summary baseline,
#        mutation check, sentiment mismatch warning
# Goal: validator fires on spin, never mutates, returns original
# Key assertion: logger.warning fires on softening patterns
# Key assertion: return value === input value (no mutation)
# Key assertion: negative sentiment + softening = distortion risk noted
# PASS: validator catches all patterns, never alters summary
# FAIL: pattern missed, or summary mutated, or no warning logged

# ── PHASE 2 PASS CRITERIA ────────────────────────────────────
# ✓ All behavior tests show PASSED
# ✓ Zero urgency patterns detected in any trust state
# ✓ Identity disclosure fires correctly for all phrasings
# ✓ Fit gate blocks handoff without explicit fit_confirmed
# ✓ Frustration produces "immediate" urgency in all cases
# ✓ Summary validator logs warning and returns unchanged


# ══════════════════════════════════════════════════════════════
# PHASE 3 — MANUAL PERSONA TESTS
# What: run each of the 6 customer personas through a realistic
#       conversation and observe how the agent behaves
# Why:  automated tests check logic; persona tests check whether
#       the agent feels right in a real conversation flow
# Time: ~60 minutes (10 min per persona)
# Tool: python3 -m src.chat
# Prerequisite: Phase 1 and Phase 2 must pass first
# Reference: PERSONA_SCRIPTS.md, PROMPT_BANK.md
# ══════════════════════════════════════════════════════════════

# ── GOAL ─────────────────────────────────────────────────────
# For each persona, verify that:
# 1. The extractor reads the right signals from natural language
# 2. The trust state advances correctly across the conversation
# 3. The agent's response posture matches soul.md for each state
# 4. Handoff triggers fire at the right moment with the right urgency
# 5. Extractor gaps are documented when signals are missed

# ── SETUP ─────────────────────────────────────────────────────
# Terminal 1:
python3 -m src.chat

# Answer rep online prompt as specified per persona below.
# Keep PERSONA_SCRIPTS.md open in a side panel for reference.
# Keep this file open to record observations.

# ── PERSONA TEST LOG TEMPLATE ─────────────────────────────────
# Complete one entry per persona after the session:
#
# PERSONA: [name]
# DATE: [date]
# REP ONLINE: [y/n]
# TURNS COMPLETED: [number]
#
# Per-turn observations:
# Turn N | Input: [message] | State: [trust state] | Mode: [mode]
#         | Signal: [what fired] | Response tone: [posture]
#         | Pass/Fail: [✓/✗] | Notes: [anything unexpected]
#
# Extractor gaps found: [list prompts where signals were missed]
# Soul.md violations found: [list any responses that failed]
# Overall verdict: [PASS / PARTIAL / FAIL]
# ─────────────────────────────────────────────────────────────

# ═══════════════════════
# PERSONA 1 — THE SKEPTIC
# ═══════════════════════
# Rep online: NO
# Duration: ~10 minutes
# Prompts: use P1 section from PROMPT_BANK.md

# TEST GOAL: Confirm the agent handles doubt, probing questions,
# and identity challenges without becoming defensive or evasive.

# STEP 1: Start chat, answer 'n' for rep online
# STEP 2: Run opening prompts (skeptical frame establishment)
# STEP 3: Run identity test prompts
# STEP 4: Run objection escalation prompts
# STEP 5: Run hesitation prompts
# STEP 6: Type 'state' — check trust state and handoff_queue
# STEP 7: Type 'reset'

# WHAT TO VERIFY:
# ┌─────────────────────────────────────────────────────────┐
# │ Check                        Expected        Observed   │
# ├─────────────────────────────────────────────────────────┤
# │ Response to "are you a bot"  AI disclosure   __________ │
# │ Response to objection        Validates first __________ │
# │ Urgency language present     Never           __________ │
# │ Defensive patterns present   Never           __________ │
# │ Trust state at turn 5        OBJECTION/HESI  __________ │
# │ Handoff queue at end         Empty           __________ │
# │ Mode throughout              AUTONOMOUS      __________ │
# └─────────────────────────────────────────────────────────┘

# EXTRACTOR GAPS TO TEST:
# - "Are you actually a human writing these?" → identity_question fires?
# - "I feel like I'm going in circles" → frustration fires?
# - "There's a lot going on internally" → urgency = low fires?
# Record what actually happens in each case.

# ═══════════════════════════
# PERSONA 2 — THE EAGER BUYER
# ═══════════════════════════
# Rep online: YES
# Duration: ~10 minutes
# Prompts: use P2 section from PROMPT_BANK.md

# TEST GOAL: Confirm the agent doesn't rush to handoff despite
# high enthusiasm. Fit validation must gate the DECISION_READY bridge.

# STEP 1: Start chat, answer 'y' for rep online
# STEP 2: Run high enthusiasm opening prompts
# STEP 3: Run strong fit signal prompts (Zendesk, volume, etc.)
# STEP 4: Run premature close attempt ("can we sign this week?")
# STEP 5: Observe whether fit_confirmed fires or fit-check appears
# STEP 6: Type 'state' — check fit_score and fit_confirmed
# STEP 7: Type 'reset'

# WHAT TO VERIFY:
# ┌─────────────────────────────────────────────────────────┐
# │ Check                        Expected        Observed   │
# ├─────────────────────────────────────────────────────────┤
# │ Urgency mirroring present    Never           __________ │
# │ fit_score after Zendesk msg  Positive (>0)   __________ │
# │ fit_confirmed after 3 turns  True or False   __________ │
# │ Response to "can we sign"    Fit-check or    __________ │
# │                              handoff (depends on score) │
# │ Handoff template has rep     Yes if ALERT    __________ │
# │ Mode when human req fires    ALERT           __________ │
# └─────────────────────────────────────────────────────────┘

# CRITICAL CHECK:
# After "I'd like to speak to someone about pricing":
#   → mode MUST = ALERT
#   → rep brief MUST appear
#   → customer message MUST NOT appear
# If customer message appears when mode = ALERT, that is a FAIL.

# ═══════════════════════
# PERSONA 3 — THE GHOSTER
# ═══════════════════════
# Rep online: NO
# Duration: ~10 minutes
# Prompts: use P3 section from PROMPT_BANK.md

# TEST GOAL: Confirm the agent handles silence and minimal
# responses with patience — never manufacturing urgency.

# STEP 1: Start chat, answer 'n' for rep online
# STEP 2: Run initial interest prompts
# STEP 3: Send silence simulations (single period, "ok", "sorry")
# STEP 4: Run re-engagement prompts
# STEP 5: Run fit signal prompts (Zendesk, volume) mid-ghost
# STEP 6: Type 'state' — verify mode = AUTONOMOUS throughout
# STEP 7: Type 'reset'

# WHAT TO VERIFY:
# ┌─────────────────────────────────────────────────────────┐
# │ Check                        Expected        Observed   │
# ├─────────────────────────────────────────────────────────┤
# │ Response to "." (period)     Warm, open      __________ │
# │ Response to "ok"             Non-pressured   __________ │
# │ Urgency after silence        Never           __________ │
# │ Scarcity after silence       Never           __________ │
# │ Patience language present    Yes             __________ │
# │ fit_score accumulates        Yes (gradually) __________ │
# │ Mode throughout              AUTONOMOUS      __________ │
# └─────────────────────────────────────────────────────────┘

# EXTRACTOR GAPS TO TEST:
# - "I keep meaning to loop back" → what signal fires?
# - "This is on my radar" → does intent = explore fire?
# - "We're planning a pilot next quarter" → pilot_mindset fires?

# ═══════════════════════════════
# PERSONA 4 — THE FRUSTRATED ONE
# ═══════════════════════════════
# Rep online: YES (required for ALERT to fire)
# Duration: ~10 minutes
# Prompts: use P4 section from PROMPT_BANK.md

# TEST GOAL: Confirm frustration triggers immediate escalation
# to rep, suppresses customer response, and produces correct brief.

# STEP 1: Start chat, answer 'y' for rep online
# STEP 2: Run background frustration-building prompts (2 turns)
# STEP 3: Send explicit frustration trigger ("this is so frustrating")
# STEP 4: Observe ALERT mode firing — note urgency_sla in output
# STEP 5: Send indirect frustration prompts — document whether they fire
# STEP 6: Type 'state' — check handoff_queue
# STEP 7: Type 'reset'

# WHAT TO VERIFY:
# ┌─────────────────────────────────────────────────────────┐
# │ Check                        Expected        Observed   │
# ├─────────────────────────────────────────────────────────┤
# │ Mode on frustration message  ALERT           __________ │
# │ urgency_sla on brief         "immediate"     __________ │
# │ Customer message visible     NO              __________ │
# │ Brief action contains        "do not re-     __________ │
# │                              engage via agent"          │
# │ trigger in brief             "frustration"   __________ │
# │ handoff_queue after ALERT    1 event         __________ │
# └─────────────────────────────────────────────────────────┘

# EXTRACTOR GAPS TO TEST (document all results):
# - "at my wits end" → frustration fires? (expected: NO)
# - "talking to walls" → frustration fires? (expected: NO)
# - "burned out" → frustration fires? (expected: NO)
# - "fed up" → frustration fires? (expected: YES — in keywords)
# - "ridiculous" → frustration fires? (expected: YES — in keywords)

# ═══════════════════════════
# PERSONA 5 — THE POOR FIT
# ═══════════════════════════
# Rep online: NO
# Duration: ~10 minutes
# Prompts: use P5 section from PROMPT_BANK.md

# TEST GOAL: Confirm honest disqualification — fit_score goes
# negative and blocks handoff despite strong positive signals.

# STEP 1: Start chat, answer 'n' for rep online
# STEP 2: Run poor fit signal prompts (small team, no tools, low volume)
# STEP 3: Run warm buying signals ("I'm ready to get started")
# STEP 4: Observe whether fit-check fires or handoff renders
# STEP 5: Type 'state' — verify fit_score is negative
# STEP 6: Type 'reset'

# WHAT TO VERIFY:
# ┌─────────────────────────────────────────────────────────┐
# │ Check                        Expected        Observed   │
# ├─────────────────────────────────────────────────────────┤
# │ fit_score after "30 tickets" Negative        __________ │
# │ fit_confirmed throughout     False           __________ │
# │ Response to "ready to sign"  Fit-check       __________ │
# │ Handoff template appears     Never           __________ │
# │ Rep brief generated          Never           __________ │
# │ Rejection language in resp   Never           __________ │
# │ Tone of fit-check response   Open, curious   __________ │
# └─────────────────────────────────────────────────────────┘

# EXTRACTOR GAPS TO TEST:
# - "We're growing fast, 10x in 6 months" → high_volume signal?
# - "Planning to move to Zendesk next quarter" → helpdesk signal?
# These are both expected NO — document for LLM upgrade spec.

# ═══════════════════════════════
# PERSONA 6 — THE HUMAN REQUESTER
# ═══════════════════════════════
# Rep online: YES (required)
# Duration: ~10 minutes
# Prompts: use P6 section from PROMPT_BANK.md

# TEST GOAL: Confirm human_request triggers ALERT immediately
# at every trust state, and wins over all competing signals.

# STEP 1: Start chat, answer 'y' for rep online
# STEP 2: Send explicit human request at AWARENESS ("can I speak to someone?")
# STEP 3: Observe ALERT fires immediately. Type 'reset'.
# STEP 4: Restart, build 2-3 turns of context, then send human request
# STEP 5: Verify ALERT fires mid-conversation too
# STEP 6: Test competing signals: human_request + pricing + buying_signal
# STEP 7: Verify trigger = human_request (not pricing or buying_intent)
# STEP 8: Type 'reset'

# WHAT TO VERIFY:
# ┌─────────────────────────────────────────────────────────┐
# │ Check                        Expected        Observed   │
# ├─────────────────────────────────────────────────────────┤
# │ Mode on "real person" msg    ALERT           __________ │
# │ trigger in brief             human_request   __________ │
# │ urgency_sla                  15 min          __________ │
# │ Customer message visible     NO              __________ │
# │ Fires at AWARENESS           Yes             __________ │
# │ Fires at TRUST_BUILDING      Yes             __________ │
# │ Wins over pricing signal     Yes             __________ │
# │ Wins over buying_signal      Yes             __________ │
# └─────────────────────────────────────────────────────────┘

# EXTRACTOR GAPS TO TEST:
# - "Is there someone I can get on a call with?" → fires?
# - "I'd love to chat with your team directly" → fires?
# - "Do you have anyone I could talk to?" → fires?
# Document which phrasings the extractor catches vs misses.

# ── PHASE 3 PASS CRITERIA ────────────────────────────────────
# ✓ All 6 personas complete without FAIL observations
# ✓ ALERT fires at correct moments for P4 and P6
# ✓ fit-check blocks handoff for P2 (if score low) and P5 always
# ✓ No urgency language appears in any persona's responses
# ✓ Identity disclosure fires correctly for P1 identity prompts
# ✓ Extractor gap log has at least 8 documented entries


# ══════════════════════════════════════════════════════════════
# PHASE 4 — MANUAL REP COLLABORATION TESTS
# What: test all four collaboration modes and rep-facing
#       behaviors using the rep terminal
# Why:  the rep experience is the second half of the system —
#       the dual behavior layer must work from both sides
# Time: ~45 minutes
# Tool: python3 -m src.rep_chat
# Prerequisite: Phase 3 must complete first
# Reference: REP_SCRIPTS.md
# ══════════════════════════════════════════════════════════════

# ── GOAL ─────────────────────────────────────────────────────
# Verify that all four collaboration modes activate correctly,
# the rep receives complete and accurate briefings, and handoff
# context is never lost — even across offline transitions.

# ── SETUP ─────────────────────────────────────────────────────
# Terminal:
python3 -m src.rep_chat

# Keep REP_SCRIPTS.md open for the full command sequences.
# Complete one rep scenario at a time. Type 'reset' between each.

# ── REP SCENARIO TEST LOG TEMPLATE ───────────────────────────
# SCENARIO: [name]
# DATE: [date]
# COMMANDS RUN: [list]
#
# Check                          Expected          Observed
# ──────────────────────────────────────────────────────────
# Mode after command             [expected mode]   __________
# urgency_sla in brief           [expected value]  __________
# Customer message visible       [yes/no]          __________
# handoff_queue event count      [expected count]  __________
# Context preserved after reset  N/A               __________
# ─────────────────────────────────────────────────────────────

# ═══════════════════════════════════════════
# REP SCENARIO 1 — FRUSTRATION ALERT (R1)
# ═══════════════════════════════════════════
# Commands: online → assign → inject (normal) → inject (frustration)
# Duration: ~8 minutes

# TEST GOAL: Verify frustration escalation path end-to-end
# from the rep's perspective.

# WHAT TO VERIFY:
# ┌─────────────────────────────────────────────────────────┐
# │ Check                        Expected        Observed   │
# ├─────────────────────────────────────────────────────────┤
# │ Mode after frustration inj.  ALERT           __________ │
# │ urgency_sla in brief         "immediate"     __________ │
# │ recommended_action           no re-engage    __________ │
# │ Customer msg visible         NO              __________ │
# │ handoff_queue after offline  1 event         __________ │
# │ interrupted_mode in event    ALERT           __________ │
# │ reason in event              rep_went_offline__________ │
# │ Queue visible after online   YES             __________ │
# └─────────────────────────────────────────────────────────┘

# ══════════════════════════════════════════════
# REP SCENARIO 2 — SHADOW MODE SUPPORT (R2)
# ══════════════════════════════════════════════
# Commands: assign → online → inject (context) → shadow → inject
# Duration: ~8 minutes

# TEST GOAL: Verify SHADOW mode activates correctly and agent
# generates suggested responses while rep leads.

# WHAT TO VERIFY:
# ┌─────────────────────────────────────────────────────────┐
# │ Check                        Expected        Observed   │
# ├─────────────────────────────────────────────────────────┤
# │ Mode after 'shadow'          SHADOW          __________ │
# │ Agent response in shadow     Suggested (rep  __________ │
# │                              can use or not)            │
# │ fit_score accumulating       Yes             __________ │
# │ Urgency in suggestion        Never           __________ │
# │ Rep still in control         Yes             __________ │
# └─────────────────────────────────────────────────────────┘

# ══════════════════════════════════════════════
# REP SCENARIO 3 — RELAY DRAFT APPROVAL (R3)
# ══════════════════════════════════════════════
# Commands: assign → online → relay → inject → approve → inject
# Duration: ~8 minutes

# TEST GOAL: Verify RELAY mode draft-and-approve flow works
# correctly. Draft appears, rep approves, then delivers.

# WHAT TO VERIFY:
# ┌─────────────────────────────────────────────────────────┐
# │ Check                        Expected        Observed   │
# ├─────────────────────────────────────────────────────────┤
# │ Mode after 'relay'           RELAY           __________ │
# │ Draft appears before approve YES             __________ │
# │ Draft delivered before appr. NO              __________ │
# │ "Approved and delivered" msg YES after appr. __________ │
# │ Draft tone                   Non-pushy       __________ │
# │ Urgency in draft             Never           __________ │
# └─────────────────────────────────────────────────────────┘

# ════════════════════════════════════════════════════
# REP SCENARIO 4 — OFFLINE DROP CONTEXT PRESERVATION (R4)
# ════════════════════════════════════════════════════
# Commands: assign → online → inject (human_request) → offline
#           → inject → online → context → brief
# Duration: ~8 minutes

# TEST GOAL: Verify that going offline mid-ALERT preserves
# the interrupted context so the rep can recover on return.

# WHAT TO VERIFY:
# ┌─────────────────────────────────────────────────────────┐
# │ Check                        Expected        Observed   │
# ├─────────────────────────────────────────────────────────┤
# │ Mode after human_request     ALERT           __________ │
# │ Mode after 'offline'         AUTONOMOUS      __________ │
# │ handoff_queue event present  YES             __________ │
# │ interrupted_mode in event    ALERT           __________ │
# │ Agent handles while offline  YES             __________ │
# │ Queue still visible online   YES             __________ │
# │ Brief retrievable on return  YES             __________ │
# └─────────────────────────────────────────────────────────┘

# ════════════════════════════════════════════════
# REP SCENARIO 5 — HIGH-VALUE CLOSE SEQUENCE (R5)
# ════════════════════════════════════════════════
# Commands: assign → online → score 75 → inject (fit signals ×3)
#           → inject (buying signal) → shadow
# Duration: ~10 minutes

# TEST GOAL: Verify fit evaluation accumulates correctly and
# handoff template renders with rep name when fit confirmed.

# WHAT TO VERIFY:
# ┌─────────────────────────────────────────────────────────┐
# │ Check                        Expected        Observed   │
# ├─────────────────────────────────────────────────────────┤
# │ fit_score after 3 signals    Positive (>5)   __________ │
# │ fit_confirmed after thresh.  True            __________ │
# │ Handoff template contains    Rep name        __________ │
# │ Fit-check blocks if low      Yes             __________ │
# │ SHADOW support quality       Non-pushy       __________ │
# └─────────────────────────────────────────────────────────┘

# ═══════════════════════════════════════════════
# REP SCENARIO 6 — POOR FIT DISQUALIFICATION (R6)
# ═══════════════════════════════════════════════
# Commands: assign → online → inject (poor fit ×3)
#           → inject (buying signals) → context
# Duration: ~8 minutes

# TEST GOAL: Verify that poor fit signals dominate and no
# rep brief is generated despite strong buying intent.

# WHAT TO VERIFY:
# ┌─────────────────────────────────────────────────────────┐
# │ Check                        Expected        Observed   │
# ├─────────────────────────────────────────────────────────┤
# │ fit_score after poor signals Negative        __________ │
# │ fit_confirmed throughout     False           __________ │
# │ Handoff template appears     Never           __________ │
# │ Rep brief generated          Never           __________ │
# │ Fit-check fires at READY     Yes             __________ │
# │ Fit-check tone               Open, not harsh __________ │
# └─────────────────────────────────────────────────────────┘

# ── PHASE 4 PASS CRITERIA ────────────────────────────────────
# ✓ All 4 collaboration modes activate correctly
# ✓ ALERT brief always shows urgency_sla correctly
# ✓ Frustration brief contains "do not re-engage via agent"
# ✓ Offline drop writes event to handoff_queue
# ✓ Context recoverable when rep returns online
# ✓ RELAY draft never delivers without explicit approve
# ✓ fit_confirmed gates handoff template in both terminals


# ══════════════════════════════════════════════════════════════
# EXTRACTOR GAP LOG
# Complete this across all phases. Minimum 10 entries before
# considering the LLM extractor upgrade ready to specify.
# ══════════════════════════════════════════════════════════════

# HOW TO COMPLETE AN ENTRY
# ─────────────────────────
# After any test where the agent response surprised you —
# either the signal didn't fire or the trust state didn't
# move as expected — fill in one entry here.

# ENTRY FORMAT:
# ─────────────────────────────────────────────────────────────
# GAP #: [number]
# PROMPT: [exact message you sent]
# EXPECTED SIGNAL: [what should have fired]
# ACTUAL SIGNAL: [what fired — from terminal output]
# TRUST STATE EXPECTED: [what you expected]
# TRUST STATE ACTUAL: [what appeared in output]
# SOUL.MD IMPACT: [did the response feel wrong as a result?]
# LLM UPGRADE NOTE: [what the LLM extractor needs to handle]
# ─────────────────────────────────────────────────────────────

# KNOWN GAPS (pre-filled from prompt bank analysis):
#
# GAP #1
# PROMPT: "You know what, I think I was overthinking it."
# EXPECTED SIGNAL: resolve = True → OBJECTION → EVALUATION
# ACTUAL SIGNAL: no resolve fires (rule-based can't detect implicit)
# TRUST STATE EXPECTED: EVALUATION
# TRUST STATE ACTUAL: OBJECTION (stuck)
# SOUL.MD IMPACT: Agent keeps using objection language after issue resolved
# LLM UPGRADE NOTE: detect implicit resolution in natural conversational phrases
#
# GAP #2
# PROMPT: "I'm at my wits end with this whole process."
# EXPECTED SIGNAL: sentiment = frustration → ALERT
# ACTUAL SIGNAL: sentiment = negative (not frustration)
# TRUST STATE EXPECTED: ALERT mode triggered
# TRUST STATE ACTUAL: AUTONOMOUS, OBJECTION
# SOUL.MD IMPACT: Frustration escalation misses real frustrated customers
# LLM UPGRADE NOTE: understand emotional phrases beyond keyword list
#
# GAP #3
# PROMPT: "We're growing fast — expecting 10x volume in 6 months."
# EXPECTED SIGNAL: high_support_volume (future) → fit signal
# ACTUAL SIGNAL: no fit signal (keywords only catch current volume)
# TRUST STATE EXPECTED: fit_score increases
# TRUST STATE ACTUAL: no change
# SOUL.MD IMPACT: agent under-qualifies genuinely good fits
# LLM UPGRADE NOTE: reason about future state and growth trajectory
#
# GAP #4
# PROMPT: "We spend most of our day answering the same five questions."
# EXPECTED SIGNAL: repetitive_ticket_types
# ACTUAL SIGNAL: no signal (phrase not in keyword list)
# TRUST STATE EXPECTED: fit_score increases
# TRUST STATE ACTUAL: no change
# SOUL.MD IMPACT: strong fit indicator missed entirely
# LLM UPGRADE NOTE: understand semantically equivalent descriptions
#
# [Continue adding entries during testing sessions]
# GAP #5: ____________________________________________
# GAP #6: ____________________________________________
# GAP #7: ____________________________________________
# GAP #8: ____________________________________________
# GAP #9: ____________________________________________
# GAP #10: ___________________________________________


# ══════════════════════════════════════════════════════════════
# OVERALL TEST COMPLETION CHECKLIST
# ══════════════════════════════════════════════════════════════

# PHASE 1 — UNIT TESTS
# [ ] All trust state transition tests pass
# [ ] All collaboration mode tests pass
# [ ] All trigger catalog tests pass
# [ ] All handoff + fit_confirmed tests pass
# [ ] Coverage > 80% on core files

# PHASE 2 — BEHAVIOR TESTS
# [ ] B1 identity disclosure — all 6 phrasings pass
# [ ] B2 no urgency — all trust states clean
# [ ] B3 fit gate — blocks without confirmed, allows with
# [ ] B4 frustration — immediate urgency all variants
# [ ] B5 summary honesty — validator fires, no mutation

# PHASE 3 — PERSONA TESTS
# [ ] P1 Skeptic — complete, no FAIL observations
# [ ] P2 Eager Buyer — fit gate works despite momentum
# [ ] P3 Ghoster — patience maintained, no urgency
# [ ] P4 Frustrated — ALERT fires, urgency = immediate
# [ ] P5 Poor Fit — handoff blocked, fit-check fires
# [ ] P6 Human Requester — ALERT at all trust states

# PHASE 4 — REP TESTS
# [ ] R1 Frustration alert — brief correct, customer suppressed
# [ ] R2 Shadow mode — activates, agent supports silently
# [ ] R3 Relay approval — draft held, delivers on approve
# [ ] R4 Offline drop — queue preserved, context recoverable
# [ ] R5 High-value close — fit accumulates, template renders
# [ ] R6 Poor fit disqual — brief never generated

# EXTRACTOR GAP LOG
# [ ] Minimum 10 entries documented
# [ ] Each entry has LLM upgrade note

# ══════════════════════════════════════════════════════════════
# WHAT COMES AFTER THIS TEST PLAN
# ══════════════════════════════════════════════════════════════
#
# When all phases complete and the gap log has 10+ entries:
#
# 1. LLM EXTRACTOR UPGRADE
#    Replace extractor.py keyword matching with Claude API calls.
#    The gap log becomes the test cases for the new extractor.
#    Each gap entry is a prompt the LLM extractor must handle.
#
# 2. LLM RESPONSE GENERATION
#    Replace behavior_engine.py hardcoded strings with LLM calls.
#    soul.md becomes the system prompt.
#    product_context.md provides product knowledge.
#    Trust state + fit assessment provided as context per turn.
#
# 3. API LAYER
#    Wrap orchestrator.run_turn() in FastAPI.
#    Replace MemoryStore with persistent storage.
#    Add /chat, /context, /brief, /rep/action endpoints.
#
# 4. REP DASHBOARD UI
#    Build the visual layer for the rep-facing side.
#    Trust arc, mode switcher, fit score, alert queue.
#    Maps directly to OrchestrationResult data structure.
# ══════════════════════════════════════════════════════════════
