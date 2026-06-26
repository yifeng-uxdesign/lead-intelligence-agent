"""Entry point: delegates to orchestration (customer / rep / mode paths).

Run from the project root (lead_agent/) with:
    python src/main.py

The demo sequence simulates two turns of a realistic Sierra AI prospect
conversation so you can verify the full pipeline end-to-end before running
the test suite.

Turn 1: pricing inquiry with a human request signal
  → Expected: ALERT mode, rep brief generated, no customer message

Turn 2: exploratory follow-up with curiosity signal
  → Expected: AUTONOMOUS mode, customer message generated,
    fit_confirmed reported from fit_criteria evaluation

Pass ``fit_criteria=SIERRA_FIT_CRITERIA`` to run_turn() so fit evaluation
is active in the demo. Omit it in unit/behavior tests that don't need it.
"""

from __future__ import annotations

from src.clients.sierra.fit_criteria import SIERRA_FIT_CRITERIA
from src.orchestrator import build_default_dependencies, run_turn


def _print_result(label: str, result) -> None:
    """Print a turn result in a readable format for CLI inspection."""
    print(f"\n{'─' * 60}")
    print(f"  {label}")
    print(f"{'─' * 60}")
    print(f"  mode            : {result.collaboration_mode}")
    print(f"  trust_state     : {result.trust_state.value}")
    print(f"  trigger         : {result.trigger_type}")
    print(f"  handoff         : {result.handoff_triggered}")
    print(f"  fit_confirmed   : {result.fit_confirmed}")
    print(f"  fit_score       : {result.fit_score}")

    if result.rep_alert_brief:
        brief = result.rep_alert_brief.as_dict()
        print(f"\n  [REP ALERT BRIEF]")
        print(f"  urgency_sla     : {brief['urgency_sla']}")
        print(f"  recommended     : {brief['recommended_action']}")
        print(f"  summary         : {brief['summary'][:80]}...")

    if result.customer_message:
        print(f"\n  [CUSTOMER MESSAGE]")
        print(f"  {result.customer_message}")

    print(f"\n  signals         : {result.lead_signals.as_dict()}")


def main() -> None:
    (
        store,
        signal_extractor,
        customer_engine,
        rep_engine,
        handoff_manager,
        mode_machine,
        _queue,
    ) = build_default_dependencies()

    # Shared kwargs for all turns — avoids repeating the dependency list
    shared = dict(
        store=store,
        signal_extractor=signal_extractor,
        customer_engine=customer_engine,
        rep_engine=rep_engine,
        handoff_manager=handoff_manager,
        mode_machine=mode_machine,
        fit_criteria=SIERRA_FIT_CRITERIA,  # activates fit evaluation in orchestrator
    )

    # ------------------------------------------------------------------
    # Turn 1: pricing inquiry + human request
    # Expected path:
    #   - human_request signal detected → handoff_triggered = True
    #   - rep_online=True → ALERT mode
    #   - rep alert brief generated with urgency_sla from trigger catalog
    #   - no customer message (ALERT suppresses autonomous response)
    # ------------------------------------------------------------------
    result_1 = run_turn(
        lead_id="demo-1",
        raw_message="I'd like to speak to someone about pricing for our team.",
        rep_online=True,
        live_session=False,
        awaiting_approval=False,
        **shared,
    )
    _print_result("Turn 1 — Pricing inquiry + human request", result_1)

    # ------------------------------------------------------------------
    # Turn 2: exploratory follow-up on same lead (tests state continuity)
    # Expected path:
    #   - no handoff signal → AUTONOMOUS mode
    #   - trust state advances from prior context
    #   - customer message generated
    #   - fit_confirmed reported from SIERRA_FIT_CRITERIA evaluation
    #   - fit_score reflects signals extractable from this message alone
    # ------------------------------------------------------------------
    result_2 = run_turn(
        lead_id="demo-1",  # same lead_id — context loaded from store
        raw_message=(
            "Actually, tell me more about how it works. "
            "We use Zendesk and get a lot of repetitive support tickets."
        ),
        rep_online=False,  # rep offline — system stays autonomous
        live_session=False,
        awaiting_approval=False,
        **shared,
    )
    _print_result("Turn 2 — Exploratory follow-up (rep offline)", result_2)

    # ------------------------------------------------------------------
    # Turn 3: frustration signal (tests soul.md priority 2 escalation)
    # Expected path:
    #   - sentiment = "frustration" → handoff_triggered = True
    #   - rep_online=True → ALERT mode
    #   - frustration guard fires: urgency_sla = "immediate"
    # ------------------------------------------------------------------
    result_3 = run_turn(
        lead_id="demo-1",
        raw_message="This is really frustrating — I've been waiting and nobody's followed up.",
        rep_online=True,
        live_session=False,
        awaiting_approval=False,
        **shared,
    )
    _print_result("Turn 3 — Frustration signal (tests escalation guard)", result_3)


if __name__ == "__main__":
    main()
