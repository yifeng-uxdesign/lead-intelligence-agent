"""Entry point: delegates to orchestration (customer / rep / mode paths)."""

from __future__ import annotations

from src.orchestrator import build_default_dependencies, run_turn


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

    result = run_turn(
        lead_id="demo-1",
        raw_message="I'd like to speak to someone about pricing for our team.",
        store=store,
        signal_extractor=signal_extractor,
        customer_engine=customer_engine,
        rep_engine=rep_engine,
        handoff_manager=handoff_manager,
        mode_machine=mode_machine,
        rep_online=True,
        live_session=False,
        awaiting_approval=False,
    )

    print(f"mode={result.collaboration_mode}")
    print(f"trigger={result.trigger_type} handoff={result.handoff_triggered}")
    if result.rep_alert_brief:
        print("rep_alert:", result.rep_alert_brief.as_dict())
    if result.customer_message:
        print("customer:", result.customer_message)


if __name__ == "__main__":
    main()
