/**
 * Deterministic conversation engine for the Northstar widget demo.
 * Not the Python orchestrator. Later this module can be swapped for API calls.
 *
 * Behavior is data-driven (see scenarios.js). The engine adds light, local session memory:
 *   - fit evidence gathered from choices and free text (demo heuristics, not real scoring)
 *   - an "alert" hold: once a visitor is frustrated, the agent stops answering on its own
 *   - a recovery ladder (see RECOVERY in scenarios.js): consecutive misses on one node escalate, never repeat
 *   - a turn queue: the visitor can keep typing while a reply is on its way; messages are handled in order
 *   - length-aware pacing: replies appear one bubble at a time, each after a typing pause that fits its length
 *   - questions first: a visitor's question is answered (or honestly not) before the agent returns to its own question
 *   - handoff: a conversation that reaches a person is saved to a lead store, and the person's actions arrive from it
 * Decisions stay deterministic: every choice below is a pure function of the conversation state.
 */
import {
  FIT, GLOBAL_ROUTES, HANDOFF, KNOWLEDGE, NODES, PERSONAL_EMAIL_DOMAINS, RECOVERY, REPAIR, RESUME_PREFIX, SCENARIOS, isQuestion,
} from "./scenarios.js";
import { createNullStore } from "./store.js";

const EMAIL_RE = /[^\s@]+@([^\s@]+\.[a-z]{2,})/i;

function straighten(text) {
  return String(text || "").replace(/[’‘]/g, "'");
}

function normalize(text) {
  return straighten(text).toLowerCase().replace(/\s+/g, " ").trim();
}

function hasKeyword(h, keyword) {
  const k = normalize(keyword);
  // Very short keywords ("ok", "ae", "rep") match whole words only, so "book" is not "ok".
  if (k.length <= 3 && /^[a-z0-9]+$/.test(k)) {
    return new RegExp(`\\b${k}s?\\b`).test(h);
  }
  return h.includes(k);
}

function includesAny(haystack, keywords) {
  const h = normalize(haystack);
  return keywords.some((k) => hasKeyword(h, k));
}

function isMinimal(text) {
  const n = normalize(text);
  return /^[\s.\-–—…?!,;:]*$/.test(n) || ["ok", "okay", "k", "kk", "hmm", "hm", "mm", "mhm"].includes(n);
}

const MAX_QUEUE = 2; // messages a visitor can have waiting while a reply is on its way

/** Typing delay in ms before one bubble of `chars` characters. Pure. Values live in config.pacing. */
export function paceMs(chars, pacing) {
  const p = { minMs: 600, baseMs: 400, perCharMs: 6, maxMs: 1800, ...(pacing || {}) };
  return Math.round(Math.min(p.maxMs, Math.max(p.minMs, p.baseMs + chars * p.perCharMs)));
}

/**
 * The recovery reply for the idx-th consecutive miss on one node. Pure.
 * Tiers play in order; past the last tier it cycles through the last tier and the alternates, and it never
 * returns the text of the previous assistant message.
 */
export function pickRecovery(tiers, idx, lastText, alternates = []) {
  const last = tiers.length - 1;
  const tail = tiers[last];
  let pick;
  if (idx <= last) pick = tiers[idx];
  else {
    const cycle = [tail, ...alternates.map((text) => ({ text, choices: tail.choices }))];
    pick = cycle[(idx - last) % cycle.length];
  }
  if (pick.text === lastText) {
    const text = alternates.find((t) => t !== lastText);
    if (text) pick = { text, choices: tail.choices };
  }
  return { ...pick, final: idx >= last };
}

function uid() {
  return `m_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 7)}`;
}

/** Inquiries per month, if the text states a volume ("about 300 leads a month"). */
function parseVolume(text) {
  const m = text.match(
    /(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s*(k\b)?\s*(?:\+\s*)?(?:[a-z-]+\s+){0,3}?(leads?|inquir\w*|inbound|requests?|submissions?|sign-?ups?|emails?|tickets?|conversations?|chats?)/i
  );
  if (!m) return null;
  let n = parseFloat(m[1].replace(/,/g, ""));
  if (m[2]) n *= 1000;
  if (/\b(a|per|each|every)\s*week|weekly|\/wk/i.test(text)) n *= 4.3;
  else if (/\b(a|per|each|every)\s*day|daily/i.test(text)) n *= 21;
  else if (/\b(a|per|each|every)\s*year|annually/i.test(text)) n /= 12;
  return n;
}

function extractFit(raw) {
  const text = straighten(raw);
  const tags = [];
  const volume = parseVolume(text);
  if (volume != null) {
    if (volume < FIT.volume.low) tags.push("low_volume");
    else if (volume >= FIT.volume.high) tags.push("high_volume");
    else tags.push("mid_volume"); // stated, but neither a strong nor a weak signal
  }
  if (FIT.patterns.noSystems.test(text)) tags.push("no_systems");
  else if (FIT.patterns.crm.test(text)) tags.push("existing_crm");
  if (FIT.patterns.triage.test(text)) tags.push("triage_pain");
  if (FIT.patterns.automation.test(text)) tags.push("wants_automation");
  return tags;
}

function listPhrases(tags, fit) {
  const phrases = tags.filter((t) => fit.has(t)).map((t) => FIT.phrases[t]);
  if (!phrases.length) return "a few things worth a conversation";
  if (phrases.length === 1) return phrases[0];
  return `${phrases.slice(0, -1).join(", ")} and ${phrases[phrases.length - 1]}`;
}

export function createConversation({ config, onTypingDelay, store: givenStore }) {
  const store = givenStore || createNullStore(); // where a handoff is saved and a person's actions arrive
  let state = buildWelcomeState(config);
  let syncing = false; // true while this conversation writes to the store, so its own write is not read back as news
  let epoch = 0; // bumped on restart so in-flight replies from the old thread are dropped
  let stage = null; // while set, replies are collected here and shown after the typing delay
  const listeners = new Set();
  const put = (msg) => (stage || state.messages).push(msg);

  function emit() {
    if (state.lead) syncLead();
    const snapshot = getState();
    listeners.forEach((fn) => fn(snapshot));
  }

  function getState() {
    const node = state.nodeId && state.nodeId !== "welcome" ? NODES[state.nodeId] : null;
    return {
      scenarioId: state.scenarioId,
      nodeId: state.nodeId,
      messages: state.messages.map((m) => ({ ...m })),
      startersVisible: state.startersVisible,
      choices: choicesNow(node),
      mode: state.mode,
      rep: state.rep ? { ...state.rep } : null,
      typing: state.typing,
      queued: state.queue.length,
      canSend: state.queue.length < MAX_QUEUE,
    };
  }

  function currentChoices() {
    return getState().choices;
  }

  // After an interruption the visitor can pick up the question they were on.
  function choicesNow(node) {
    const base = state.extraChoices ?? node?.choices ?? [];
    if (state.offerResume && state.resumeNode) return [...base, { id: "resume", label: "Carry on where we left off", next: "__resume__", kind: "action" }];
    return base;
  }

  function setWelcome() {
    if (state.lead && state.lead.state === "open") {
      state.lead.state = "closed"; // the visitor started over: the person sees the conversation ended
      state.lead.endedBy = "visitor";
      syncLead();
    }
    epoch += 1;
    state = buildWelcomeState(config);
    emit();
  }

  function pushUser(text, queued = false) {
    const id = uid();
    state.messages.push({ id, role: "user", text: text.trim(), at: Date.now(), ...(queued ? { queued: true } : {}) });
    state.startersVisible = false;
    return id;
  }

  // `stated` = the visitor said it in their own words, so that question needn't be asked.
  // Evidence implied by a suggested-reply chip counts toward fit but never skips a question.
  function addFit(tags = [], stated = false) {
    for (const tag of tags) {
      state.fit.add(tag);
      const nodeId = FIT.tagNode[tag];
      if (stated && nodeId) state.answered.add(nodeId);
    }
  }

  // ---- fit gate -----------------------------------------------------------
  function nextQuestion() {
    if (state.fitChecks >= 3) return undefined; // asked enough; don't keep looping
    return FIT.questionNodes.find((id) => !state.answered.has(id));
  }

  function evaluateGate(allowQuestions) {
    const pos = FIT.positive.filter((t) => state.fit.has(t)).length;
    const neg = FIT.negative.filter((t) => state.fit.has(t)).length;
    if (neg === 0 && pos >= FIT.confirmAt) return [FIT.gate.confirmed];
    if (neg >= 1 && pos - neg <= -1) return [FIT.gate.poor];
    const question = nextQuestion();
    if (allowQuestions && question) {
      const first = state.fitChecks === 0;
      state.fitChecks += 1;
      return [first ? FIT.gate.firstCheck : FIT.gate.repeatCheck, question];
    }
    return [FIT.gate.unclear];
  }

  /** Expand a `next` (id, array, or special token) into the node ids to play. */
  function resolve(target) {
    const out = [];
    for (const t of Array.isArray(target) ? target : [target]) {
      if (t === "__fit_gate__") out.push(...evaluateGate(true));
      else if (t === "__fit_next__") {
        const q = nextQuestion();
        if (q) out.push(q);
        else out.push(...evaluateGate(false));
      } else out.push(t);
    }
    return out;
  }

  function fillTemplate(text) {
    return text
      .replace("{fit_positive}", listPhrases(FIT.positive, state.fit))
      .replace("{fit_negative}", listPhrases(FIT.negative, state.fit))
      .replace("{fit_new}", listPhrases(state.newTags, new Set(state.newTags)));
  }

  function applyNode(nodeId) {
    if (nodeId === "__restart__") {
      setWelcome();
      return;
    }
    if (nodeId === "__resume__") {
      // Pick the earlier question back up, in one short bubble.
      const back = state.resumeNode;
      state.resumeNode = null;
      state.offerResume = false;
      const question = back && NODES[back]?.replies.at(-1);
      if (!question) return;
      state.nodeId = back;
      state.extraChoices = null;
      put({ id: uid(), role: "assistant", text: RESUME_PREFIX + fillTemplate(question.text), tone: "message", at: Date.now() });
      return;
    }
    // A node already shown once can offer a shorter variant instead of repeating itself.
    if (NODES[nodeId]?.repeat && state.seen.has(nodeId)) nodeId = NODES[nodeId].repeat;
    state.seen.add(nodeId);
    const node = NODES[nodeId];
    state.extraChoices = null; // a node's own suggested replies come back when the thread moves on
    if (!node) {
      put({
        id: uid(),
        role: "assistant",
        text: "I don’t have a scripted path for that yet. You can pick a suggested reply or restart the conversation.",
        at: Date.now(),
      });
      return;
    }
    state.nodeId = nodeId;
    if (!nodeId.startsWith("kb.")) {
      state.resumeNode = null; // the visitor moved on, so there is nothing to carry on from
      state.offerResume = false;
    }
    if (nodeId.startsWith("alert.")) state.alert = true;
    openLead(nodeId);
    for (const [id, scenario] of Object.entries(SCENARIOS)) {
      if (nodeId.startsWith(`${id}.`)) state.scenarioId = scenario.id;
    }
    for (const reply of node.replies) {
      put({
        id: uid(),
        role: "assistant",
        text: fillTemplate(reply.text),
        tone: reply.tone || "message",
        at: Date.now(),
      });
    }
  }

  /**
   * Run `produce` (which decides the replies and updates the state), then show the replies one bubble at a time,
   * each after a typing pause that fits its own length. A restart in the meantime drops what is left.
   */
  async function deliver(produce) {
    const myEpoch = epoch;
    state.typing = true;
    const staged = [];
    stage = staged;
    try {
      produce();
    } finally {
      stage = null;
    }
    if (myEpoch !== epoch) return; // the thread was restarted while deciding
    emit(); // the typing indicator appears
    for (let i = 0; i < staged.length; i++) {
      const m = staged[i];
      let ms = paceMs(m.text.length, config.pacing);
      if (typeof onTypingDelay === "function") {
        const override = onTypingDelay({ chars: m.text.length, ms, index: i, total: staged.length });
        if (typeof override === "number") ms = override;
      }
      await new Promise((r) => setTimeout(r, ms));
      if (myEpoch !== epoch) return;
      m.at = Date.now();
      state.messages.push(m);
      if (i === staged.length - 1) state.typing = false; // between bubbles the indicator stays
      emit();
    }
    if (!staged.length) {
      state.typing = false;
      emit();
    }
  }

  // ---- handoff: saving the conversation for a person, and what the person does ----
  function openLead(nodeId) {
    const h = HANDOFF.nodes[nodeId];
    if (!h) return;
    const reason = { code: h.code, label: h.label };
    if (!state.lead) state.lead = { id: uid(), reason, level: h.level, state: "open" };
    else if (state.lead.state !== "open") state.lead = { ...state.lead, reason, level: h.level, state: "open" }; // asked again after a resolve
    else if (HANDOFF.rank[h.level] > HANDOFF.rank[state.lead.level]) Object.assign(state.lead, { reason, level: h.level });
    if (h.level === "intervention" && state.mode === "agent") state.mode = "waiting";
  }

  function leadStatus() {
    const l = state.lead;
    if (l.state !== "open") return l.state; // "resolved" or "closed"
    if (state.mode === "rep") return "with_rep";
    return l.level === "intervention" ? "needs_rep" : "attention";
  }

  const sentence = (t) => t.charAt(0).toUpperCase() + t.slice(1);

  /** Plain lines for the person: what the visitor told us and what they wanted to know. */
  function summaryLines() {
    const out = [];
    for (const tag of [...FIT.positive, ...FIT.negative, "mid_volume"]) if (state.fit.has(tag)) out.push(sentence(FIT.phrases[tag]));
    for (const id of state.seen) if (HANDOFF.topics[id]) out.push(HANDOFF.topics[id]);
    if (state.contact?.email) out.push("Shared a work email");
    return [...new Set(out)];
  }

  function syncLead() {
    const l = state.lead;
    if (!l) return;
    const snapshot = {
      id: l.id,
      status: leadStatus(),
      level: l.level,
      reason: l.reason,
      contact: state.contact ? { ...state.contact } : {},
      summary: summaryLines(),
      endedBy: l.endedBy || null,
      transcript: state.messages.map((m) => ({ role: m.role, text: m.text, at: m.at, ...(m.name ? { name: m.name } : {}) })),
    };
    const key = JSON.stringify(snapshot);
    if (key === state.lastSynced) return;
    state.lastSynced = key;
    syncing = true;
    try {
      store.upsertLead(snapshot);
    } finally {
      syncing = false;
    }
  }

  const eventLine = (text) => state.messages.push({ id: uid(), role: "event", text, at: Date.now() });

  /** One thing the person did. Returns a node to play afterwards, if any. */
  function applyRepAction(a) {
    const name = a.name || state.rep?.name || "Someone from the team";
    switch (a.type) {
      case "join":
        state.mode = "rep";
        state.rep = { name };
        eventLine(`${name} from the Northstar team has joined the conversation.`);
        return null;
      case "message":
        state.messages.push({ id: uid(), role: "rep", name, text: a.text, at: Date.now() });
        return null;
      case "handback":
        Object.assign(state, { mode: "agent", rep: null, alert: false });
        eventLine(`${name} has handed the conversation back to the assistant.`);
        return null;
      case "resolve":
        Object.assign(state, { mode: "agent", rep: null, alert: false });
        state.lead.state = "resolved";
        eventLine(`${name} has finished helping with this. I’m back if you need anything else, and you can ask for ${name} or someone on the team again anytime.`);
        return "rep.checkin"; // the assistant asks; only the visitor can say it is not resolved
      case "close":
        Object.assign(state, { mode: "agent", rep: null, alert: false });
        state.lead.state = "closed";
        eventLine(`${name} has ended the conversation. You can restart whenever you like.`);
        return null;
      default:
        return null;
    }
  }

  function applyRepActions() {
    if (!state.lead) return;
    if (state.busy || state.typing) {
      state.repPending = true; // handled as soon as the reply in progress is done
      return;
    }
    const actions = store.getActions(state.lead.id);
    let followUp = null;
    while (state.repSeen < actions.length) followUp = applyRepAction(actions[state.repSeen++]) || followUp;
    state.repPending = false;
    emit();
    if (followUp) turn(async () => respond(followUp));
  }
  store.subscribe(() => {
    if (!syncing) applyRepActions();
  });

  // ---- questions first: a visitor's question outranks the agent's own pending question ----
  function canResume(nodeId) {
    const n = NODES[nodeId];
    if (!n || nodeId.startsWith("kb.") || nodeId.startsWith("alert.") || nodeId.startsWith("rep.")) return false;
    return /\?\s*$/.test(n.replies?.at(-1)?.text || "") || !!n.captureEmail;
  }

  function matchKnowledge(text) {
    const raw = straighten(text);
    return KNOWLEDGE.find((k) => k.pattern.test(raw))?.node || null;
  }

  async function answerFromKnowledge(target) {
    if (!state.resumeNode && canResume(state.nodeId)) state.resumeNode = state.nodeId;
    state.offerResume = !!state.resumeNode;
    state.missNode = null;
    state.missCount = 0;
    state.gapCount = 0;
    state.repair = { intent: null, n: 0 };
    await deliver(() => applyNode(target));
  }

  /** A question nothing covers: say so plainly, offer what can be answered, and never repeat. */
  async function respondGap() {
    if (!state.resumeNode && canResume(state.nodeId)) state.resumeNode = state.nodeId;
    const idx = state.gapCount;
    state.gapCount = idx + 1;
    state.missNode = null;
    state.missCount = 0;
    await deliver(() => {
      const lastAssistant = [...state.messages].reverse().find((m) => m.role === "assistant");
      const pick = pickRecovery(RECOVERY.gap.tiers, idx, lastAssistant?.text, RECOVERY.alternates);
      state.extraChoices = pick.choices || null;
      state.offerResume = !!state.resumeNode;
      put({ id: uid(), role: "assistant", text: pick.text, at: Date.now() });
    });
  }

  /** Show the typing indicator, then play `target` (unless the thread was restarted meanwhile). */
  async function respond(target) {
    if (target === "__restart__") {
      setWelcome();
      return;
    }
    state.missNode = null; // an understood reply ends any run of misses
    state.missCount = 0;
    state.repair = { intent: null, n: 0 };
    state.gapCount = 0;
    await deliver(() => {
      for (const id of resolve(target)) applyNode(id);
    });
  }

  /** The tiers to use when nothing matched at `nodeId`: its recovery group, else its own single fallback. */
  function tiersFor(nodeId, node) {
    const groupId = RECOVERY.nodeGroup[nodeId];
    if (groupId) return RECOVERY.groups[groupId].tiers;
    if (node?.fallback) return [{ text: node.fallback.text, next: node.fallback.next }];
    return null;
  }

  async function respondFallback(node) {
    const nodeId = state.nodeId;
    const tiers = tiersFor(nodeId, node);
    const idx = state.missNode === nodeId ? state.missCount : 0; // consecutive misses on this node
    state.missNode = nodeId;
    state.missCount = idx + 1;
    await deliver(() => {
      if (!tiers) return;
      const lastAssistant = [...state.messages].reverse().find((m) => m.role === "assistant");
      const pick = pickRecovery(tiers, idx, lastAssistant?.text, RECOVERY.alternates);
      // Releasing the visitor from a fit question counts as answering it (a refusal is an answer).
      if (pick.final && RECOVERY.nodeGroup[nodeId] && FIT.questionNodes.includes(nodeId)) state.answered.add(nodeId);
      state.extraChoices = pick.choices || null;
      if (pick.text) put({ id: uid(), role: "assistant", text: pick.text, at: Date.now() });
      if (pick.next) {
        state.missNode = null;
        state.missCount = 0;
        for (const id of resolve(pick.next)) applyNode(id);
      }
    });
  }

  function matchGlobal(text) {
    const raw = straighten(text);
    for (const route of GLOBAL_ROUTES) {
      if (route.patterns?.some((re) => re.test(raw))) return route;
      if (route.keywords && includesAny(raw, route.keywords)) return route;
    }
    return null;
  }

  /** Is the visitor talking about the conversation itself ("why do you need that", "I'd rather not say")? */
  function matchRepair(text) {
    const raw = straighten(text);
    return REPAIR.order.find((intent) => REPAIR.patterns[intent].test(raw)) || null;
  }

  async function respondRepair(intent) {
    const nodeId = state.nodeId;
    const spec = REPAIR[intent];
    const n = state.repair.intent === intent ? state.repair.n : 0; // the same repair again: escalate, never repeat
    state.repair = { intent, n: n + 1 };
    state.missNode = null; // the visitor is engaged, so this is not a miss
    state.missCount = 0;
    await deliver(() => {
      let tiers = spec.tiers;
      if (intent === "why" && REPAIR.why.byNode[nodeId]) tiers = [{ text: REPAIR.why.byNode[nodeId] }, ...spec.tiers.slice(1)];
      const lastAssistant = [...state.messages].reverse().find((m) => m.role === "assistant");
      const pick = pickRecovery(tiers, n, lastAssistant?.text, RECOVERY.alternates);
      put({ id: uid(), role: "assistant", text: pick.text, at: Date.now() });
      let next = null;
      if (intent === "refusal" || intent === "unknown") {
        // A refusal or "I don't know" is an answer: the question is closed and is not asked again.
        if (FIT.questionNodes.includes(nodeId)) {
          state.answered.add(nodeId);
          next = "__fit_next__";
        } else if (intent === "refusal") {
          next = REPAIR.refusalNext[nodeId] || null;
        }
      }
      if (pick.choices) state.extraChoices = pick.choices;
      if (next) for (const id of resolve(next)) applyNode(id);
    });
  }

  function matchNode(node, text) {
    if (!node) return null;
    const n = normalize(text);
    for (const choice of [...(state.extraChoices || []), ...(node.choices || [])]) {
      if (n === normalize(choice.label) || n.includes(normalize(choice.label))) {
        return { next: choice.next, fit: choice.fit };
      }
    }
    for (const route of node.routes || []) {
      if (includesAny(n, route.keywords)) return { next: route.next, fit: route.fit };
    }
    return null;
  }

  function matchStarter(text) {
    const n = normalize(text);
    for (const starter of config.starters) {
      if (n === normalize(starter.label) || n.includes(normalize(starter.label))) {
        return starter.scenarioId;
      }
    }
    if (includesAny(n, ["concern", "worry", "trust", "prospects", "ai talking"])) return "hesitant";
    if (includesAny(n, ["how does", "qualify", "qualification"])) return "promising";
    if (includesAny(n, ["explor", "looking", "curious", "evaluat"])) return "curious";
    return null;
  }

  /**
   * One visitor turn, then any messages that arrived while it was being answered, in order. Nothing is dropped,
   * so a request for a person or a sign of frustration typed mid-reply is still handled (just after that reply).
   */
  async function turn(first) {
    const myEpoch = epoch;
    state.busy = true;
    try {
      await first();
      while (myEpoch === epoch && state.queue.length) {
        const next = state.queue.shift();
        const shown = state.messages.find((m) => m.id === next.id);
        if (shown) delete shown.queued;
        await processTurn(next.text);
      }
    } finally {
      if (myEpoch === epoch) {
        state.busy = false;
        if (state.repPending) applyRepActions();
      }
    }
  }

  function canSend() {
    return state.queue.length < MAX_QUEUE;
  }

  /** Returns false when the message was not accepted (empty, or the queue is full). */
  async function send(raw) {
    const text = String(raw || "").trim();
    if (!text) return false;
    if (state.busy) {
      if (!canSend()) return false;
      const id = pushUser(text, true);
      state.queue.push({ id, text });
      emit();
      return true;
    }
    await turn(async () => {
      pushUser(text);
      await processTurn(text);
    });
    return true;
  }

  async function processTurn(text) {
    // While a person is in the conversation the assistant stays silent; the message goes to them (the lead's transcript).
    if (state.mode === "rep") {
      emit();
      return;
    }

    // The visitor was shown an answer to an interruption and is now answering the question they left: go back to it.
    if (state.nodeId.startsWith("kb.") && state.resumeNode && !isQuestion(text)) {
      state.nodeId = state.resumeNode;
      state.resumeNode = null;
      state.offerResume = false;
      state.extraChoices = null;
    }

    // Once frustrated, the agent does not keep answering on its own.
    if (state.alert) {
      if (state.nodeId === "alert.handoff") await respond("alert.hold");
      else await respondFallback(NODES[state.nodeId]);
      return;
    }

    const node = NODES[state.nodeId];

    // A work email typed where one is wanted: company domains only.
    if (node?.captureEmail) {
      const m = text.match(EMAIL_RE);
      if (m) {
        const personal = PERSONAL_EMAIL_DOMAINS.includes(m[1].toLowerCase());
        if (!personal) state.contact = { email: m[0].replace(/[.,;:!?)]+$/, "") }; // saved with the lead
        await respond(personal ? node.captureEmail.personal : node.captureEmail.company);
        return;
      }
    }

    const tags = extractFit(text);
    addFit(tags, true);

    // Persona signals: identity, human request, frustration, buying signal, hesitation...
    const route = matchGlobal(text);
    if (route && (Array.isArray(route.next) || route.next !== state.nodeId)) {
      await respond(route.next);
      return;
    }

    // The visitor is talking about the conversation itself: why we ask, "that's not what I asked", "I'd rather not say".
    const repair = matchRepair(text);
    if (repair) {
      await respondRepair(repair);
      return;
    }

    const asked = isQuestion(text);
    const known = asked ? matchKnowledge(text) : null;

    if (state.nodeId === "welcome") {
      if (known) {
        await answerFromKnowledge(known);
        return;
      }
      if (tags.length) {
        state.newTags = tags;
        await respond(["fit.ack", "__fit_next__"]);
        return;
      }
      if (isMinimal(text)) {
        await respond("quiet.patient");
        return;
      }
      const scenarioId = matchStarter(text) || "curious";
      await respond(SCENARIOS[scenarioId].entry);
      return;
    }

    const hit = matchNode(node, text);
    if (hit) {
      if (FIT.questionNodes.includes(state.nodeId)) state.answered.add(state.nodeId);
      addFit(hit.fit);
      if (tags.length && hit.next !== "__restart__") {
        state.newTags = tags;
        await respond(["fit.ack", ...[].concat(hit.next)]);
      } else {
        await respond(hit.next);
      }
      return;
    }

    // A question the node did not expect: answer it first (or say honestly that there is no reliable answer).
    if (known) {
      await answerFromKnowledge(known);
      return;
    }
    if (asked) {
      await respondGap();
      return;
    }

    // The visitor volunteered fit evidence without being asked.
    if (tags.length) {
      state.newTags = tags;
      await respond(["fit.ack", "__fit_next__"]);
      return;
    }

    // One-word or empty replies: patient, no pressure.
    if (isMinimal(text)) {
      if (state.nodeId === "quiet.patient") await respondFallback(NODES["quiet.patient"]);
      else await respond("quiet.patient");
      return;
    }

    // Grouped nodes mark the question answered only when the ladder releases the visitor (tier 3).
    if (FIT.questionNodes.includes(state.nodeId) && !RECOVERY.nodeGroup[state.nodeId]) state.answered.add(state.nodeId);
    await respondFallback(node);
  }

  async function choose(choiceId) {
    if (state.busy) return;
    const choice = currentChoices().find((c) => c.id === choiceId);
    if (!choice) return;
    await turn(async () => {
      pushUser(choice.label);
      if (FIT.questionNodes.includes(state.nodeId)) state.answered.add(state.nodeId);
      addFit(choice.fit);
      await respond(choice.next);
    });
  }

  async function startFrom(scenarioId) {
    if (state.busy) return;
    await turn(async () => {
      const starter = config.starters.find((s) => s.scenarioId === scenarioId);
      const label = starter?.label || SCENARIOS[scenarioId]?.title || scenarioId;
      pushUser(label);
      await respond(SCENARIOS[scenarioId].entry);
    });
  }

  function restart() {
    setWelcome();
  }

  function subscribe(fn) {
    listeners.add(fn);
    fn(getState());
    return () => listeners.delete(fn);
  }

  return { send, choose, startFrom, restart, subscribe, getState, canSend };
}

function buildWelcomeState(config) {
  return {
    scenarioId: null,
    nodeId: "welcome",
    startersVisible: true,
    typing: false,
    alert: false,
    fit: new Set(),
    answered: new Set(), // fit questions the visitor has actually answered
    seen: new Set(),
    newTags: [],
    fitChecks: 0,
    missNode: null, // node where the visitor's words last matched nothing, and how many times in a row
    missCount: 0,
    repair: { intent: null, n: 0 }, // the repair the visitor last asked for, and how many times in a row
    extraChoices: null, // suggested replies a recovery tier offers instead of the node's own
    queue: [], // visitor messages waiting for the reply in progress
    busy: false,
    mode: "agent", // "agent" | "waiting" (a person has been told) | "rep" (a person is in the conversation)
    rep: null, // the person who joined: { name }
    lead: null, // set once the conversation reaches a person: { id, reason, level, state }
    contact: null, // a work email the visitor shared
    repSeen: 0, // how many of the person's actions have been applied
    repPending: false,
    lastSynced: "",
    gapCount: 0, // consecutive questions nothing covered
    resumeNode: null, // the question the visitor was on before an interruption
    offerResume: false,
    messages: [{ id: "welcome", role: "assistant", text: config.welcomeMessage, at: Date.now() }],
  };
}
