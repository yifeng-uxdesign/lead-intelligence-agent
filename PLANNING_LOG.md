# Planning Log

A running log of brainstorming, strategy iterations and decisions for the Lead Intelligence Agent
(Northstar frontend demo + `intent-agent-v2` behavior backend).

Newest entries go at the top of **Log**. Never delete an old entry. If a decision changes, add a new
entry that says what changed and why, and mark the old one `superseded`.

---

## Current focus

- Northstar conversational demo: customer-facing UI, scripted scenarios, deterministic behavior rules,
  trust and frustration handling, human handoff scenarios.
- Constraint: the architecture stays deterministic. No LLM provider, external API key or external
  service for now.

## Open questions

- [ ] _(add yours here)_

## Ideas parking lot

- _(unrefined ideas; promote to a log entry when you act on one)_

---

## Log

### 2026-11-12 — Reframe: decision system, not a chatbot

**Context / trigger:** Considered whether the vision is mainly about agent behavior toward human reps, and whether it changes the customer-facing widget.

**Thinking:**
- Partly right. Qualification, routing and handoff do surface to reps. But intake and interpretation happen in the customer conversation, and the trust state machine governs how the agent gathers missing evidence from the customer. So the product is decision-system-centric; the widget is one signal-acquisition channel and reps/CRM are the action side.
- The widget is text-only and scripted, so voice concerns (end-of-speech, pronunciation, expressiveness, barge-in) do not apply yet.
- Checked in code: typing delay is a fixed 720 ms (`northstar/config.js`); input is locked while typing (`engine.js` `send`), so no interruption; the unscripted fallback is canned ("I don't have a scripted path for that yet...", `engine.js`), which matches known role-play issue 3.

**Decision:** Product framing and widget scope recorded in `intent-agent-v2/CLAUDE.md` ("Product framing").

**What would change my mind:** a voice channel, or evidence that customer-facing polish drives qualification outcomes more than routing quality.

**Follow-ups:**
- [ ] Replace the canned fallback with evidence-seeking recovery.
- [ ] Make typing delay depend on reply length (keep reduced-motion behavior).

---

### 2026-11-12 — Product vision: Intelligent Intake & Decision Routing

**Context / trigger:** Writing down what I am trying to achieve with the lead agent product.

**Thinking:**

The product category is **Intelligent Intake & Decision Routing**. This is a potential product category, not an established industry standard.

The five stages:

1. **Intake:** What is being requested?
2. **Interpretation:** What does the request actually need?
3. **Qualification:** Is it qualified, eligible, and suitable?
4. **Matching and routing:** Where should it go, and why?
5. **Disposition and feedback:** What happened after routing?

**Decision:** _(none yet; this is the framing)_

**Open threads** (my notes, not decisions; edit or delete):
- Which stages does the current code cover? Possible mapping to check: `signals/extractor.py` for interpretation, the `clients/sierra` fit criteria for qualification, and `collaboration/` handoff for routing. Stage 5 (disposition and feedback) may be the least built.
- Do roadmap steps 5 to 7 in `intent-agent-v2/CLAUDE.md` (memory, qualification separation, LLM interpretation) line up with these five stages?

**Follow-ups:**
- [ ] Map each stage to current code and demo scenarios, and note the gaps.

---

### 2026-11-12 — Cloud environment for the repo

**Context:** Setting up a Claude Cloud dev environment, with the current priority on the Northstar frontend.

**Findings (from inspecting the repo):**
- `northstar/` is plain static HTML, CSS and ES modules. It has no package manager, no build step and no network calls.
- `intent-agent-v2/` core uses only the Python standard library. Its only declared dependencies were `pytest` and `pytest-cov`.
- `tests/test_phase0_api.py` also needs `fastapi` and `httpx`, which were not declared.
- With those installed: 304 passed, 3 xfailed. The 3 xfails are the known roadmap step-3 autonomy-profile gaps.

**Decisions:**
- Personal environment `lead-intelligence-agent`: limited network, package registries only, no extra hosts, no secrets, no variables.
- Setup script: `pip install pytest pytest-cov fastapi httpx`.
- Added `fastapi` and `httpx` to `intent-agent-v2/requirements.txt`, so the script can later become `pip install -r`.
- Do not allow LLM provider hosts yet. This keeps the deterministic-demo constraint intact.

**Follow-ups:**
- [ ] Switch the saved setup script to `cd intent-agent-v2 && pip install -r requirements.txt` (needs approval).
- [ ] Verify the setup script in a fresh session. It has not been proven yet.

---

## Entry template

```
### YYYY-MM-DD — Title

**Context / trigger:**
**Thinking (options considered, trade-offs):**
**Decision:**
**Why:**
**What would change my mind:**
**Follow-ups:**
```
