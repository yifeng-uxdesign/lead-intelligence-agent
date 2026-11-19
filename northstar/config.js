/**
 * Customer-facing copy and widget settings.
 * Change welcome text and starters here — the UI reads this object.
 */
export const WIDGET_CONFIG = {
  assistantName: "Northstar AI",
  statusLabel: "Here to help",
  welcomeMessage:
    "Hi there! I'm the Northstar AI assistant — an AI, not a person. Northstar's Lead Intelligence Agent talks with people who show interest in your product, learns what they need, and hands the right conversations to your sales team. I can explain how it works, help you see whether it fits your sales process, or answer questions about getting started. What brings you here today?",
  starters: [
    {
      id: "explore",
      label: "I'm exploring AI for lead qualification.",
      scenarioId: "curious",
    },
    {
      id: "qualify",
      label: "How does your agent qualify leads?",
      scenarioId: "promising",
    },
    {
      id: "concerns",
      label: "I have concerns about AI talking to prospects.",
      scenarioId: "hesitant",
    },
  ],
  // Typing pause in ms before each bubble: minMs..maxMs, growing with the bubble's length. Reduced motion uses 80.
  pacing: { minMs: 600, baseMs: 400, perCharMs: 6, maxMs: 1800 },
  placeholder: "Write a message…",
};
