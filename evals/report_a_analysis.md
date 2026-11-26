## 0. Headline (read this first)

**Result: 12 of 12 case/mode tests fail; 18 of 36 perturbation cases fail (146 failed checks).** This is the expected, useful output. Nothing was tuned to pass; no YAML value was edited; no source outside `evals/` was changed.

What the failures are made of (counts from section 1c; classification rules below):
- **Mostly missing features (73 free_text + 38 structured + 6 perturbation).** The scenarios assume signals, triggers and state that the config A code does not have: 34 of 44 distinct signal placeholders have no counterpart; `accountability_moment` and `security_compliance` triggers, `qualification`, `fit_assessment` (low_fit), `next_question_targets`, `context_preserved` and an "unknown" signal state do not exist (see `MAPPING.md`). These are not agent bugs; they are the distance between the golden cases and the current build.
- **Real extraction misses (8 free_text + 10 perturbation).** Mapped concepts that passed with injected signals but not with raw text. Notably: **"Let me talk to someone." is not recognised as a human request in any of the 6 scenarios (PERT-5)** and "I still want to talk to someone" (GD-S6 t6) is not either; the lexical `pricing_discussion` rule fires on the word "budget" inside a hypothetical question (GD-S1 t3); competitor/stakeholder triggers fire on "We use HubSpot" and on "approved" (substring "approve").
- **Decision bugs.** None isolated in the scenario turns once missing features and the YAML's own ambiguities are separated. The perturbation runs show config A **repeats itself**: `guard_against_repetition` swaps in canned loop-breakers on 4 of 5 turns of GD-S3 (t2–t5), 2 turns of GD-S1/S4/S5, and PERT-1 ("That's not what I asked") triggers a loop-breaker in 4 scenarios; the open-intervention follow-up copy repeats verbatim in GD-S6 (known gap POL-26).
- **Invariant violations: 0 of 82 runtime checks per mode; 0 hits in the static audit of 59 templates.** Caution: this is partly because the templates say very little. E.g. all five GD-S4 security questions get generic replies ("I'd love to understand what matters most to you about trust…" or a loop-breaker), which cannot make a certification claim but also never say "a person can tell you". 5 invariant checks are `not_evaluable` (fields absent) and are NOT counted as passes.
- **Bad expectations (inferred): 2 per mode**, both GD-S6 (`mode: RELAY` for a human request; the code gives ALERT with the rep online). Several other expectations are in tension with the code design and are flagged in notes rather than reclassified: GD-S1 t5 (accountability questions are deliberately *not* handoffs, `signal_adapters.py:20-24`) and GD-S5 t2 (pricing interest is an attention trigger that keeps the agent answering, `trigger_catalog.py:50-53`). You decide.

## How failures are classified (all classification labels are **inferred** unless a code cite is given)
| class | rule |
|---|---|
| invariant violation | an invariants_v0.yaml check failed |
| missing feature | the placeholder/field is `DOES NOT EXIST` in `MAPPING.md`, or the turn's inputs cannot be injected in structured mode |
| bad expectation (inferred) | the YAML contradicts the code's design (listed in `evals/mapping.py` `BAD_EXPECTATION`, each with a cite) |
| extraction miss (fails free_text only) | mapped concept; fails on raw text, passes with injected signals (cause may be the extractor OR the raw-text lexical rules in `signal_adapters.py`) |
| decision bug (fails both) / (structured only) | fails with injected signals too, and the placeholders involved all exist |

## Method and limits
- Adapter: `evals/adapter.py` calls `src.orchestrator.run_turn` directly with `build_default_dependencies()` (fresh state per case), `rep_online=True`, no `fit_criteria`. Structured mode replaces the extractor with the mapped `LeadSignals`; because the raw-text lexical rules (pricing/negotiation/commitment/contract) read the message, structured mode sends a neutral string, so those triggers cannot be injected.
- `context_preserved` is checked literally (are the signals retrievable from session state?) and fails because signals are never persisted.
- Perturbations run free_text only, after the full scenario, asserting only deterministic keys. Judge-only keys are unasserted.
- Reproduce: `cd evals && PYTHONDONTWRITEBYTECODE=1 python3 -m pytest test_config_a.py && python3 report_a.py && python3 gen_mapping_md.py`.
