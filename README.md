# Lead Intelligence Agent

A trust-first lead agent that helps prospects make confident decisions while coordinating with human sales reps. The agent manages collaboration modes, trust states, signal extraction, and handoff triggers through a layered architecture.

## Project structure

```
intent-agent-v2/          # Active codebase
├── src/
│   ├── orchestrator.py   # Turn orchestration pipeline
│   ├── customer_layer/   # Trust, behavior, response policy
│   ├── rep_layer/        # Rep alerts, drafts, assist engine
│   ├── collaboration/    # Mode & handoff state machines
│   ├── domain/           # Triggers, session state
│   └── clients/sierra/   # Example client config & fit criteria
├── tests/                # Unit, behavior, and persona tests
├── requirements.txt
└── pytest.ini
```

## Quick start

```bash
cd intent-agent-v2
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the demo pipeline
python main.py

# Run tests
pytest
```

## Testing

| Marker    | Scope                                      | Command              |
|-----------|--------------------------------------------|----------------------|
| `unit`    | State machines, triggers, handoff logic    | `pytest -m unit`     |
| `behavior`| soul.md compliance checks                  | `pytest -m behavior` |
| `persona` | End-to-end prospect conversation sims      | `pytest -m persona`  |

See `intent-agent-v2/tests/TEST_PLAN.md` for the full test strategy.

## Design principles

The agent's behavior is governed by `src/core/soul.md` — a value constitution that prioritizes trust over conversion. All behavior rules, state machines, and prompt strategies are downstream of that document.
