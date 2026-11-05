// Observe the Northstar widget engine. Read-only: imports engine.js/scenarios.js/config.js unmodified.
// usage: node run_widget.mjs <widget_dir> <cases.json> <out.json> <cases_hash>
import { readFileSync, writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { join, resolve } from "node:path";

const [, , widgetDir, casesPath, outPath, hash] = process.argv;
const dir = resolve(widgetDir);
const { createConversation } = await import(pathToFileURL(join(dir, "engine.js")));
const { GLOBAL_ROUTES, NODES } = await import(pathToFileURL(join(dir, "scenarios.js")));
const { WIDGET_CONFIG } = await import(pathToFileURL(join(dir, "config.js")));

const straighten = (t) => String(t || "").replace(/[’‘]/g, "'");
const normalize = (t) => straighten(t).toLowerCase().replace(/\s+/g, " ").trim();
const hasKeyword = (h, k) => {
  const n = normalize(k);
  if (n.length <= 3 && /^[a-z0-9]+$/.test(n)) return new RegExp(`\\b${n}s?\\b`).test(h);
  return h.includes(n);
};
const includesAny = (hay, kws) => { const h = normalize(hay); return kws.some((k) => hasKeyword(h, k)); };
function matchGlobal(text) {
  const raw = straighten(text);
  for (const r of GLOBAL_ROUTES) {
    if (r.patterns?.some((re) => re.test(raw))) return r;
    if (r.keywords && includesAny(raw, r.keywords)) return r;
  }
  return null;
}

// reply text -> node ids (template texts matched by the part before the first "{")
const textToNodes = [];
for (const [id, n] of Object.entries(NODES)) for (const r of n.replies || []) textToNodes.push([r.text.split("{")[0], id]);
const nodesOf = (msg) => textToNodes.filter(([pre, id]) => pre && msg.startsWith(pre)).map(([, id]) => id);
const HUMAN_NODES = new Set(["pricing.person", "setup.person", "trust.accountability"]);

const doc = JSON.parse(readFileSync(casesPath, "utf8"));
const out = {};
for (const c of doc.cases) {
  if (c.layer !== "understanding") continue;
  const conv = createConversation({ config: WIDGET_CONFIG, onTypingDelay: () => 0 });
  const rows = [];
  let held = false;
  for (const t of c.turns) {
    const before = conv.getState();
    const prevNode = NODES[before.nodeId];
    const seen = before.messages.length;
    const route = held ? null : matchGlobal(t.u);
    await conv.send(t.u);
    const after = conv.getState();
    const msgs = after.messages.slice(seen + 1).filter((m) => m.role === "assistant");
    const visited = new Set([after.nodeId, ...msgs.flatMap((m) => nodesOf(m.text))]);
    const reply = msgs.map((m) => m.text).join("\n");
    let label = route ? (route.id === "frustration" ? "frustration_agent" : route.id) : "none";
    const hold = held || [...visited].some((n) => n.startsWith("alert."));
    held = hold;
    const humanPath = [...visited].some((n) => n.startsWith("intervention.") || HUMAN_NODES.has(n));
    const fbText = prevNode?.fallback?.text;
    rows.push({
      reply, route: label,
      escalation: hold ? "hold" : humanPath ? "human_path" : "none",
      rep_notified: null, customer_facing: null, intervention_open: null, trust_state: null,
      fallback_used: reply.startsWith("I don’t have a scripted path for that yet.") || (!!fbText && reply.startsWith(fbText)),
    });
  }
  out[c.id] = rows;
}
writeFileSync(outPath, JSON.stringify({ engine: "widget", cases_hash: hash, observations: out }, null, 1));
console.log(`widget: observed ${Object.keys(out).length} cases -> ${outPath}`);
