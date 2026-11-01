import { useState, useRef, useEffect } from "react";

const TRUST_STATES = [
  { key: "AWARENESS", label: "Awareness", color: "#6B7280", desc: "Just learning the product exists" },
  { key: "CURIOSITY", label: "Curiosity", color: "#5B8DEF", desc: "Asking exploratory questions, non-committal" },
  { key: "HESITATION", label: "Hesitation", color: "#E0A458", desc: "Vague stalling, unspecific doubt" },
  { key: "OBJECTION", label: "Objection", color: "#D9714E", desc: "Raising a specific counter-argument" },
  { key: "EVALUATION", label: "Evaluation", color: "#8B7FD1", desc: "Comparing options, asking for proof" },
  { key: "TRUST_BUILDING", label: "Trust Building", color: "#4FB286", desc: "Tone warms, asks about logistics" },
  { key: "DECISION_READY", label: "Decision Ready", color: "#38A169", desc: "Signals intent to move forward" },
  { key: "COMMITMENT", label: "Commitment", color: "#C9A227", desc: "Explicitly agrees to proceed" },
];

const MODES = {
  AUTONOMOUS: { label: "Autonomous", color: "#5B8DEF", desc: "Handling the conversation independently" },
  ALERT: { label: "Alert", color: "#D9714E", desc: "Friction detected, flagged for rep attention" },
  SHADOW: { label: "Shadow", color: "#8992A3", desc: "Drafting for human review, not sending live" },
  RELAY: { label: "Relay", color: "#C9A227", desc: "Handing off to a human closer" },
};

const STARTERS = [
  "Just checking this out, what does it do?",
  "What's the pricing look like?",
  "We already use a competitor for this.",
  "Okay — what's the next step?",
];

const SYSTEM_PROMPT = `You are the reasoning engine behind a B2B sales qualification agent called the Lead Intelligence Agent.
The user is typing AS the prospective lead. You play two roles at once:

1. SALES AGENT — write a short, natural reply (2-4 sentences) to the lead's latest message, as a competent, non-pushy sales rep.
2. TRUST CLASSIFIER — read the full conversation and classify the LEAD's current trust state and the AGENT's operating mode.

Trust states (pick exactly one key):
- AWARENESS: just learning the product exists, minimal context
- CURIOSITY: asking exploratory questions, engaged but non-committal
- HESITATION: vague stalling, unspecific doubt, no concrete reason given
- OBJECTION: a SPECIFIC counter-argument — price, timing, competitor, fit
- EVALUATION: comparing options, asking for proof, case studies, data
- TRUST_BUILDING: tone warms, asks about implementation or logistics
- DECISION_READY: signals intent to move forward, asks about next steps or contracts
- COMMITMENT: explicitly agrees or asks to proceed

Mode (pick exactly one key):
- AUTONOMOUS: default steady state
- ALERT: use when trust_state is OBJECTION or the lead sounds frustrated
- SHADOW: use when the lead explicitly asks for a human, or the message is too ambiguous to classify confidently
- RELAY: use when trust_state is DECISION_READY or COMMITMENT

Respond with ONLY a raw JSON object, no markdown fences, no preamble, matching exactly:
{"reply": "string", "trust_state": "ONE_OF_THE_KEYS_ABOVE", "rationale": "one short plain-language sentence explaining the trust read", "mode": "ONE_OF_THE_MODE_KEYS_ABOVE"}`;

function transcriptToText(messages) {
  return messages
    .map((m) => (m.role === "lead" ? `Lead: ${m.text}` : `Agent: ${m.text}`))
    .join("\n");
}

export default function LeadAgentDemo() {
  const [messages, setMessages] = useState([]);
  const [trustState, setTrustState] = useState("AWARENESS");
  const [rationale, setRationale] = useState("No signal yet — start the conversation below.");
  const [mode, setMode] = useState("AUTONOMOUS");
  const [log, setLog] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, loading]);

  const stateIndex = TRUST_STATES.findIndex((s) => s.key === trustState);
  const currentState = TRUST_STATES[stateIndex] || TRUST_STATES[0];
  const currentMode = MODES[mode] || MODES.AUTONOMOUS;

  async function send(text) {
    const clean = text.trim();
    if (!clean || loading) return;
    setError(null);
    const nextMessages = [...messages, { role: "lead", text: clean }];
    setMessages(nextMessages);
    setInput("");
    setLoading(true);

    try {
      const transcript = transcriptToText(nextMessages);
      const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-6",
          max_tokens: 1000,
          system: SYSTEM_PROMPT,
          messages: [
            {
              role: "user",
              content: `Conversation so far:\n${transcript}\n\nRespond with the JSON object only.`,
            },
          ],
        }),
      });
      const data = await res.json();
      const rawText = (data.content || [])
        .filter((b) => b.type === "text")
        .map((b) => b.text)
        .join("");
      const clean_json = rawText.replace(/```json|```/g, "").trim();
      const parsed = JSON.parse(clean_json);

      const validState = TRUST_STATES.some((s) => s.key === parsed.trust_state) ? parsed.trust_state : trustState;
      const validMode = MODES[parsed.mode] ? parsed.mode : mode;

      if (validState !== trustState || validMode !== mode) {
        setLog((prev) => [
          ...prev,
          {
            time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
            from: trustState,
            to: validState,
            mode: validMode,
          },
        ]);
      }

      setTrustState(validState);
      setRationale(parsed.rationale || "");
      setMode(validMode);
      setMessages((prev) => [...prev, { role: "agent", text: parsed.reply || "..." }]);
    } catch (e) {
      setError("Couldn't reach the model. Check the connection and try again.");
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setMessages([]);
    setTrustState("AWARENESS");
    setRationale("No signal yet — start the conversation below.");
    setMode("AUTONOMOUS");
    setLog([]);
    setError(null);
  }

  const mono = { fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" };
  const sans = { fontFamily: "ui-sans-serif, system-ui, -apple-system, sans-serif" };

  return (
    <div
      className="w-full min-h-screen flex flex-col"
      style={{ background: "#12151B", color: "#E8EAEE", ...sans }}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b" style={{ borderColor: "#2A3140" }}>
        <div>
          <div className="text-xs tracking-widest uppercase" style={{ ...mono, color: "#8992A3" }}>
            Trust Telemetry &middot; v0.1
          </div>
          <div className="text-lg font-semibold">Lead Intelligence Agent</div>
        </div>
        <button
          onClick={reset}
          className="text-xs px-3 py-2 rounded border transition"
          style={{ borderColor: "#2A3140", color: "#8992A3", ...mono }}
        >
          Reset conversation
        </button>
      </div>

      <div className="flex flex-col md:flex-row flex-1">
        {/* Transcript panel */}
        <div className="flex flex-col flex-1 border-b md:border-b-0 md:border-r" style={{ borderColor: "#2A3140" }}>
          <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-5" style={{ minHeight: "360px", maxHeight: "560px" }}>
            {messages.length === 0 && (
              <div className="text-sm" style={{ color: "#8992A3" }}>
                Type as a sales lead below. The agent replies, and its trust read updates live on the right.
              </div>
            )}
            {messages.map((m, i) => (
              <div key={i} className={`flex mb-4 ${m.role === "lead" ? "justify-end" : "justify-start"}`}>
                <div
                  className="max-w-md px-4 py-3 rounded-lg text-sm leading-relaxed"
                  style={{
                    background: m.role === "lead" ? "#1B2029" : "#182430",
                    border: `1px solid ${m.role === "lead" ? "#2A3140" : "#2D3F52"}`,
                  }}
                >
                  <div className="text-[10px] uppercase tracking-wider mb-1" style={{ ...mono, color: "#8992A3" }}>
                    {m.role === "lead" ? "Lead" : "Agent"}
                  </div>
                  {m.text}
                </div>
              </div>
            ))}
            {loading && (
              <div className="text-xs" style={{ ...mono, color: "#8992A3" }}>
                Agent is responding…
              </div>
            )}
            {error && (
              <div className="text-xs px-3 py-2 rounded" style={{ background: "#2A1B1B", color: "#D9714E" }}>
                {error}
              </div>
            )}
          </div>

          {/* Starters */}
          {messages.length === 0 && (
            <div className="px-6 pb-3 flex flex-wrap gap-2">
              {STARTERS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="text-xs px-3 py-2 rounded-full border transition"
                  style={{ borderColor: "#2A3140", color: "#8992A3" }}
                >
                  {s}
                </button>
              ))}
            </div>
          )}

          {/* Input */}
          <div className="px-6 py-4 flex gap-2 border-t" style={{ borderColor: "#2A3140" }}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send(input)}
              placeholder="Type as the lead…"
              className="flex-1 px-3 py-2 rounded text-sm outline-none"
              style={{ background: "#1B2029", border: "1px solid #2A3140", color: "#E8EAEE" }}
            />
            <button
              onClick={() => send(input)}
              disabled={loading}
              className="px-4 py-2 rounded text-sm font-medium"
              style={{ background: "#5B8DEF", color: "#0B0E13", opacity: loading ? 0.5 : 1 }}
            >
              Send
            </button>
          </div>
        </div>

        {/* Sidebar */}
        <div className="w-full md:w-[340px] flex flex-col px-6 py-5 gap-6">
          {/* Mode badge */}
          <div>
            <div className="text-[10px] uppercase tracking-widest mb-2" style={{ ...mono, color: "#8992A3" }}>
              Mode
            </div>
            <div
              className="flex items-center gap-2 px-3 py-2 rounded"
              style={{ background: "#1B2029", border: `1px solid ${currentMode.color}55` }}
            >
              <span className="inline-block rounded-full" style={{ width: 8, height: 8, background: currentMode.color }} />
              <span className="text-sm font-semibold">{currentMode.label.toUpperCase()}</span>
            </div>
            <div className="text-xs mt-1" style={{ color: "#8992A3" }}>
              {currentMode.desc}
            </div>
          </div>

          {/* Trust dial */}
          <div>
            <div className="text-[10px] uppercase tracking-widest mb-2" style={{ ...mono, color: "#8992A3" }}>
              Trust State
            </div>
            <div className="flex gap-1 mb-3">
              {TRUST_STATES.map((s, i) => (
                <div
                  key={s.key}
                  className="flex-1 rounded"
                  style={{
                    height: 8,
                    background: i <= stateIndex ? s.color : "#242A35",
                    opacity: i === stateIndex ? 1 : i < stateIndex ? 0.55 : 1,
                  }}
                  title={s.label}
                />
              ))}
            </div>
            <div className="text-base font-semibold mb-1" style={{ color: currentState.color }}>
              {currentState.label}
            </div>
            <div className="text-xs leading-relaxed" style={{ ...mono, color: "#8992A3" }}>
              {rationale}
            </div>
          </div>

          {/* Activity log */}
          <div className="flex-1 flex flex-col min-h-0">
            <div className="text-[10px] uppercase tracking-widest mb-2" style={{ ...mono, color: "#8992A3" }}>
              Activity Log
            </div>
            <div className="flex-1 overflow-y-auto flex flex-col gap-2" style={{ maxHeight: "220px" }}>
              {log.length === 0 && (
                <div className="text-xs" style={{ color: "#565D6B" }}>
                  State transitions will appear here.
                </div>
              )}
              {[...log].reverse().map((entry, i) => (
                <div key={i} className="text-xs px-2 py-1.5 rounded" style={{ ...mono, background: "#1B2029", color: "#8992A3" }}>
                  <span style={{ color: "#565D6B" }}>{entry.time}</span>{" "}
                  {TRUST_STATES.find((s) => s.key === entry.from)?.label || entry.from} →{" "}
                  <span style={{ color: TRUST_STATES.find((s) => s.key === entry.to)?.color }}>
                    {TRUST_STATES.find((s) => s.key === entry.to)?.label || entry.to}
                  </span>{" "}
                  <span style={{ color: MODES[entry.mode]?.color }}>({MODES[entry.mode]?.label})</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
