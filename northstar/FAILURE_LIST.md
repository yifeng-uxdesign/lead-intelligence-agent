# Northstar widget: failure list from owner testing

Written 2026-11-18. Source: the owner's feedback from two test rounds (2026-11-16 and 2026-11-17) and the problems they hit getting the code to run. Statuses reflect the branch `claude/bold-heisenberg-lvt224` at commit `eea45e0` (PR #9, open).

**How to read this.** Part 1 lists what the owner reported, in their words, with the cause, the fix and what is still wrong. Part 2 lists failures I found in the same flows that the owner has not yet raised. Part 3 sorts every failure by cause (design, my own mistake, copy, process). Part 4 says how to re-test each fix.

Status words: **Fixed** (verified by tests and in a browser), **Partly fixed** (better, with a named gap), **Open** (not addressed), **Explained** (not a code fault).

---

## 1. Reported by the owner

| ID | What the owner saw | Severity | Cause | Status |
|---|---|---|---|---|
| **F1** | Replies load too fast. All of a reply's bubbles appear at once; they should load one by one at a gentle pace | High | **My mistake.** The pacing step used one short pause for the whole reply, so every bubble landed together | **Fixed** (`4a21e88`) |
| **F2** | A highlighted line ("I'm explaining this before asking you anything, so you know what the questions are for") that the owner could not understand, and did not see why agent behavior should be highlighted | High | The original script had 18 "cue" lines, shown in italics with an orange bar, narrating the agent's own process. They also break my own rules, and I had not audited them | **Fixed** (`e4fe3d4`, `82c0f56`) |
| **F3** | Suggested replies should follow the Pigment example: "Ask me things like" with three questions, plus suggested actions below | Medium | Every suggestion was one row of identical pill buttons; nothing distinguished a question from an action | **Partly fixed** (`e4fe3d4`, `82c0f56`) |
| **F4** | After refreshing `localhost:8000`, the issue still showed, and the owner wondered whether the code had changed | Medium (blocks testing) | The owner's folder was a ZIP snapshot of the branch; a push does not update it. The code was correct on GitHub | **Explained**; the lasting fix is open (see F4 below) |
| **F5** | No pull request was visible, and the code files on GitHub still said "updated 2 weeks ago" | Low | Earlier PRs (#5, #6) were merged within seconds, so the design documents looked fresh on `main` while the code was not on `main`. PR #9 was opened later and is still open | **Explained** |
| **F6** | The handoff said "prototype" and "simulated" ("In this prototype, that path is simulated", "Simulated note filed", "This prototype does not store or send it"). The owner wants it to feel real: the agent stores the customer's information and hands off to live sales reps | High | The original copy disclaimed the demo inside the chat, and there was no rep side at all | **Fixed in the demo's world** (`a4c1ed0`, `bd3e4f8`, `6fd84b5`) |
| **F7** | When the owner interrupted with another question, the agent ignored it and kept following up on the previous one. Example screens: "How is your agent different?" got "A work address looks like name@yourcompany.com", "What happens if it qualifies someone as a good lead…" got "Simulated note filed", "Can I see what evidence the agent uses…" got "The simulated note is the end of this handoff path. Restart anytime." Was it designed this way? | High | **Not on purpose.** The original script understood only each step's own answers plus about 25 shared topics, so anything else counted as "no match" at the current step. The design said to answer the question, but it was never built | **Mostly fixed** (`bd3e4f8`, `a4c1ed0`) |
| **F8** | Whenever the owner asked something outside the scenario scripts, the answer was irrelevant and the agent urged starting over. Is it a design deficit or missing LLM integration? | High | Mainly design (see Part 3): no question handling, no approved answers, no honest "I don't know", and dead-end lines like "Restart anytime" | **Partly fixed** (`bd3e4f8`, `a4c1ed0`) |
| **F9** | Visible in the screenshots, not described by the owner: the first message of S1 ("our sales reps ended up ignoring most of the scores") was treated as a request for a person, which started the whole bad run | High | Two keyword false positives: "sales rep" read as a request for a person, "review" read as a request for reviews | **Fixed for these two** (`a4c1ed0`); a third case is open (R5) |

### Detail on each

**F1. Pace.** *Expected:* each bubble arrives on its own with the typing indicator between. *Now:* one bubble at a time, each after a pause fitted to its length (600 to 1,800 ms). In a browser, your starter's three bubbles arrived at about 1.8, 3.2 and 4.3 seconds; before, all at about 0.7. *Remaining:* the numbers are guesses. A long reply now takes about 4 to 5 seconds, which may still feel slow or fast to you. Tune `pacing` in `config.js`.

**F2. Highlighted narration.** *Now:* 13 of the 18 cue lines are removed (the message beside them already said it) and 5 are folded into the question they explain, for example "Volume tells me whether a conversation like this is likely to be worth your time. Roughly how many inbound inquiries do you get in a typical month?" The highlight style is deleted, and rule R46 and a test now forbid narrating the agent's own process. *Remaining:* none known.

**F3. Suggestions.** *Now:* two groups, "Ask me things like:" (a short list with a × to hide it) and action buttons below. *Remaining:* I wrote the suggestions by hand only for the two main explanation steps (`qualify.explain`, `product.intro`). Every other step uses a rule (a label ending in "?" is a question), so most steps show one or two questions and one or two buttons, and none has been reviewed. The three opening starters are unchanged.

**F4. Local copy did not update.** *Cause:* a downloaded ZIP is a snapshot. *Lasting fix, not done:* a hosted test address that rebuilds on every push. I recommended GitHub Pages (the widget is plain static files) and offered a widget-only workflow that avoids publishing the planning documents. **Waiting on your decision.**

**F5. Pull request and dates.** *State:* PR #9 is open and not merged. Until you merge it, `main` shows the old code and the old dates; the branch shows the new code.

**F6. Real handoff.** *Now:* no "prototype", "simulated" or "no one has been contacted" anywhere in the chat. The conversation and any work email the visitor shares are saved, and a new lead workspace page (`workspace.html`) is the rep's side: who needs a person and why, what is known, the contact, the conversation, and Join, Reply, Hand back, Resolve and Close. The widget shows the person's name and messages, the assistant goes quiet while they are in, and after a resolve the assistant asks whether it is really resolved. *Caveats:* the workspace page is provisional and simple (your own design will replace it); "stored" means saved in the browser; the two pages must be open in the same browser; a rep's message reaches the visitor only while the widget window is open; the page around the widget still says it is a scripted prototype (outside the chat).

**F7. Interruptions.** *Now:* a visitor's question outranks the agent's own pending question. It is answered from 14 draft answers, or declined plainly ("I don't have a reliable answer to that, and I'd rather not guess"), and the visitor can tap "Carry on where we left off". Answering the earlier question afterwards also works. Your three S1 questions now get real answers. *Remaining:* only those 14 topics and the existing steps are covered (see F8, R1 to R3).

**F8. Only predefined questions.** *Honest answer on cause:* about two thirds is design (coverage, question handling, honest gaps) and is fixable without an LLM; the rest is paraphrase understanding and phrasing, where an LLM would help. An LLM could not decide what is true to say; that needs approved product facts either way. *Now:* an honest "no reliable answer" ladder that escalates to a person and never repeats; the dead-end "Restart anytime" lines are gone. *Remaining:* anything outside the 14 topics gets the honest gap, not an answer.

**F9. The false escalation.** *Now:* "our sales reps…" and "reps review leads" no longer trigger the person path or the reviews answer. Measured on the existing conformance cases: no change in either direction.

---

## 2. Found by me in the same flows (not yet raised by the owner)

| ID | Where | What goes wrong | Cause | Status |
|---|---|---|---|---|
| **R1** | S6 | After the visitor asks for a person, the assistant keeps asking qualification questions, and asks the same question twice | The "ask engine" is not built: no "pending decision first" rule, no ask pacing | **Open** |
| **R2** | S10 | Facts given in the first message are ignored (it answers a pilot question), then asks about the pain and outcome the visitor already gave. A work email typed outside an email question is not recognised | No memory of what was said; the email is only read at steps that ask for it | **Open** |
| **R3** | S3 turn 5, S6 turn 5 | "Why wouldn't this be a good fit for us?" and "Is our current process suitable?" get "I don't have a reliable answer" | The agent cannot yet explain suitability from what the visitor said, and no size rule is approved | **Open** |
| **R4** | S2 turns 3 to 5 | The same "Here's what I've heard…" pitch repeats three times and never asks who decides | The repeat guard covers recovery lines, not normal replies | **Open** |
| **R5** | S11, conformance A1 to A4 | Frustration about *other vendors* ("sent me in circles") puts the conversation on hold one turn early | Frustration is not target-aware (the backend is) | **Open** |
| **R6** | S5 | "Do you charge per lead or per user?" gets the generic gap reply instead of the pricing answer; "more expensive than our HubSpot setup?" is read as a setup question | Pricing is matched by a few phrases only | **Open** |
| **R7** | S4 | Two different questions (where is data stored, and what is your security model) get the same privacy reply | One step answers both | **Open** |
| **R8** | All | Internal words still appear in visitor copy: "fit", "evidence", "qualify", "lead", "prospect", "handoff" | The word-list rewrite is not done; three conformance cases require "evidence" or "fit", so it needs your decision | **Open** |
| **R9** | Pacing | The numbers are untested guesses | | **Open** (yours to tune) |
| **R10** | Knowledge | 14 draft answers are live, three of them new product claims (how it differs from a black-box score, what a rep sees, what happens if it qualifies someone wrongly) | Drafts from the repo's own documents, not yet approved by you | **Open** |
| **R11** | Workspace | Provisional; same browser only; no sound or push notification | A stand-in for your workspace design | **Open** |

---

## 3. Sorted by cause

| Cause | Failures |
|---|---|
| **Design deficit** (behavior the design needed and the build lacked) | F2, F3, F7, F8, R1, R2, R3, R4, R5, R6 |
| **My own mistake in the build** | F1 (a single pause per reply), F2 (I did not audit the 18 cue lines against my own rules) |
| **Copy and wording** | F2, F6, R8 |
| **Delivery and process** | F4, F5 |
| **Missing LLM** | The smaller part of F8 and R3: understanding paraphrases and phrasing within approved facts. Nothing in this list needs an LLM to reach a first acceptable state |

## 4. How to re-test each fix

| ID | Try | Expect |
|---|---|---|
| F1 | Click "How does your agent qualify leads?" | Three bubbles arrive one at a time, with the typing dots between, over about 4 seconds |
| F2 | The same screen | No orange-barred italic line anywhere |
| F3 | The same screen | "Ask me things like:" with three questions and a × to hide, then action buttons |
| F6 | Open `index.html` and `workspace.html` in two windows; ask for a person, share a work email; in the workspace click Join conversation and reply | The chat never says prototype or simulated; the lead appears with its reason and email; the person's name and message show in the widget; Resolve brings a check-in |
| F7, F8 | Ask "How is your agent different? I don't want another black-box score." mid-conversation, then "Do you have a mobile app for iOS?" | The first gets an answer and a "Carry on where we left off" button; the second gets the honest "no reliable answer" and a person option; neither says restart |
| F9 | Type "our sales reps ended up ignoring most of the scores" as the first message | A reply about the bad experience, not the person path |

## 5. What I suggest next (your call)

1. **Ask engine** (R1, R2, R3): memory of what was said, "pending decision first", and one question at a time. This is the biggest remaining gap.
2. **Target-aware frustration** (R5), measured on the existing conformance cases.
3. **Your review of the 14 draft answers** (R10), so the agent only states what you have confirmed.
4. **A hosted test address** (F4), so you never download a ZIP again.
5. **The word-list copy pass** (R8), once you decide how to treat the three conformance cases that expect "evidence" or "fit".
