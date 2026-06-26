"""Rep collaboration terminal — simulates the sales rep's side of the system.

Run from project root:
    python3 -m src.rep_chat

This tool lets you play the role of the sales rep. It shows:
- Alert briefs when the agent escalates to you
- The full LeadContext at any point (what the agent knows)
- Rep actions you can take: go online/offline, take shadow mode,
  approve relay drafts, inject signals into the conversation
- The agent's behavior changing as you toggle collaboration modes

Use this ALONGSIDE src/chat.py to simulate both sides of the system.
In a real test session:
  Terminal 1: python3 -m src.chat    (you play the customer)
  Terminal 2: python3 -m src.rep_chat (you play the rep)

For solo testing, run rep_chat alone and use the scripted
inject commands to simulate customer messages without switching windows.

Commands (type at the rep prompt):
  online          — set rep status to online
  offline         — set rep status to offline
  shadow          — activate shadow mode (rep goes live)
  relay           — activate relay/approval mode
  approve         — approve the pending relay draft
  context         — print full LeadContext snapshot
  brief           — show the latest alert brief
  inject <msg>    — send a customer message as if from the customer terminal
  assign <name>   — assign a rep name to the lead context
  score <n>       — manually set lead_score (0-100)
  reset           — start a new lead session
  quit / exit     — end session
"""

from __future__ import annotations

import sys
from typing import Optional

from src.clients.sierra.fit_criteria import SIERRA_FIT_CRITERIA
from src.collaboration.mode_state_machine import CollaborationMode
from src.core.lead_context import LeadContext
from src.orchestrator import build_default_dependencies, run_turn


_DIVIDER = "─" * 60
_WIDE = "═" * 60


def _print_alert_brief(brief) -> None:
    b = brief.as_dict()
    print(f"\n{'!' * 60}")
    print(f"  ⚠️  ALERT BRIEF — action required")
    print(f"{'!' * 60}")
    print(f"  lead_id        : {b['lead_id']}")
    print(f"  trigger        : {b['trigger']}")
    print(f"  urgency_sla    : {b['urgency_sla']}")
    print(f"  lead_score     : {b['lead_score']}")
    print(f"  sentiment      : {b['sentiment']}")
    print(f"  recommended    : {b['recommended_action']}")
    print(f"  summary        : {b['summary'][:120]}")
    print(f"{'!' * 60}\n")


def _print_context(ctx: LeadContext) -> None:
    print(f"\n{_DIVIDER}")
    print("  LeadContext — full snapshot")
    print(_DIVIDER)
    print(f"  lead_id        : {ctx.lead_id}")
    print(f"  customer_state : {ctx.customer_state}")
    print(f"  collaboration  : {ctx.collaboration_mode}")
    print(f"  sentiment      : {ctx.sentiment}")
    print(f"  lead_score     : {ctx.lead_score}")
    print(f"  rep_online     : {ctx.rep_online}")
    print(f"  assigned_rep   : {ctx.assigned_rep or 'unassigned'}")
    print(f"  handoff_queue  : {len(ctx.handoff_queue)} events")
    for i, event in enumerate(ctx.handoff_queue):
        print(f"    [{i}] {event}")
    summary = ctx.conversation_summary
    if summary:
        print(f"  summary        :")
        # Print summary in readable wrapped chunks
        words = summary.split()
        line = "    "
        for word in words:
            if len(line) + len(word) > 72:
                print(line)
                line = "    " + word + " "
            else:
                line += word + " "
        if line.strip():
            print(line)
    print()


def _print_turn_result(result, label: str = "Customer turn") -> None:
    print(f"\n{_DIVIDER}")
    print(f"  {label}")
    print(_DIVIDER)
    print(f"  trust state    : {result.trust_state.value}")
    print(f"  mode           : {result.collaboration_mode}")
    print(f"  handoff        : {result.handoff_triggered} ({result.trigger_type})")
    print(f"  fit confirmed  : {result.fit_confirmed}")
    print(f"  fit score      : {result.fit_score}")
    print(f"  sentiment      : {result.lead_signals.sentiment}")

    if result.rep_alert_brief:
        _print_alert_brief(result.rep_alert_brief)

    if result.customer_message:
        print(f"\n  🤖 Agent said to customer:")
        print(f"  \"{result.customer_message}\"\n")


def _print_rep_prompt(rep_online: bool, mode: str) -> None:
    status = "🟢 online" if rep_online else "🔴 offline"
    print(f"  Rep [{status} | mode={mode}] > ", end="", flush=True)


def main() -> None:
    print(f"\n{_WIDE}")
    print("  Lead Agent — Rep Collaboration Terminal")
    print("  Client: Sierra AI — agentic customer service")
    print(_WIDE)
    print("  You are playing the role of the sales rep.")
    print("  The agent escalates to you when trust-critical moments occur.")
    print(f"{_WIDE}")
    print("  Commands: online | offline | shadow | relay | approve")
    print("            inject <msg> | context | brief | assign <name>")
    print("            score <n> | reset | quit")
    print(f"{_WIDE}\n")

    (
        store,
        signal_extractor,
        customer_engine,
        rep_engine,
        handoff_manager,
        mode_machine,
        _queue,
    ) = build_default_dependencies()

    lead_id = "rep-session-1"
    session_count = 1
    rep_online = False
    live_session = False
    awaiting_approval = False
    last_result = None
    last_brief = None
    pending_relay_draft: Optional[str] = None

    shared = dict(
        store=store,
        signal_extractor=signal_extractor,
        customer_engine=customer_engine,
        rep_engine=rep_engine,
        handoff_manager=handoff_manager,
        mode_machine=mode_machine,
        fit_criteria=SIERRA_FIT_CRITERIA,
    )

    # Initialise context in store
    ctx = LeadContext(lead_id=lead_id)
    store.save(ctx)

    _print_rep_prompt(rep_online, mode_machine.get_mode().value)

    for line in sys.stdin:
        cmd = line.strip()

        if not cmd:
            _print_rep_prompt(rep_online, mode_machine.get_mode().value)
            continue

        cmd_lower = cmd.lower()

        # ── quit ──────────────────────────────────────────────────
        if cmd_lower in ("quit", "exit"):
            print("\n  Rep session ended.\n")
            break

        # ── online ────────────────────────────────────────────────
        elif cmd_lower == "online":
            rep_online = True
            print("  ✓ Rep status set to ONLINE.")
            print("  Agent will now route alerts to you when triggered.")
            if last_result:
                ctx = store.get(lead_id)
                if ctx:
                    ctx.rep_online = True
                    store.save(ctx)

        # ── offline ───────────────────────────────────────────────
        elif cmd_lower == "offline":
            rep_online = False
            live_session = False
            print("  ✓ Rep status set to OFFLINE.")
            print("  Agent resumes AUTONOMOUS mode. Handoff events preserved.")
            # Trigger mode transition to record the offline drop event
            if last_result:
                ctx = store.get(lead_id)
                if ctx:
                    ctx.rep_online = False
                    mode_machine.transition(
                        rep_online=False,
                        live_session=False,
                        handoff_triggered=False,
                        awaiting_approval=False,
                        context=ctx,
                    )
                    store.save(ctx)
                    if ctx.handoff_queue:
                        print(f"  Handoff queue now has {len(ctx.handoff_queue)} event(s).")
                        print("  These will be visible when you come back online.")

        # ── shadow ────────────────────────────────────────────────
        elif cmd_lower == "shadow":
            if not rep_online:
                print("  ✗ Must be online to enter shadow mode. Type 'online' first.")
            else:
                live_session = True
                awaiting_approval = False
                new_mode = mode_machine.transition(
                    rep_online=True,
                    live_session=True,
                    handoff_triggered=False,
                    awaiting_approval=False,
                )
                print(f"  ✓ SHADOW mode activated. Mode = {new_mode.value}")
                print("  Agent supports silently. You lead the conversation.")
                print("  Use 'inject <msg>' to simulate the customer's next message")
                print("  and see what the agent would suggest.")

        # ── relay ─────────────────────────────────────────────────
        elif cmd_lower == "relay":
            if not rep_online:
                print("  ✗ Must be online to enter relay mode. Type 'online' first.")
            else:
                awaiting_approval = True
                live_session = False
                new_mode = mode_machine.transition(
                    rep_online=True,
                    live_session=False,
                    handoff_triggered=False,
                    awaiting_approval=True,
                )
                print(f"  ✓ RELAY mode activated. Mode = {new_mode.value}")
                print("  Agent will draft responses. You approve before delivery.")
                print("  Use 'inject <msg>' then 'approve' to simulate this flow.")

        # ── approve ───────────────────────────────────────────────
        elif cmd_lower == "approve":
            if pending_relay_draft:
                print(f"\n  ✓ Draft approved and delivered to customer:")
                print(f"  \"{pending_relay_draft}\"\n")
                pending_relay_draft = None
                awaiting_approval = False
            else:
                print("  ✗ No pending relay draft to approve.")
                print("  Use 'inject <msg>' in relay mode to generate a draft.")

        # ── context ───────────────────────────────────────────────
        elif cmd_lower == "context":
            ctx = store.get(lead_id)
            if ctx:
                _print_context(ctx)
            else:
                print("  No context found for current session.\n")

        # ── brief ─────────────────────────────────────────────────
        elif cmd_lower == "brief":
            if last_brief:
                _print_alert_brief(last_brief)
            else:
                print("  No alert brief generated yet this session.\n")

        # ── reset ─────────────────────────────────────────────────
        elif cmd_lower == "reset":
            session_count += 1
            lead_id = f"rep-session-{session_count}"
            live_session = False
            awaiting_approval = False
            last_result = None
            last_brief = None
            pending_relay_draft = None
            mode_machine.__init__()
            ctx = LeadContext(lead_id=lead_id)
            store.save(ctx)
            print(f"\n  ✓ New session started (id: {lead_id})")

            # Re-ask rep online status for the new session —
            # same prompt as startup so each scenario starts clean.
            print()
            rep_input = input("  Is the rep online for this session? (y/n, default n): ").strip().lower()
            rep_online = rep_input == "y"
            print(f"  Rep online: {rep_online}\n")

        # ── assign <name> ─────────────────────────────────────────
        elif cmd_lower.startswith("assign "):
            name = cmd[7:].strip()
            if name:
                ctx = store.get(lead_id)
                if ctx:
                    ctx.assigned_rep = name
                    store.save(ctx)
                    print(f"  ✓ Rep assigned: {name}")
                    print("  Handoff template will now include your name.")
            else:
                print("  ✗ Usage: assign <rep name>")

        # ── score <n> ─────────────────────────────────────────────
        elif cmd_lower.startswith("score "):
            try:
                score = int(cmd[6:].strip())
                if 0 <= score <= 100:
                    ctx = store.get(lead_id)
                    if ctx:
                        ctx.lead_score = score
                        store.save(ctx)
                        print(f"  ✓ Lead score set to {score}.")
                else:
                    print("  ✗ Score must be between 0 and 100.")
            except ValueError:
                print("  ✗ Usage: score <number between 0 and 100>")

        # ── inject <msg> ──────────────────────────────────────────
        elif cmd_lower.startswith("inject "):
            customer_msg = cmd[7:].strip()
            if not customer_msg:
                print("  ✗ Usage: inject <customer message>")
            else:
                print(f"\n  → Injecting customer message: \"{customer_msg}\"")

                result = run_turn(
                    lead_id=lead_id,
                    raw_message=customer_msg,
                    rep_online=rep_online,
                    live_session=live_session,
                    awaiting_approval=awaiting_approval,
                    **shared,
                )

                last_result = result

                # In relay mode, show the draft for approval rather than
                # delivering it — rep must approve first.
                if awaiting_approval and result.customer_message:
                    pending_relay_draft = result.customer_message
                    print(f"\n  📝 RELAY DRAFT (pending your approval):")
                    print(f"  \"{pending_relay_draft}\"")
                    print("  Type 'approve' to deliver, or 'inject' another message.\n")
                else:
                    _print_turn_result(result, label=f"Inject: \"{customer_msg[:40]}\"")

                if result.rep_alert_brief:
                    last_brief = result.rep_alert_brief

        # ── unknown command ───────────────────────────────────────
        else:
            print(f"  ✗ Unknown command: '{cmd}'")
            print("  Available: online | offline | shadow | relay | approve |")
            print("             inject <msg> | context | brief | assign <name> |")
            print("             score <n> | reset | quit")

        _print_rep_prompt(rep_online, mode_machine.get_mode().value)


if __name__ == "__main__":
    main()
