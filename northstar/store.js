/**
 * The demo's lead store: where a conversation that reaches a person is saved, and where the person's actions arrive.
 *
 * It stands in for the product's backend so the whole handoff can be shown with no server: the widget page writes the
 * lead (who, why, what was said), the lead workspace page writes the rep's actions (join, reply, hand back, resolve,
 * close), and both pages see each other's changes live. In a browser it uses localStorage plus a BroadcastChannel, so two
 * tabs of the same site stay in step. Nothing leaves the browser.
 *
 * Ownership keeps two tabs from overwriting each other: the widget is the only writer of `leads`; the workspace is the only
 * writer of `actions`.
 *
 * Shape:
 *   leads:   { [id]: { id, createdAt, updatedAt, status, reason: { code, label }, level, contact: { email? },
 *                      summary: [string], transcript: [{ role, text, at, name? }] } }
 *   actions: { [id]: [{ type: "join" | "message" | "handback" | "resolve" | "close", name, text?, at }] }
 */
const KEY = "northstar.demo.v1";
const CHANNEL = "northstar-demo";

function emptyState() {
  return { leads: {}, actions: {} };
}

function makeStore({ load, save, broadcast, listen }) {
  const subs = new Set();
  let state = load() || emptyState();
  const notify = () => subs.forEach((fn) => fn());
  const reload = () => {
    state = load() || emptyState();
  };
  listen(() => {
    reload();
    notify();
  });
  const write = (change) => {
    reload(); // another tab may have written since we last looked
    change(state);
    save(state);
    broadcast();
    notify();
  };
  return {
    getState: () => state,
    listLeads: () => Object.values(state.leads).sort((a, b) => b.updatedAt - a.updatedAt),
    getLead: (id) => state.leads[id] || null,
    getActions: (id) => state.actions[id] || [],
    /** The widget writes the lead. Fields are merged; the transcript is replaced. */
    upsertLead(lead) {
      write((s) => {
        s.leads[lead.id] = { ...(s.leads[lead.id] || { createdAt: Date.now() }), ...lead, updatedAt: Date.now() };
      });
    },
    /** The workspace writes what the rep does. */
    postRepAction(id, action) {
      write((s) => {
        (s.actions[id] ||= []).push({ ...action, at: Date.now() });
      });
    },
    /** Demo housekeeping: forget every lead and action. */
    clear() {
      write((s) => {
        s.leads = {};
        s.actions = {};
      });
    },
    subscribe(fn) {
      subs.add(fn);
      return () => subs.delete(fn);
    },
  };
}

/** In memory only. Used by tests and anywhere a page is not talking to another tab. Two stores never share data. */
export function createMemoryStore() {
  let saved = null;
  return makeStore({
    load: () => saved && JSON.parse(saved),
    save: (s) => {
      saved = JSON.stringify(s);
    },
    broadcast: () => {},
    listen: () => {},
  });
}

/** Does nothing. The default for the widget when no store is given, so existing callers and the conformance suite are unaffected. */
export function createNullStore() {
  return {
    getState: emptyState,
    listLeads: () => [],
    getLead: () => null,
    getActions: () => [],
    upsertLead() {},
    postRepAction() {},
    clear() {},
    subscribe: () => () => {},
  };
}

/** localStorage + BroadcastChannel, so the widget tab and the workspace tab see each other. Falls back to memory if blocked. */
export function createBrowserStore() {
  let storage = null;
  try {
    storage = window.localStorage;
    storage.setItem(`${KEY}.probe`, "1");
    storage.removeItem(`${KEY}.probe`);
  } catch {
    return createMemoryStore();
  }
  let channel = null;
  try {
    channel = new BroadcastChannel(CHANNEL);
  } catch {
    channel = null;
  }
  return makeStore({
    load: () => {
      try {
        return JSON.parse(storage.getItem(KEY));
      } catch {
        return null;
      }
    },
    save: (s) => {
      try {
        storage.setItem(KEY, JSON.stringify(s));
      } catch {
        /* storage full or blocked: the demo keeps working in this tab */
      }
    },
    broadcast: () => channel?.postMessage("changed"),
    listen: (fn) => {
      if (channel) channel.onmessage = fn;
      window.addEventListener("storage", (e) => e.key === KEY && fn()); // a fallback for browsers without BroadcastChannel
    },
  });
}
