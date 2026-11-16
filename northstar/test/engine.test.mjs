import test from "node:test";
import assert from "node:assert/strict";
import { createConversation, paceMs, pickRecovery } from "../engine.js";
import { WIDGET_CONFIG } from "../config.js";
import { NODES, RECOVERY, REPAIR } from "../scenarios.js";

const fast = (ms = 5) => createConversation({ config: WIDGET_CONFIG, onTypingDelay: () => ms });
const assistantTexts = (conv) => conv.getState().messages.filter((m) => m.role === "assistant").map((m) => m.text);
const adjacentRepeats = (texts) => texts.filter((t, i) => i && t === texts[i - 1]);
const NONSENSE = ["zzz qqq xxx", "qqq zzz www", "xxx www zzz", "www xxx qqq", "yyy ttt rrr", "ttt rrr yyy"];

test("paceMs grows with length and stays inside its bounds", () => {
  assert.equal(paceMs(0, WIDGET_CONFIG.pacing), WIDGET_CONFIG.pacing.minMs);
  assert.ok(paceMs(100, WIDGET_CONFIG.pacing) > paceMs(40, WIDGET_CONFIG.pacing));
  assert.equal(paceMs(100000, WIDGET_CONFIG.pacing), WIDGET_CONFIG.pacing.maxMs);
  assert.equal(paceMs(10, { minMs: 1, baseMs: 0, perCharMs: 2, maxMs: 99 }), 20);
});

test("pickRecovery plays tiers in order, then cycles without ever repeating the last text", () => {
  const tiers = [{ text: "a" }, { text: "b" }, { text: "c", choices: [{ id: "x" }] }];
  const alts = ["alt1", "alt2"];
  assert.deepEqual([0, 1, 2].map((i) => pickRecovery(tiers, i, "", alts).text), ["a", "b", "c"]);
  assert.equal(pickRecovery(tiers, 2, "", alts).final, true);
  assert.equal(pickRecovery(tiers, 1, "", alts).final, false);
  let last = "c";
  for (let i = 3; i < 12; i++) {
    const p = pickRecovery(tiers, i, last, alts);
    assert.notEqual(p.text, last, `idx ${i} repeated the previous reply`);
    assert.deepEqual(p.choices, [{ id: "x" }]); // the last tier's suggested replies stay
    last = p.text;
  }
  assert.notEqual(pickRecovery([{ text: "same" }], 0, "same", alts).text, "same");
});

test("recovery copy follows the word list and never claims a person has been told or contacted", () => {
  const repairTexts = ["refusal", "unknown", "misunderstood", "straight", "why"].flatMap((k) => [
    ...REPAIR[k].tiers.map((t) => t.text),
    ...Object.values(REPAIR[k].byNode || {}),
  ]);
  const texts = [...RECOVERY.alternates, ...repairTexts, ...Object.values(RECOVERY.groups).flatMap((g) => g.tiers.map((t) => t.text))];
  assert.ok(texts.length > 80);
  for (const t of texts) {
    assert.doesNotMatch(t, /\b(leads?|prospects?|qualif\w*|evidence|simulated|prototype|hand ?off|fit)\b/i, `word list: ${t}`);
    assert.doesNotMatch(t, /been told|been contacted|is joining|will join|has joined|notified/i, `unearned claim: ${t}`);
  }
});

test("every grouped node exists, and its own fallback equals tier 1 (so the conformance observer keeps counting it)", () => {
  for (const [nodeId, groupId] of Object.entries(RECOVERY.nodeGroup)) {
    assert.ok(NODES[nodeId], `missing node ${nodeId}`);
    assert.ok(RECOVERY.groups[groupId], `missing group ${groupId}`);
    assert.equal(NODES[nodeId].fallback.text, RECOVERY.groups[groupId].tiers[0].text);
  }
});

test("ladder: three misses escalate, the third moves the conversation on, and no reply repeats", async () => {
  const c = fast();
  await c.startFrom("curious"); // curious.business
  assert.equal(c.getState().nodeId, "curious.business");
  await c.send(NONSENSE[0]);
  const t1 = assistantTexts(c).at(-1);
  await c.send(NONSENSE[1]);
  const t2 = assistantTexts(c).at(-1);
  assert.equal(c.getState().nodeId, "curious.business"); // still asking, not moved on
  await c.send(NONSENSE[2]);
  assert.equal(c.getState().nodeId, "curious.process"); // tier 3 releases the visitor
  assert.notEqual(t1, t2);
  assert.deepEqual(adjacentRepeats(assistantTexts(c)), []);
});

test("a fit question is only marked answered when the ladder releases the visitor", async () => {
  const c = fast();
  await c.startFrom("promising");
  await c.choose("ask"); // first fit question
  const first = c.getState().nodeId;
  assert.ok(first.startsWith("promising."));
  await c.send(NONSENSE[0]);
  await c.send(NONSENSE[1]);
  assert.equal(c.getState().nodeId, first);
  await c.send(NONSENSE[2]);
  assert.notEqual(c.getState().nodeId, first); // moved to the next question or the gate
});

test("tier 3 can offer its own suggested replies, and they work", async () => {
  const c = fast();
  await c.startFrom("hesitant"); // hesitant.ack
  for (const m of NONSENSE.slice(0, 3)) await c.send(m);
  assert.deepEqual(c.getState().choices.map((x) => x.id), ["person", "stop"]);
  await c.choose("person");
  assert.equal(c.getState().nodeId, "intervention.explain");
});

test("minimal replies (L1-style) never produce the same reply twice in a row", async () => {
  const c = fast();
  for (const m of ["ok", "hmm", "maybe", "not sure", "what else", "sure", "go on", "ok", "hm"]) await c.send(m);
  assert.deepEqual(adjacentRepeats(assistantTexts(c)), []);
});

test("holding for a person varies its lines and keeps holding", async () => {
  const c = fast();
  await c.send("This is so frustrating, I'm fed up and going in circles");
  assert.equal(c.getState().nodeId, "alert.handoff");
  for (const m of ["why", "hello?", "what does it cost", "anyone there", "ok"]) await c.send(m);
  const texts = assistantTexts(c);
  assert.deepEqual(adjacentRepeats(texts), []);
  assert.ok(["alert.hold", "alert.handoff"].includes(c.getState().nodeId));
});

test("queue: the visitor can keep typing; messages wait in order, up to two; nothing is dropped", async () => {
  const c = fast(30);
  const p1 = c.send("Hello there");
  assert.equal(c.getState().typing, true);
  assert.equal(c.canSend(), true);
  assert.equal(await c.send("How does it work?"), true); // accepted at once, and waiting behind the first
  assert.equal(c.getState().queued, 1);
  assert.equal(await c.send("And what about privacy?"), true);
  assert.equal(c.getState().queued, 2);
  assert.equal(c.canSend(), false);
  assert.equal(await c.send("one too many"), false); // full queue refuses, and says so
  const userNow = c.getState().messages.filter((m) => m.role === "user");
  assert.deepEqual(userNow.map((m) => m.text), ["Hello there", "How does it work?", "And what about privacy?"]);
  assert.deepEqual(userNow.map((m) => !!m.queued), [false, true, true]);
  await p1; // resolves once the first reply and the queued ones have been answered
  await new Promise((r) => setTimeout(r, 200));
  const s = c.getState();
  assert.equal(s.typing, false);
  assert.equal(s.queued, 0);
  assert.equal(c.canSend(), true);
  assert.equal(s.messages.filter((m) => m.queued).length, 0);
  assert.ok(s.messages.filter((m) => m.role === "assistant").length >= 4); // welcome + one answer to each of three
});

test("a request for a person typed mid-reply is still handled", async () => {
  const c = fast(30);
  const p = c.send("Hello there");
  c.send("I want to speak to a real person please");
  await p;
  await new Promise((r) => setTimeout(r, 200));
  assert.ok(assistantTexts(c).some((t) => /person should help/i.test(t) || /A person is the right next step/i.test(t)));
  assert.equal(c.getState().nodeId.startsWith("intervention."), true);
});

test("frustration typed mid-reply is still handled and puts the conversation on hold", async () => {
  const c = fast(30);
  const p = c.send("Hello there");
  c.send("This is useless, I'm fed up");
  await p;
  await new Promise((r) => setTimeout(r, 200));
  assert.equal(c.getState().nodeId, "alert.handoff");
});

test("restart drops the reply in flight and clears the queue", async () => {
  const c = fast(40);
  const p = c.send("Hello there");
  c.send("How does it work?");
  c.restart();
  await p;
  await new Promise((r) => setTimeout(r, 150));
  const s = c.getState();
  assert.equal(s.messages.length, 1); // only the welcome message
  assert.equal(s.typing, false);
  assert.equal(s.queued, 0);
  assert.equal(c.canSend(), true);
  await c.send("Hello again"); // the new thread works
  assert.ok(c.getState().messages.length >= 3);
});

test("typing delay is longer for longer replies, and the host can override it (reduced motion)", async () => {
  const seen = [];
  const c = createConversation({ config: WIDGET_CONFIG, onTypingDelay: ({ chars, ms }) => (seen.push({ chars, ms }), 1) });
  await c.send("ok"); // short reply (quiet.patient)
  await c.send("Tell me more about how Northstar works"); // longer reply (product.intro)
  assert.ok(seen.length >= 2);
  const [short, long] = [seen[0], seen[1]];
  assert.ok(long.chars > short.chars && long.ms > short.ms, JSON.stringify(seen));
});

// ---- repair: talking about the conversation itself ----
const toFirstFitQuestion = async (c) => { await c.startFrom("promising"); await c.choose("ask"); return c.getState().nodeId; };

test("repair: \"why do you need to know that\" gives the reason for the current question, then escalates without repeating", async () => {
  const c = fast();
  const q = await toFirstFitQuestion(c);
  await c.send("Why do you need to know that?");
  const r1 = assistantTexts(c).at(-1);
  assert.equal(r1, REPAIR.why.byNode[q]);
  assert.equal(c.getState().nodeId, q); // still on the question: the visitor can answer it now
  await c.send("Why do you need to know that?");
  const r2 = assistantTexts(c).at(-1);
  assert.notEqual(r2, r1);
});

test("repair: a refusal is accepted, the question is closed, and the conversation moves on", async () => {
  const c = fast();
  const q = await toFirstFitQuestion(c);
  const before = assistantTexts(c).length;
  await c.send("I don't want to share that");
  const said = assistantTexts(c).slice(before);
  assert.match(said[0], /completely fine|leave that out/i);
  assert.notEqual(c.getState().nodeId, q); // moved on to the next question or the gate
  assert.ok(!said.slice(1).some((t) => NODES[q].replies.some((r) => r.text === t))); // the same question is not asked again
});

test("repair: refusing an email at the contact ask is accepted and the email is not asked for again", async () => {
  const c = fast();
  await c.send("I want to speak to a real person");
  await c.choose("email"); // contact.ask
  assert.equal(c.getState().nodeId, "contact.ask");
  const before = assistantTexts(c).length;
  await c.send("I don't want to share my email.");
  assert.equal(c.getState().nodeId, "intervention.noted");
  const after = assistantTexts(c).slice(before).join(" ");
  assert.match(after, /completely fine|leave that out/i);
  assert.doesNotMatch(after, /Type a work email|work email/i);
});

test("repair: \"I don't know\" closes a fit question without penalty", async () => {
  const c = fast();
  const q = await toFirstFitQuestion(c);
  await c.send("I don't know");
  assert.match(assistantTexts(c).join(" "), /Not knowing is a useful answer/);
  assert.notEqual(c.getState().nodeId, q);
});

test("repair: \"that's not what I asked\" owns the miss, then escalates to a person, never repeating", async () => {
  const c = fast();
  await c.startFrom("curious");
  const seen = [];
  for (let i = 0; i < 4; i++) {
    await c.send("That's not what I asked.");
    seen.push(assistantTexts(c).at(-1));
  }
  assert.deepEqual(adjacentRepeats(seen), []);
  assert.match(seen[0], /missed that/i);
  assert.deepEqual(c.getState().choices.map((x) => x.id).sort(), ["person", "stop"]);
});

test("repair: a straight-answer request gets a short honest answer", async () => {
  const c = fast();
  await c.startFrom("curious");
  await c.send("Can you just give me a straight answer?");
  const t = assistantTexts(c).at(-1);
  assert.match(t, /Short version/);
  assert.match(t, /AI assistant/);
});

test("frustration and a request for a person still win over a repair phrase", async () => {
  const c = fast();
  await c.send("That's not what I asked and this is useless, I'm fed up");
  assert.equal(c.getState().nodeId, "alert.handoff");
  const d = fast();
  await d.send("That's not what I asked. Let me talk to someone.");
  assert.ok(d.getState().nodeId.startsWith("intervention."));
});

// ---- one bubble at a time; no highlighted narration; suggestion groups ----
test("a multi-part reply appears one bubble at a time, with the typing indicator between", async () => {
  const c = createConversation({ config: WIDGET_CONFIG, onTypingDelay: () => 15 });
  const shots = [];
  c.subscribe((st) => shots.push({ n: st.messages.filter((m) => m.role === "assistant").length, typing: st.typing }));
  await c.startFrom("promising"); // qualify.explain has several bubbles
  const bubbles = NODES["qualify.explain"].replies.length;
  assert.ok(bubbles >= 3);
  const counts = [...new Set(shots.map((x) => x.n))];
  assert.deepEqual(counts, Array.from({ length: bubbles + 1 }, (_, i) => counts[0] + i)); // 1,2,3,... never a jump
  assert.equal(shots.at(-1).typing, false);
  assert.ok(shots.slice(0, -1).filter((x) => x.n > counts[0]).every((x) => x.typing)); // still typing until the last bubble
});

test("each bubble gets its own typing pause that fits its length", async () => {
  const seen = [];
  const c = createConversation({ config: WIDGET_CONFIG, onTypingDelay: (i) => (seen.push(i), 1) });
  await c.startFrom("promising");
  const lens = NODES["qualify.explain"].replies.map((r) => r.text.length);
  assert.deepEqual(seen.map((x) => x.chars), lens);
  assert.deepEqual(seen.map((x) => x.index), lens.map((_, i) => i));
  assert.ok(seen.every((x) => x.total === lens.length));
});

test("no reply is highlighted narration of the agent's own process", () => {
  for (const [id, node] of Object.entries(NODES)) {
    for (const r of node.replies) {
      assert.notEqual(r.tone, "cue", `${id} still has a cue`);
      assert.doesNotMatch(r.text, /^I’m (explaining|naming|telling you|flagging|separating|stepping back)/, `${id}: narration`);
    }
  }
});

test("every suggested reply leads somewhere that exists", () => {
  const special = new Set(["__restart__", "__fit_next__", "__fit_gate__"]);
  const ok = (t) => (Array.isArray(t) ? t : [t]).every((x) => x == null || special.has(x) || NODES[x]);
  for (const [id, node] of Object.entries(NODES)) for (const ch of node.choices || []) assert.ok(ok(ch.next), `${id}: ${ch.id} -> ${ch.next}`);
  for (const g of Object.values(RECOVERY.groups)) for (const t of g.tiers) for (const ch of t.choices || []) assert.ok(ok(ch.next), `recovery ${ch.id}`);
  for (const t of REPAIR.misunderstood.tiers) for (const ch of t.choices || []) assert.ok(ok(ch.next), `repair ${ch.id}`);
});

test("the main explanation nodes offer questions to ask and actions to take", () => {
  const kindOf = (c) => c.kind || (/\?\s*$/.test(c.label) ? "ask" : "action");
  for (const id of ["qualify.explain", "product.intro"]) {
    const kinds = NODES[id].choices.map(kindOf);
    assert.ok(kinds.filter((k) => k === "ask").length >= 3, `${id} needs three suggested questions`);
    assert.ok(kinds.includes("action"), `${id} needs an action`);
  }
});
