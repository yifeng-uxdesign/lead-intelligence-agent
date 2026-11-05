# Lead Intelligence Agent (intent-agent-v2) — working notes for Claude Code

Portfolio-centerpiece B2B sales-qualification agent. Python backend (this repo) + a static JS "Northstar" widget demo (separate repo/folder). Goal: make the deterministic behavior layer correct and *measurable* before adding an LLM, so the demo highlights the behavior-layer design.

## Architecture rule (do not violate)
- **Deterministic Python owns decisions**: trust state, autonomy, handoff, authorization, delivery.
- **LLM (later) only interprets** into a frozen label set, and **phrases** within an approved response contract. A deterministic validator checks outputs.
- Constitution: `src/core/soul.md`. Existing soul-compliance tests must keep passing.

## Current state
- Phase 0 done: target-aware frustration, explicit human requests, offline handoff queuing, ALERT holding copy, RELAY approval (`/rep/approve`), backend-owned authorization (`/chat` takes only lead_id+message; rep endpoints need `X-Rep-Token` / env `LEAD_AGENT_REP_TOKEN`, fail closed 503), loop guard, interpretation-failure handling.
- Delivery matrix (`src/collaboration/delivery_policy.py`): AUTONOMOUS→delivered; ALERT→holding; SHADOW→rep suggestion; RELAY→pending approval; open human intervention overrides to holding; unknown mode fails closed.
- Conformance suite (`conformance/`, `tests/test_conformance.py`): 66 cases, two layers. Policy layer (hand-labeled signals) must reach 100%; understanding layer (raw text) has a recorded baseline the LLM must beat.
- Decision trace (`src/domain/decision_trace.py`): one per turn on `OrchestrationResult.decision_trace`, last 50 persisted in metadata, rep-only via `GET /context` (`decision_trace`). Records signals, every trigger hit (class + evidence), intervention action, rep-notified reason, mode reason, delivery reason, response source, outcome.
- Trigger taxonomy (`TriggerClass` / `TRIGGER_CLASS` / `TRIGGER_PRECEDENCE` in `trigger_catalog.py`): intervention = human_request, frustration (agent/unspecified), commitment_demand, pricing_negotiation, contract_legal_ask → open intervention + hold; attention = strong_buying_signal, pricing_discussion (interest) → rep notified, agent answers; context = competitor, stakeholder → rep notified once per lead (`rep_notices`), agent answers. New intervention detectors are narrow lexical rules in `signal_adapters.py` (replace in step 7).
- Tests: `python3 -m pytest -q` → 304 passed, 3 xfailed (the xfails are the roadmap step-3 gaps: autonomy profiles).
- Conformance observer: `human_path` = the customer is offered a person (taxonomy.json), not "rep was notified". The backend observer used to conflate them; fixed in its own commit with baselines recorded before/after (backend false_escalation 0.189→0.038 is measurement only; on a consistent measure, steps 1–2 took it 0.170→0.038).

- Held-out set (`conformance/heldout.json`, `python3 conformance/run_heldout.py`): 22 paraphrases of the intervention boundary, report-only, never tune rules to it. Lexical rules today: **1/14 interventions caught (0/12 negotiation/commitment/contract), 8/8 non-interventions correct** — the step-2 detectors are overfit to `cases.json` phrasings. Drafted by the same agent as the rules (not blind); owner should add phrasings. The LLM interpreter (step 7) is judged on this set.

## Workflow for every roadmap step
1. Make the change.
2. Delete the fixed cases from `conformance/known_gaps.json` (strict xfail turns red when a gap starts passing).
3. `./conformance/run_all.sh <path-to-widget-dir> --record` (needs Node; widget dir is `northstar/`), commit the new baselines only if metrics did not regress.
4. Never weaken `cases.json` to make a number pass; changing it changes `cases_hash` and requires re-recording baselines.

## Roadmap (in order)
1. ~~Decision trace (why each turn was held/answered/notified).~~ done
2. ~~Trigger taxonomy~~ done: context / attention / intervention. Closed gaps POL-07, 08, 09, 11, 12, 13, 14. Fixes my Phase 0 regression: holding copy announces a handoff on buying signals before fit is confirmed.
3. Autonomy profiles incl. `restricted` (open gaps POL-20, 21, 26 in `known_gaps.json`, tagged step 3).
4. Response contract + deterministic validator; reuse widget copy as the approved-response library.
5. Conversation memory (facts known, questions asked) — stops re-asking.
6. Phase 1-lite qualification separation: generic fit engine, Sierra criteria frozen by golden tests, per-client signal mapping (`_prospect_signals_from_lead` still maps Sierra keys), four-outcome result, Northstar default in API with empty criteria.
7. LLM interpretation (frozen label set from `conformance/taxonomy.json`), then LLM response generation. Re-measure after each.

**LLM gate**: policy cases 100%, understanding baseline recorded, held-out set scored, trace covers decisions, validator passes adversarial tests, label set frozen.

## Decisions assumed (owner has not explicitly confirmed — ask before changing)
- D1 buying/pricing interest before fit → alert rep, keep fit check, don't hold.
- D2 after a human request → restricted autonomy until a rep resolves.
- D3 approval gate with rep offline → restricted, never unrestricted.
- D4 interventions = human request, agent-directed frustration, commitment/accountability demand, pricing negotiation, contract/legal ask. Competitor/stakeholder = context.
- Open: RELAY with rep offline; SHADOW withholds agent replies (currently implemented as withheld).

## Role-play issues being fixed
1. Agent over-hands-off when the prospect mentions their own team's/vendor's frustration.
2. Agent doesn't recognize when accountability requires a human.
3. Canned "explore or restart" fallbacks; no real understanding of nuance.

## Before any public hosted demo
Durable storage, per-lead locking, restrict CORS (currently "*"), rate limits, session ownership / lead_id spoofing protection.

## Gotchas
- Importing the widget in Node needs a throwaway copy with `package.json {"type":"module"}` (run_all.sh does this).
- Stub extractor failure falls back to the real rule-based extractor by design (POL-23).
- `src/rep_chat (1).py` has a space/paren in its name; rename when convenient.
