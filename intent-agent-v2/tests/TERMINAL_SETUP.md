# Lead Agent — Complete Terminal Setup & Test Guide
# ─────────────────────────────────────────────────
# Run every command from the lead_agent/ project root
# unless a step says otherwise.
# ─────────────────────────────────────────────────


# ══════════════════════════════════════════════════
# STEP 0 — Open terminal in Cursor
# ══════════════════════════════════════════════════

# Press: Cmd + ` (backtick) on Mac
# Press: Ctrl + ` (backtick) on Windows / Linux
#
# Confirm you are in the right folder:
pwd
# Should print something like: /Users/yourname/lead_agent
#
# If not, navigate there:
cd path/to/lead_agent


# ══════════════════════════════════════════════════
# STEP 1 — Find your Python command
# ══════════════════════════════════════════════════
#
# "python: command not found" means macOS uses python3.
# Run this to confirm which command works on your machine:

python3 --version
# If this prints Python 3.x.x → use python3 everywhere below

# If python3 also fails, Python is not installed.
# Install it from: https://www.python.org/downloads/
# Or with Homebrew: brew install python3

# Quick reference — replace PYTHON with what works for you:
#   Mac (most common) : python3
#   Windows           : python  or  py
#   Linux             : python3


# ══════════════════════════════════════════════════
# STEP 2 — Create virtual environment
# ══════════════════════════════════════════════════
#
# This keeps project dependencies isolated from your system.
# Run once per project — not every time.

python3 -m venv venv

# Activate the virtual environment:

# Mac / Linux:
source venv/bin/activate

# Windows (Command Prompt):
# venv\Scripts\activate.bat

# Windows (PowerShell):
# venv\Scripts\Activate.ps1

# You should see (venv) appear at the start of your terminal prompt:
# (venv) yourname@machine lead_agent %
#
# If PowerShell blocks activation with a permissions error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then try activating again.


# ══════════════════════════════════════════════════
# STEP 3 — Install dependencies
# ══════════════════════════════════════════════════

pip install pytest pytest-cov

# Confirm installation:
pytest --version
# Should print: pytest 8.x.x


# ══════════════════════════════════════════════════
# STEP 4 — Move legacy files out of root
# ══════════════════════════════════════════════════
#
# These files are from Iteration 0 and are no longer active.
# Moving them prevents accidental imports during testing.

mkdir -p _legacy
mv utils.py _legacy/utils_legacy.py
mv policy.py _legacy/policy_legacy.py
mv guardrails.py _legacy/guardrails_legacy.py
mv prompt.py _legacy/prompt_legacy.py
mv config.py _legacy/config_legacy.py
mv main.py _legacy/main_legacy_fastapi.py

# If a file doesn't exist, mv will show an error — that's fine, skip it.
# Confirm only active files remain at root:
ls
# Should show: _legacy/  src/  tests/  pytest.ini  requirements.txt  venv/


# ══════════════════════════════════════════════════
# STEP 5 — Create __init__.py files
# ══════════════════════════════════════════════════
#
# Python needs these files to treat each folder as a package
# so imports like "from src.orchestrator import ..." work correctly.
# Run the whole block at once — paste all lines together.

touch src/__init__.py
touch src/core/__init__.py
touch src/customer_layer/__init__.py
touch src/rep_layer/__init__.py
touch src/collaboration/__init__.py
touch src/domain/__init__.py
touch src/signals/__init__.py
touch src/application/__init__.py
touch src/clients/__init__.py
touch src/clients/sierra/__init__.py
touch tests/__init__.py

# Confirm they were created:
find src -name "__init__.py"
# Should list one __init__.py per folder above


# ══════════════════════════════════════════════════
# STEP 6 — Confirm project structure
# ══════════════════════════════════════════════════
#
# Your project root should look like this before running tests:
#
# lead_agent/
# ├── _legacy/
# ├── pytest.ini                  ← must exist
# ├── requirements.txt            ← must exist
# ├── src/
# │   ├── __init__.py
# │   ├── orchestrator.py
# │   ├── core/
# │   │   ├── __init__.py
# │   │   ├── lead_context.py
# │   │   ├── memory_store.py
# │   │   └── handoff_queue.py
# │   ├── customer_layer/
# │   │   ├── __init__.py
# │   │   ├── behavior_engine.py
# │   │   └── trust_state_machine.py
# │   ├── rep_layer/
# │   │   ├── __init__.py
# │   │   └── rep_assist_engine.py
# │   ├── collaboration/
# │   │   ├── __init__.py
# │   │   ├── mode_state_machine.py
# │   │   └── handoff_manager.py
# │   ├── domain/
# │   │   ├── __init__.py
# │   │   ├── trigger_catalog.py
# │   │   └── session_state.py
# │   ├── signals/
# │   │   ├── __init__.py
# │   │   └── extractor.py
# │   ├── application/
# │   │   ├── __init__.py
# │   │   └── signal_adapters.py
# │   └── clients/
# │       ├── __init__.py
# │       └── sierra/
# │           ├── __init__.py
# │           ├── product_context.md
# │           └── fit_criteria.py
# ├── tests/
# │   ├── __init__.py
# │   ├── test_trust_state_transitions.py
# │   ├── test_collaboration_mode_transitions.py
# │   ├── test_trigger_catalog.py
# │   ├── test_handoff_triggers_and_sla.py
# │   ├── test_behavior_soul_compliance.py
# │   └── test_persona_conversations.py
# └── venv/                       ← never commit this

# Quick check — confirm pytest.ini exists:
cat pytest.ini
# Should print the [pytest] config block


# ══════════════════════════════════════════════════
# STEP 7 — Run the demo first (smoke test)
# ══════════════════════════════════════════════════
#
# Before running the test suite, verify the full pipeline
# works end-to-end with the CLI demo.

python3 src/main.py

# Expected output (approximate):
#
# ────────────────────────────────────────────────────────────
#   Turn 1 — Pricing inquiry + human request
# ────────────────────────────────────────────────────────────
#   mode            : ALERT
#   trust_state     : AWARENESS
#   trigger         : human_request
#   handoff         : True
#   fit_confirmed   : False
#   fit_score       : ...
#   [REP ALERT BRIEF]
#   urgency_sla     : 15 min
#   ...
#
# If you see ImportError or ModuleNotFoundError, go to
# TROUBLESHOOTING at the bottom of this file.


# ══════════════════════════════════════════════════
# STEP 8 — Run tests layer by layer
# ══════════════════════════════════════════════════
#
# Always run in this order: unit → behavior → persona
# Fix failures at each layer before moving to the next.
# A failing unit test that also breaks a persona test
# produces noise — fix the foundation first.


# ── Layer 1: Unit tests ───────────────────────────
# Tests state machine logic, trigger catalog,
# and handoff priority ordering.

pytest tests/test_trust_state_transitions.py -v
pytest tests/test_collaboration_mode_transitions.py -v
pytest tests/test_trigger_catalog.py -v
pytest tests/test_handoff_triggers_and_sla.py -v

# Run all unit tests together:
pytest tests/test_trust_state_transitions.py \
       tests/test_collaboration_mode_transitions.py \
       tests/test_trigger_catalog.py \
       tests/test_handoff_triggers_and_sla.py -v


# ── Layer 2: Behavior tests ───────────────────────
# Tests soul.md compliance in agent output.
# Only run after all unit tests pass.

pytest tests/test_behavior_soul_compliance.py -v


# ── Layer 3: Persona tests ────────────────────────
# Tests realistic conversation simulations.
# Only run after behavior tests pass.

pytest tests/test_persona_conversations.py -v


# ── Full test suite with coverage ─────────────────

pytest tests/ --cov=src --cov-report=term-missing

# Coverage report shows which lines in src/ are not
# covered by any test. Aim for >80% on core files:
#   src/customer_layer/behavior_engine.py
#   src/customer_layer/trust_state_machine.py
#   src/rep_layer/rep_assist_engine.py
#   src/collaboration/mode_state_machine.py


# ── Useful single-test commands ───────────────────

# Run one specific test by name:
pytest tests/test_trust_state_transitions.py::test_awareness_to_curiosity_on_explore_intent -v

# Run tests matching a keyword:
pytest tests/ -k "frustration" -v
pytest tests/ -k "decision_ready" -v
pytest tests/ -k "persona" -v

# Run and stop at first failure:
pytest tests/ -x -v

# Re-run only the tests that failed last time:
pytest tests/ --lf -v

# Run without coverage (faster for quick checks):
pytest tests/ -v --no-cov


# ══════════════════════════════════════════════════
# STEP 9 — Reading test output
# ══════════════════════════════════════════════════
#
# PASSED  → test passed, constraint is enforced
# FAILED  → test failed, read the assertion message
# ERROR   → test could not run (usually an import error)
#
# Example of a clean run:
#
# tests/test_trust_state_transitions.py::test_awareness_to_curiosity  PASSED
# tests/test_trust_state_transitions.py::test_decision_ready_does_not_commit_on_objection  FAILED
#
# AssertionError: DECISION_READY must not advance to COMMITMENT when
# objection=True. Add a signal check to the DECISION_READY branch.
#
# → Read the assertion message — it tells you exactly which file
#   and which method to fix. Then re-run that file only.


# ══════════════════════════════════════════════════
# DAILY WORKFLOW (after initial setup is done)
# ══════════════════════════════════════════════════
#
# Every time you open a new terminal session:

source venv/bin/activate          # Mac/Linux — re-activate venv
# venv\Scripts\activate           # Windows

# Then run tests normally:
pytest tests/ -v


# ══════════════════════════════════════════════════
# TROUBLESHOOTING
# ══════════════════════════════════════════════════

# ── "python: command not found" ──────────────────
# Use python3 instead of python on Mac:
python3 --version
python3 -m venv venv
python3 src/main.py

# ── "pytest: command not found" ──────────────────
# venv is not activated. Run:
source venv/bin/activate          # Mac/Linux
# Then retry: pytest --version

# ── "ModuleNotFoundError: No module named 'src'" ─
# Cause 1: pytest.ini is missing or wrong location
cat pytest.ini                    # must be at lead_agent/ root
# Cause 2: running pytest from wrong directory
pwd                               # must be lead_agent/
# Cause 3: missing __init__.py files
find src -name "__init__.py"      # re-run Step 5 if empty

# ── "ModuleNotFoundError: No module named 'src.clients.sierra'" ──
# fit_criteria.py or __init__.py missing in clients/sierra/
ls src/clients/sierra/
# Must show: __init__.py  fit_criteria.py  product_context.md
touch src/clients/sierra/__init__.py

# ── "ImportError: cannot import name 'X' from 'src.Y'" ──
# The file exists but the function/class name doesn't match.
# Check the exact name in the source file:
grep -n "def X\|class X" src/Y.py

# ── Tests pass but main.py throws an error ───────
# main.py imports SIERRA_FIT_CRITERIA — confirm fit_criteria.py is in place:
ls src/clients/sierra/fit_criteria.py

# ── Coverage report shows 0% on a file ───────────
# That file has no tests importing it yet.
# Check which test file should cover it and verify the import path.

# ── Windows: venv activation blocked by PowerShell ──
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then: venv\Scripts\Activate.ps1
