"""Interactive terminal demo — type messages and see the full agent pipeline.

Run from project root:
    python3 -m src.chat

This simulates a real conversation turn by turn so you can observe:
- How trust state evolves across turns
- When handoff triggers fire
- What the customer sees vs what a rep would see
- Whether fit evaluation changes as signals accumulate

Type 'quit' or 'exit' to end the session.
Type 'state' to print the current LeadContext snapshot.
Type 'reset' to start a new conversation.
"""

from __future__ import annotations

import sys
from src.clients.sierra.fit_criteria import SIERRA_FIT_CRITERIA
from src.orchestrator import build_default_dependencies, run_turn


_DIVIDER = "─" * 60


def _print_turn(result, turn_number: int) -> None:
    print(f"\n{_DIVIDER}")
    print(f"  Turn {turn_number}")
    print(_DIVIDER)
    print(f"  trust state    : {result.trust_state.value}")
    print(f"  mode           : {result.collaboration_mode}")
    print(f"  handoff        : {result.handoff_triggered} "
          f"({result.trigger_type})")
    print(f"  fit confirmed  : {result.fit_confirmed}")
    print(f"  fit score      : {result.fit_score}")
    print(f"  sentiment      : {result.lead_signals.sentiment}")
    print(f"  intent         : {result.lead_signals.intent}")

    if result.rep_alert_brief:
        b = result.rep_alert_brief.as_dict()
        print(f"\n  ⚠️  REP ALERT")
        print(f"  urgency        : {b['urgency_sla']}")
        print(f"  action         : {b['recommended_action']}")
        print(f"  summary        : {b['summary'][:100]}")

    if result.customer_message:
        print(f"\n  🤖 Agent:")
        print(f"  {result.customer_message}")

    print()


def _print_context(result) -> None:
    ctx = result.context
    print(f"\n{_DIVIDER}")
    print("  LeadContext snapshot")
    print(_DIVIDER)
    print(f"  lead_id        : {ctx.lead_id}")
    print(f"  customer_state : {ctx.customer_state}")
    print(f"  collaboration  : {ctx.collaboration_mode}")
    print(f"  sentiment      : {ctx.sentiment}")
    print(f"  lead_score     : {ctx.lead_score}")
    print(f"  rep_online     : {ctx.rep_online}")
    print(f"  assigned_rep   : {ctx.assigned_rep}")
    print(f"  handoff_queue  : {len(ctx.handoff_queue)} events")
    summary = ctx.conversation_summary
    if summary:
        print(f"  summary        : {summary[:120]}...")
    print()


def main() -> None:
    print(f"\n{'═' * 60}")
    print("  Lead Agent — Interactive Terminal Demo")
    print("  Client: Sierra AI — agentic customer service")
    print(f"{'═' * 60}")
    print("  Commands: 'state' = show context | 'reset' = new chat")
    print("            'quit' or 'exit' = end session")
    print(f"{'═' * 60}\n")

    # Ask rep status upfront — simulates real session configuration
    rep_input = input("  Is the rep online? (y/n, default n): ").strip().lower()
    rep_online = rep_input == "y"
    print(f"  Rep online: {rep_online}\n")

    (
        store,
        signal_extractor,
        customer_engine,
        rep_engine,
        handoff_manager,
        mode_machine,
        _queue,
    ) = build_default_dependencies()

    lead_id = "chat-session-1"
    turn_number = 0
    last_result = None

    shared = dict(
        store=store,
        signal_extractor=signal_extractor,
        customer_engine=customer_engine,
        rep_engine=rep_engine,
        handoff_manager=handoff_manager,
        mode_machine=mode_machine,
        fit_criteria=SIERRA_FIT_CRITERIA,
    )

    print("  You: ", end="", flush=True)

    for line in sys.stdin:
        message = line.strip()

        if not message:
            print("  You: ", end="", flush=True)
            continue

        if message.lower() in ("quit", "exit"):
            print("\n  Session ended.\n")
            break

        if message.lower() == "reset":
            lead_id = f"chat-session-{turn_number + 1}"
            turn_number = 0
            last_result = None
            mode_machine.__init__()
            print(f"\n  New session started (id: {lead_id})")
            print()
            rep_input = input("  Is the rep online? (y/n, default n): ").strip().lower()
            rep_online = rep_input == "y"
            print(f"  Rep online: {rep_online}\n")

        if message.lower() == "state":
            if last_result:
                _print_context(last_result)
            else:
                print("  No turns completed yet.\n")
            print("  You: ", end="", flush=True)
            continue

        turn_number += 1

        result = run_turn(
            lead_id=lead_id,
            raw_message=message,
            rep_online=rep_online,
            live_session=False,
            awaiting_approval=False,
            **shared,
        )

        last_result = result
        _print_turn(result, turn_number)
        print("  You: ", end="", flush=True)


if __name__ == "__main__":
    main()
