/**
 * Deterministic conversation engine for the Northstar widget demo.
 * Not the Python orchestrator. Later this module can be swapped for API calls.
 *
 * Behavior is data-driven (see scenarios.js). The engine adds light, local session memory:
 *   - fit evidence gathered from choices and free text (demo heuristics, not real scoring)
 *   - an "alert" hold: once a visitor is frustrated, the agent stops answering on its own
 */
import { FIT, GLOBAL_ROUTES, NODES, PERSONAL_EMAIL_DOMAINS, SCENARIOS } from "./scenarios.js";

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

export function createConversation({ config, onTypingDelay }) {
  let state = buildWelcomeState(config);
  let epoch = 0; // bumped on restart so in-flight replies from the old thread are dropped
  const listeners = new Set();

  function emit() {
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
      choices: node?.choices ?? [],
      typing: state.typing,
    };
  }

  function setWelcome() {
    epoch += 1;
    state = buildWelcomeState(config);
    emit();
  }

  function pushUser(text) {
    state.messages.push({ id: uid(), role: "user", text: text.trim(), at: Date.now() });
    state.startersVisible = false;
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
    // A node already shown once can offer a shorter variant instead of repeating itself.
    if (NODES[nodeId]?.repeat && state.seen.has(nodeId)) nodeId = NODES[nodeId].repeat;
    state.seen.add(nodeId);
    const node = NODES[nodeId];
    if (!node) {
      state.messages.push({
        id: uid(),
        role: "assistant",
        text: "I don’t have a scripted path for that yet. You can pick a suggested reply or restart the conversation.",
        at: Date.now(),
      });
      return;
    }
    state.nodeId = nodeId;
    if (nodeId.startsWith("alert.")) state.alert = true;
    for (const [id, scenario] of Object.entries(SCENARIOS)) {
      if (nodeId.startsWith(`${id}.`)) state.scenarioId = scenario.id;
    }
    for (const reply of node.replies) {
      state.messages.push({
        id: uid(),
        role: "assistant",
        text: fillTemplate(reply.text),
        tone: reply.tone || "message",
        at: Date.now(),
      });
    }
  }

  async function delay() {
    const ms = typeof onTypingDelay === "function" ? onTypingDelay() : config.typingDelayMs;
    await new Promise((r) => setTimeout(r, ms));
  }

  /** Show the typing indicator, then play `target` (unless the thread was restarted meanwhile). */
  async function respond(target) {
    if (target === "__restart__") {
      setWelcome();
      return;
    }
    const myEpoch = epoch;
    state.typing = true;
    emit();
    await delay();
    if (myEpoch !== epoch) return;
    state.typing = false;
    for (const id of resolve(target)) applyNode(id);
    emit();
  }

  async function respondFallback(node) {
    const fallback = node?.fallback;
    const myEpoch = epoch;
    state.typing = true;
    emit();
    await delay();
    if (myEpoch !== epoch) return;
    state.typing = false;
    if (fallback?.text) {
      state.messages.push({ id: uid(), role: "assistant", text: fallback.text, at: Date.now() });
    }
    if (fallback?.next) for (const id of resolve(fallback.next)) applyNode(id);
    emit();
  }

  function matchGlobal(text) {
    const raw = straighten(text);
    for (const route of GLOBAL_ROUTES) {
      if (route.patterns?.some((re) => re.test(raw))) return route;
      if (route.keywords && includesAny(raw, route.keywords)) return route;
    }
    return null;
  }

  function matchNode(node, text) {
    if (!node) return null;
    const n = normalize(text);
    for (const choice of node.choices || []) {
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

  async function send(raw) {
    const text = String(raw || "").trim();
    if (!text || state.typing) return;
    pushUser(text);

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

    if (state.nodeId === "welcome") {
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

    if (FIT.questionNodes.includes(state.nodeId)) state.answered.add(state.nodeId);
    await respondFallback(node);
  }

  async function choose(choiceId) {
    if (state.typing) return;
    const node = NODES[state.nodeId];
    const choice = node?.choices?.find((c) => c.id === choiceId);
    if (!choice) return;
    pushUser(choice.label);
    if (FIT.questionNodes.includes(state.nodeId)) state.answered.add(state.nodeId);
    addFit(choice.fit);
    await respond(choice.next);
  }

  async function startFrom(scenarioId) {
    if (state.typing) return;
    const starter = config.starters.find((s) => s.scenarioId === scenarioId);
    const label = starter?.label || SCENARIOS[scenarioId]?.title || scenarioId;
    pushUser(label);
    await respond(SCENARIOS[scenarioId].entry);
  }

  function restart() {
    setWelcome();
  }

  function subscribe(fn) {
    listeners.add(fn);
    fn(getState());
    return () => listeners.delete(fn);
  }

  return { send, choose, startFrom, restart, subscribe, getState };
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
    messages: [{ id: "welcome", role: "assistant", text: config.welcomeMessage, at: Date.now() }],
  };
}
