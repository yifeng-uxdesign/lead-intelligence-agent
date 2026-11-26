/**
 * The lead workspace stand-in: the sales rep's side of the handoff demo.
 * It reads the leads the widget saves (store.js), shows why each needs a person and what the visitor said, and lets the rep
 * join, reply, hand back, resolve or close. The widget tab sees every action live. Provisional: the full workspace design replaces it.
 */
import { createBrowserStore } from "./store.js";

const store = createBrowserStore();
const $ = (id) => document.getElementById(id);
const listEl = $("ws-list");
const detailEl = $("ws-detail");
const bannerEl = $("ws-banner");
const nameEl = $("ws-name");
const NAME_KEY = "northstar.demo.repname";
try {
  nameEl.value = localStorage.getItem(NAME_KEY) || nameEl.value;
} catch {
  /* storage blocked: keep the default */
}
nameEl.addEventListener("change", () => {
  nameEl.value = nameEl.value.trim() || "Maya";
  try {
    localStorage.setItem(NAME_KEY, nameEl.value);
  } catch {
    /* ignore */
  }
  render();
});

const QUICK = [
  { label: "Standard hello", text: "Hi, I’m {Name} from the Northstar team. I’ve read what you shared with the assistant, so you don’t need to repeat it. Where would you like to start?" },
  { label: "After frustration", text: "Hi, I’m {Name}. I’m sorry this has been so frustrating. I’ve read the whole conversation, so let’s start with what matters most to you. What would you like sorted out first?" },
  { label: "Ready for next steps", text: "Hi, I’m {Name}. It sounds like you’re ready to look at next steps. I’ve seen what you told the assistant, so I’ll skip what you’ve already answered." },
  { label: "Step back", text: "I’ll step back for now. The assistant is here if you need anything else, and you can ask for me again anytime." },
];

const STATUS = {
  needs_rep: { label: "Needs you", tone: "alert", order: 0 },
  attention: { label: "Heads up", tone: "warn", order: 1 },
  with_rep: { label: "With you", tone: "blue", order: 2 },
  handed_back: { label: "Handed back", tone: "grey", order: 3 },
  resolved: { label: "Resolved", tone: "ok", order: 4 },
  closed: { label: "Closed", tone: "grey", order: 5 },
};

let selectedId = null;
let draft = "";
const alerted = new Set(); // leads that already raised the "needs you" banner

/** The widget updates a lead's status after it applies an action; until then, show what the rep has just done. */
function statusOf(lead) {
  const pending = store.getActions(lead.id).filter((a) => a.at > lead.updatedAt).at(-1);
  if (pending) return { join: "with_rep", message: "with_rep", handback: "handed_back", resolve: "resolved", close: "closed" }[pending.type] || lead.status;
  return lead.status;
}

const initial = (s) => (s || "?").trim().charAt(0).toUpperCase();
const clock = (t) => new Date(t).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
const title = (lead) => lead.contact?.email || `Visitor ${lead.id.slice(-4)}`;

function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text != null) n.textContent = text;
  return n;
}

function badge(status) {
  const s = STATUS[status] || STATUS.closed;
  return el("span", `ws-badge ws-badge--${s.tone}`, s.label);
}

function renderList(leads) {
  listEl.replaceChildren();
  if (!leads.length) {
    const empty = el("div", "ws-empty");
    empty.append(el("p", "ws-empty__title", "No conversations yet"), el("p", null, "Open the widget in another window, ask for a person, and it appears here."));
    listEl.append(empty);
    return;
  }
  for (const lead of leads) {
    const st = statusOf(lead);
    const b = el("button", `ws-item${lead.id === selectedId ? " is-selected" : ""}`);
    b.type = "button";
    b.setAttribute("aria-current", lead.id === selectedId ? "true" : "false");
    const top = el("div", "ws-item__top");
    top.append(el("span", "ws-item__who", title(lead)), badge(st));
    b.append(top, el("span", "ws-item__reason", lead.reason?.label || "Conversation"), el("span", "ws-item__time", `Updated ${clock(lead.updatedAt)}`));
    b.addEventListener("click", () => {
      selectedId = lead.id;
      render();
    });
    listEl.append(b);
  }
}

function transcript(lead) {
  const box = el("div", "ws-thread");
  box.setAttribute("role", "log");
  box.setAttribute("aria-label", "Conversation so far");
  for (const m of lead.transcript || []) {
    if (m.role === "event") {
      box.append(el("p", "ws-line", m.text));
      continue;
    }
    const who = m.role === "user" ? "Visitor" : m.role === "rep" ? `${m.name} (you)` : "Assistant";
    const row = el("div", `ws-msg ws-msg--${m.role}`);
    row.append(el("p", "ws-msg__meta", `${who} · ${clock(m.at)}`), el("p", "ws-msg__text", m.text));
    box.append(row);
  }
  return box;
}

function act(lead, type, extra = {}) {
  store.postRepAction(lead.id, { type, name: nameEl.value.trim() || "Maya", ...extra });
}

function renderDetail(lead) {
  const hadFocus = document.activeElement?.id === "ws-reply";
  detailEl.replaceChildren();
  if (!lead) {
    const empty = el("div", "ws-empty");
    empty.append(el("p", "ws-empty__title", "Select a conversation"), el("p", null, "Choose one on the left to see why it needs a person and what was said."));
    detailEl.append(empty);
    return;
  }
  const st = statusOf(lead);
  const head = el("div", "ws-detail__head");
  const h = el("div");
  h.append(el("h2", null, title(lead)), el("p", "ws-sub", lead.reason?.label || ""));
  head.append(h, badge(st));
  detailEl.append(head);

  const facts = el("div", "ws-facts");
  const known = el("section", "ws-card");
  known.append(el("h3", null, "What we know"));
  const ul = el("ul");
  const lines = [...(lead.summary || [])];
  for (const t of lines.length ? lines : ["Nothing specific yet."]) ul.append(el("li", null, t));
  known.append(ul);
  const contact = el("section", "ws-card");
  contact.append(el("h3", null, "Contact"), el("p", null, lead.contact?.email ? `Work email: ${lead.contact.email}` : "No contact details shared yet."));
  facts.append(known, contact);
  detailEl.append(facts);

  detailEl.append(el("h3", "ws-h3", "Conversation"), transcript(lead));

  const actions = el("div", "ws-actions");
  const ended = st === "resolved" || st === "closed";
  if (ended) {
    actions.append(el("p", "ws-note", lead.endedBy === "visitor" ? "The visitor started over, so this conversation has ended." : "This conversation has ended."));
  } else if (st === "with_rep") {
    const quick = el("div", "ws-quick");
    quick.append(el("span", "ws-quick__label", "Quick replies"));
    for (const q of QUICK) {
      const b = el("button", "ws-chip", q.label);
      b.type = "button";
      b.addEventListener("click", () => {
        draft = q.text.replaceAll("{Name}", nameEl.value.trim() || "Maya");
        const ta = $("ws-reply");
        ta.value = draft;
        ta.focus();
      });
      quick.append(b);
    }
    const ta = el("textarea");
    ta.id = "ws-reply";
    ta.rows = 3;
    ta.value = draft;
    ta.placeholder = "Reply to the visitor…";
    ta.setAttribute("aria-label", "Reply to the visitor");
    ta.addEventListener("input", () => (draft = ta.value));
    const send = () => {
      const text = ta.value.trim();
      if (!text) return;
      act(lead, "message", { text });
      draft = "";
      ta.value = "";
    };
    ta.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        send();
      }
    });
    const row = el("div", "ws-row");
    const sendBtn = el("button", "ws-btn ws-btn--primary", "Send reply");
    sendBtn.type = "button";
    sendBtn.addEventListener("click", send);
    const done = (label, type, quiet) => {
      const b = el("button", `ws-btn${quiet ? " ws-btn--quiet" : ""}`, label);
      b.type = "button";
      b.addEventListener("click", () => act(lead, type));
      return b;
    };
    row.append(sendBtn, done("Resolve", "resolve"), done("Hand back to assistant", "handback"), done("Close conversation", "close", true));
    actions.append(quick, ta, row);
  } else {
    const join = el("button", "ws-btn ws-btn--primary", "Join conversation");
    join.type = "button";
    join.addEventListener("click", () => {
      act(lead, "join");
      draft = "";
    });
    actions.append(join, el("p", "ws-note", "The visitor sees who you are, and the assistant goes quiet while you are in the conversation."));
  }
  detailEl.append(actions);

  const thread = detailEl.querySelector(".ws-thread");
  if (thread) thread.scrollTop = thread.scrollHeight;
  if (hadFocus) $("ws-reply")?.focus();
}

function banner(leads) {
  const needs = leads.filter((l) => statusOf(l) === "needs_rep");
  const fresh = needs.filter((l) => !alerted.has(l.id));
  for (const l of needs) alerted.add(l.id);
  document.title = needs.length ? `(${needs.length}) Needs you · Lead workspace` : "Lead workspace · Northstar demo";
  if (fresh.length) {
    const l = fresh[0];
    bannerEl.hidden = false;
    bannerEl.replaceChildren(el("span", null, `New conversation needs you: ${l.reason?.label || "a visitor"}.`));
    const open = el("button", "ws-btn ws-btn--small", "Open it");
    open.type = "button";
    open.addEventListener("click", () => {
      selectedId = l.id;
      bannerEl.hidden = true;
      render();
    });
    bannerEl.append(open);
  } else if (!needs.length) {
    bannerEl.hidden = true;
  }
}

function render() {
  const leads = store
    .listLeads()
    .slice()
    .sort((a, b) => (STATUS[statusOf(a)]?.order ?? 9) - (STATUS[statusOf(b)]?.order ?? 9) || b.updatedAt - a.updatedAt);
  if (!selectedId && leads.length) selectedId = leads[0].id;
  if (selectedId && !store.getLead(selectedId)) selectedId = leads[0]?.id || null;
  renderList(leads);
  renderDetail(selectedId ? store.getLead(selectedId) : null);
  banner(leads);
}

$("ws-clear").addEventListener("click", () => {
  if (!confirm("Clear every demo conversation from this browser?")) return;
  store.clear();
  selectedId = null;
  alerted.clear();
  draft = "";
  render();
});

store.subscribe(render);
render();
