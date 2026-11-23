# Working memory (repo root)

The agent backend has its own notes in `intent-agent-v2/CLAUDE.md`; read that before touching agent code.

## What this project is
A lead-qualification conversational agent (Northstar demo widget + `intent-agent-v2` behavior backend + a rep/lead workspace) built to demonstrate how to **design and evaluate the behavior rules of a customer-facing conversational agent**. The owner's short-term goal is a portfolio demo and case study aimed at conversation-design and conversational-AI roles.

## Standing rules
- **Milestone rule:** whenever a milestone is reached (an eval iteration, a decision, a new deliverable, a plan change), update `evals/portfolio/CASE_STUDY.md` (its "Update log", status, numbers and artifact index) and `TASKS.md`, and add or refresh the matching design artifact (the canvas listed in the case study). Do this in the same turn as the milestone.
- **Label every claim** as from code (file:line), from the owner's docs, from the eval, proposed, or inferred. Never invent failures; the owner's failure list (`evals/inputs/FAILURE_LIST_*.md`) is theirs and incomplete.
- Do not edit the owner's existing files to make a result look better. Put new drafts in new files; never change expected values in the eval YAML.
- Decisions that belong to the owner are recorded in `evals/PLAN_*` Open Questions; do not assume answers.
- Changes to agent source (`intent-agent-v2/`) need the owner's go-ahead per iteration, must keep the 307 tests, conformance and held-out set from regressing, and are logged in `evals/ITERATIONS.md`.
- Do not claim LLM work that has not been done; the LLM comes after the rules (owner decision, 2026-11-22).

## Where things are
- `evals/` eval runner, reports, plans, drafts, inputs, iteration snapshots. Start at `evals/portfolio/CASE_STUDY.md`.
- `PLANNING_LOG.md` product decision log (newest first; never delete entries).
- `northstar/` scripted widget demo, conversation design docs, ICP and knowledge-base drafts.
- Design canvas (visual maps and timeline): https://claude.ai/artifact/A715tTjGBPrQw5duzggCRT (private to the owner).
