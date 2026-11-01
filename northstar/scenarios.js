/**
 * Scripted demo scenarios for the Northstar Lead Intelligence Agent widget.
 * Presentation code imports this data; it never hardcodes replies.
 *
 * Node shape:
 *   replies:  [{ text, tone?: "cue" | "message" }]   // text may use {fit_positive} / {fit_negative}
 *   choices:  [{ id, label, next, fit?: [tag] }]      // suggested replies (fit = evidence this answer implies)
 *   routes:   [{ keywords, next, fit? }]              // free text inside this node
 *   fallback: { text, next? }                         // next omitted = stay on node
 *   captureEmail?: { company, personal }              // node that accepts a typed work email
 *
 * A `next` may be a node id, an array of node ids (played in order), "__restart__",
 * "__fit_next__" (next unanswered fit question, else the gate) or "__fit_gate__".
 *
 * PERSONA DESIGN (see DEMO_SCRIPTS.md): the five scenarios are entry points; behavior
 * adapts to what the visitor says. GLOBAL_ROUTES are checked in order, first match wins.
 */

const PERSONAL_EMAIL_DOMAINS = [
  "gmail.com", "googlemail.com", "yahoo.com", "outlook.com", "hotmail.com", "live.com",
  "msn.com", "icloud.com", "me.com", "aol.com", "proton.me", "protonmail.com", "gmx.com",
];
export { PERSONAL_EMAIL_DOMAINS };

/** Demo heuristics for "does this fit?" — illustrative, not the product's real scoring. */
export const FIT = {
  questionNodes: ["promising.scale", "promising.process", "promising.volume", "promising.outcome"],
  tagNode: {
    high_volume: "promising.scale",
    low_volume: "promising.scale",
    existing_crm: "promising.process",
    no_systems: "promising.process",
    triage_pain: "promising.volume",
    wants_automation: "promising.outcome",
    mid_volume: "promising.scale",
  },
  positive: ["high_volume", "existing_crm", "triage_pain", "wants_automation"],
  negative: ["low_volume", "no_systems"],
  confirmAt: 3,
  volume: { low: 150, high: 250 }, // inquiries per month
  phrases: {
    high_volume: "a high volume of inbound inquiries",
    existing_crm: "tools already in place for tracking them",
    triage_pain: "reps spending time sorting through inquiries by hand",
    wants_automation: "a goal of qualifying with less manual effort",
    mid_volume: "a moderate volume of inbound inquiries",
    low_volume: "a small number of inbound inquiries",
    no_systems: "no CRM or tracking tools in place yet",
  },
  patterns: {
    noSystems: /(don'?t|do not|doesn'?t|haven'?t) (really )?(have|use) (a|an|any)? ?(crm|help ?desk|tools?|systems?|software)|\bno (crm|help ?desk|tools?|systems?)\b|spreadsheet|google sheet|shared inbox|just (gmail|email)|\bgmail\b/i,
    crm: /(hubspot|salesforce|pipedrive|zoho|marketo|pardot|zendesk|intercom|freshdesk|help ?desk|\bcrm\b)/i,
    triage: /(unqualified|triage|manual(ly)?|sort(ing)? through|drowning|backlog|overwhelm|time sink|too many (leads|inquiries|requests))/i,
    automation: /(automat(e|ed|ic|ion)|without (a )?reps?|end[- ]to[- ]end|qualify (them )?for us)/i,
  },
  gate: {
    confirmed: "buyer.handoff",
    poor: "buyer.mismatch",
    unclear: "buyer.unclear",
    firstCheck: "buyer.fitcheck",
    repeatCheck: "buyer.fitcheck_again",
  },
};

export const GLOBAL_ROUTES = [
  // Persona: Frustrated. The agent stops answering on its own and hands off immediately.
  {
    id: "frustration",
    next: "alert.handoff",
    alert: true,
    patterns: [
      /frustrat|fed up|ridiculous|in circles|wits'? end|talking to (a )?wall|sick of|had enough/i,
      /(nobody|no ?one) (actually )?(listens|solves|helps|cares)/i,
      /this is (useless|pointless)|(not|n't) (listening|helping|answering)|waste of my time|wasting my time/i,
    ],
  },
  // Persona: Human Requester. Escalate immediately, no detour.
  {
    id: "human",
    next: "intervention.explain",
    patterns: [
      /(speak|talk|chat|connect|get me|put me|transfer|escalate|hand (me )?off|pass me).{0,30}(person|human|someone|somebody|\brep\b|representative|salesperson|sales team|team member)/i,
      /\bi (want|need|would like|'d like|'d rather|would rather)\b.{0,25}\b(human|real person|a person|someone|a rep)\b/i,
    ],
    keywords: [
      "sales rep", "representative", "legal", "lawyer", "counsel", "security questionnaire",
      "infosec", "soc 2", "soc2", "hipaa", "custom contract", "procurement", "authorize", "handoff",
    ],
  },
  // Persona: Skeptic. "Are you a bot?" always gets a direct answer.
  {
    id: "identity",
    next: "trust.identity",
    patterns: [
      /\b(are|r) you (actually |really |just )?(a |an )?(bot|robot|human|real person|real human|person|ai|machine|automated)\b/i,
      /\b(am i|are we) (actually |really )?(talking|speaking|chatting|typing) (to|with)\b/i,
      /\bis (this|that) (a |an )?(bot|robot|human|real person|person|ai|automated)\b/i,
      /\bis there (a |an )?(real |actual )?(human|person|bot)\b/i,
      /(bot or (a )?(person|human|real))|(person or (a )?bot)|(human or (a )?(bot|ai))|who are you|who am i (talking|speaking|chatting)/i,
      /(feels?|seems?|sounds?) (like )?(scripted|canned|robotic)|(person|human|someone|somebody) (is )?(there )?on the other (end|side)|human writing/i,
    ],
  },
  // Persona: Eager Buyer / Skeptic. Never invent a commitment.
  {
    id: "unsupported-timeline",
    next: "unsupported.timeline",
    patterns: [
      /guarantee.{0,25}(timeline|date|deadline|go-?live|live by|implementation|on time)/i,
      /(timeline|deadline|go-?live|date).{0,25}guarantee/i,
    ],
  },
  {
    id: "unsupported",
    next: "unsupported.honest",
    keywords: [
      "guarantee", "guaranteed", "100%", "always convert", "always works", "promise",
      "double our pipeline", "triple", "never fail", "sla of", "five minute sla",
      "replace our sales team", "replace the team",
    ],
  },
  // Persona: Eager Buyer / Poor Fit. A buying signal triggers a fit check, not an automatic handoff.
  {
    id: "buying",
    next: "__fit_gate__",
    patterns: [
      /ready to (move forward|buy|sign|start|go|get started|proceed)/i,
      /(get|getting) started/i,
      /(set|get) (this|it|us) (set ?up|up and running|going)/i,
      /\bsign up\b|\bpurchase\b|\bbuy (this|it)\b/i,
      /(what|where) (do|would) (we|i) (need to )?sign|can we sign|how (do|can) (we|i) (buy|purchase|sign)/i,
      /budget (is |has been )?approved|i('m| am) (already )?sold|what('s| is) the next step/i,
      /(book|set up|schedule|get) (a )?demo/i,
    ],
  },
  { id: "compare", next: "eval.compare", patterns: [/(compar(e|ing|ison)|versus|\bvs\.?\b|alternatives?|competitors?|intercom|drift|conversica|zendesk ai)/i] },
  { id: "pricing", next: "pricing.person", patterns: [/(how much (does|is|would)|\bpricing\b|\bprice\b|what('s| does| would).{0,15}cost|\bquote\b|discount)/i] },
  // Persona: Skeptic cluster.
  { id: "morework", next: "trust.morework", patterns: [/(more|extra|additional) work|create work|adds? work|adopt(ion)?\b.{0,20}(hard|painful)/i] },
  { id: "accountability", next: "trust.accountability", patterns: [/who('s| is| are) (responsible|accountable)|accountab|gets? it wrong|doesn'?t deliver|pay for a year|refund|liable/i] },
  { id: "incentive", next: "trust.incentive", patterns: [/(make money|how .{0,20}(earn|profit)|incentiv|commission|paid to|push(ing)? me|trying to (sell|get me)|say whatever)/i] },
  { id: "nosell", next: "trust.nosell", patterns: [/(not (looking|here) (for|to be)|don'?t want).{0,20}(sales? pitch|sold|pitched)|just (want|need|looking for) (some |the )?(info|information|facts)|no sales pitch|just (researching|looking)/i] },
  { id: "reviews", next: "trust.reviews", patterns: [/(reviews?|testimonials?|references?|case stud(y|ies)|customers who)/i] },
  { id: "burned", next: "trust.burned", patterns: [/(burn(ed|t)|disaster|nightmare|didn'?t work|waste of (time|money)|\b(we|i)('ve| have)? (already )?tried\b)/i] },
  { id: "skeptical", next: "trust.skeptic", patterns: [/(skeptic|sceptic|not convinced|don'?t trust|take your word|prove it|how do i know)/i] },
  { id: "privacy", next: "hesitant.privacy", patterns: [/(my data|our data|what happens to (my|our|the) data|data (is )?(stored|kept|retained|shared)|privacy|gdpr)/i] },
  { id: "setup", next: "setup.person", patterns: [/(implement(ation)?|set ?up|rollout|roll out|onboard(ing)?|disrupt(ion)?|integrat(e|ion))/i] },
  // Persona: Eager Buyer.
  { id: "urgency", next: "buyer.urgency", patterns: [/(by (the )?end of (the )?(quarter|month|year)|peak season|move fast|asap|as soon as possible|urgent(ly)?|deadline|right away|this week|need this (running|live|done))/i] },
  { id: "enthusiasm", next: ["buyer.grounded", "__fit_next__"], patterns: [/(looks|sounds|seems) (amazing|great|perfect|fantastic|incredible)|exactly (what|like)|already sold|love (this|it|what)|really impressed/i] },
  // Persona: Ghoster.
  { id: "return", next: "quiet.return", patterns: [/(sorry|got pulled|pulled (away|into)|checking back|coming back|circling back|back to this|still thinking|on my radar|haven'?t forgotten|keep meaning to|loop back)/i] },
  { id: "pilot", next: "eval.pilot", patterns: [/(pilot|next quarter|next month|next year|start(ed)? (with )?(one|a single|a small|small)|phase it|phased)/i] },
  { id: "pause", next: "pause.normalize", patterns: [/(think (about )?it|think it over|need to think|bring (this|it) back|(talk|talking|chat|chatting|speak) (to|with) my (team|boss|manager)|discuss (it |this )?with|run (it|this) by|not a good time|lot going on|bandwidth|\bbusy\b)/i] },
  { id: "stakeholder", next: "stakeholder.open", patterns: [/(my (boss|manager|cto|ceo|cfo|vp|director|leadership|team lead)|leadership|decision[- ]maker|sign[- ]off|approve (this|it)|buy[- ]in)/i] },
  { id: "product", next: "product.intro", patterns: [/(what (exactly |actually |even )?(is|does) (northstar|this|the agent|it)\b)|(what'?s northstar)|(tell me (more )?about (northstar|the agent|how))|(how (exactly |actually )?(does|do) (northstar|the agent|it|this) work)|(what do you (do|offer|sell))/i] },
  { id: "empathy", next: "empathy.ack", patterns: [/(six months|for months|nothing (has |'s )?(worked|helped|changed)|struggling|can'?t keep up|overwhelmed|drowning)/i] },
];

export const SCENARIOS = {
  curious: { id: "curious", title: "Curious visitor", entry: "curious.business" },
  hesitant: { id: "hesitant", title: "Hesitant buyer", entry: "hesitant.ack" },
  promising: { id: "promising", title: "Promising lead", entry: "qualify.explain" },
  unsupported: { id: "unsupported", title: "Unsupported commitment", entry: "unsupported.honest" },
  intervention: { id: "intervention", title: "Human intervention", entry: "intervention.explain" },
};

const RESTART = { id: "restart", label: "Restart the conversation", next: "__restart__" };

export const NODES = {
  // ============ A. Curious visitor ============
  "curious.business": {
    replies: [
      { text: "Good place to start. In one line: Northstar’s agent holds the first conversation with people interested in your product, learns what they need, and tells your sales team where a person should step in." },
      { tone: "cue", text: "I’ll ask about you first so what I say is relevant, not generic." },
      { text: "What kind of company are you evaluating this for?" },
    ],
    choices: [
      { id: "saas", label: "B2B software", next: "curious.process" },
      { id: "services", label: "Professional services", next: "curious.process" },
      { id: "other", label: "Another kind of business", next: "curious.process" },
    ],
    routes: [
      { keywords: ["saas", "software", "b2b", "product"], next: "curious.process" },
      { keywords: ["agency", "consult", "services", "firm"], next: "curious.process" },
    ],
    fallback: { text: "That still helps. If you can say the industry in a few words, I’ll use that as context.", next: "curious.process" },
  },
  "curious.process": {
    replies: [{ text: "Got it. One thing at a time: how do you currently decide which inbound leads are worth a conversation?" }],
    choices: [
      { id: "forms", label: "Forms and a score", next: "curious.contact" },
      { id: "reps", label: "Reps triage everything", next: "curious.contact", fit: ["triage_pain"] },
      { id: "none", label: "We don’t have a consistent process", next: "curious.contact" },
    ],
    routes: [
      { keywords: ["form", "score", "mql", "marketo", "hubspot"], next: "curious.contact" },
      { keywords: ["rep", "sdr", "ae", "manually", "inbox"], next: "curious.contact" },
      { keywords: ["no process", "inconsistent", "ad hoc", "chaos"], next: "curious.contact" },
    ],
    fallback: { text: "Even a rough picture is useful.", next: "curious.contact" },
  },
  "curious.contact": {
    replies: [
      { tone: "cue", text: "I’m not asking for this to close a deal. It only matters if you want a human follow-up later." },
      { text: "Would you like to share a work email for a specialist to follow up, or keep exploring here without leaving contact details?" },
    ],
    captureEmail: { company: "contact.saved", personal: "contact.personal" },
    choices: [
      { id: "email", label: "Share a work email", next: "contact.ask" },
      { id: "email-later", label: "I’ll share one later", next: "curious.close" },
      { id: "keep", label: "Keep exploring here", next: "curious.keep" },
      { id: "done", label: "That’s enough for now", next: "curious.close" },
    ],
    routes: [
      { keywords: ["email", "follow up"], next: "contact.ask" },
      { keywords: ["later", "not yet", "keep talking", "explore"], next: "curious.keep" },
    ],
    fallback: { text: "No pressure on contact details. We can stop here, or I can keep answering questions about how qualification works.", next: "curious.close" },
  },
  "curious.keep": {
    replies: [{ text: "Happy to stay in the conversation. If you want to go deeper, I can ask about your sales process next — that’s how the agent gathers evidence, one question at a time." }],
    choices: [
      { id: "deeper", label: "Ask about our sales process", next: "__fit_next__" },
      { id: "what", label: "What does Northstar do?", next: "product.intro" },
      { id: "pause", label: "That’s enough for now", next: "curious.close" },
    ],
    routes: [{ keywords: ["process", "qualify", "deeper", "more"], next: "__fit_next__" }],
    fallback: { text: "Whenever you’re ready, say what you’d like to look at next.", next: null },
  },
  "curious.close": {
    replies: [{ text: "Thank you for sharing that context. A sensible next step is a short conversation with someone on the Northstar team who can map this to your inbound flow — this prototype does not book that meeting automatically. You can restart this chat anytime, or keep asking questions here." }],
    choices: [RESTART, { id: "more", label: "I have another question", next: "curious.keep" }],
    routes: [{ keywords: ["question", "more", "how"], next: "curious.keep" }],
    fallback: { text: "I’m here if you have another question, or you can restart the chat from the header.", next: null },
  },

  // ============ B. Hesitant buyer (Skeptic) ============
  "hesitant.ack": {
    replies: [
      { text: "That’s a fair concern, and you don’t have to share anything you’re not comfortable with. I’m an AI assistant for this Northstar demo — not a person, and not a hidden script pretending to be your sales team." },
      { tone: "cue", text: "I’m naming that clearly because trust starts with knowing who you’re talking to." },
      { text: "What about AI speaking with prospects worries you most?" },
    ],
    choices: [
      { id: "tone", label: "It might pressure people", next: "hesitant.boundaries" },
      { id: "data", label: "Sharing company or contact details", next: "hesitant.privacy" },
      { id: "wrong", label: "It might say the wrong thing", next: "hesitant.boundaries" },
    ],
    routes: [
      { keywords: ["pressure", "pushy", "aggressive", "spam"], next: "hesitant.boundaries" },
      { keywords: ["wrong", "hallucin", "inaccurate", "make things up"], next: "hesitant.boundaries" },
    ],
    fallback: { text: "I hear the caution. The agent is designed to ask, not to push, and to hand off when a human should decide. Which of those worries is closest?", next: null },
  },
  "hesitant.privacy": {
    replies: [
      { text: "You can explore this product without leaving a name or email. In a real deployment, contact details would only be requested after the conversation has a clear reason — and you can decline. Nothing you type in this prototype is stored on a server." },
      { text: "Specifics such as where data is kept, how long, or how it is secured are questions a person should answer. I won’t state them from memory." },
      { text: "Would you like to keep talking about how the agent behaves, or pause here?" },
    ],
    choices: [
      { id: "keep", label: "Keep talking about behavior", next: "hesitant.boundaries" },
      { id: "person", label: "I want a person to answer data questions", next: "intervention.explain" },
      { id: "pause", label: "Pause here", next: "hesitant.close" },
    ],
    routes: [
      { keywords: ["keep", "behavior", "how"], next: "hesitant.boundaries" },
      { keywords: ["stop", "pause", "enough"], next: "hesitant.close" },
    ],
    fallback: { text: "We can stop whenever you want. No follow-up is required.", next: "hesitant.close" },
  },
  "hesitant.boundaries": {
    replies: [
      { text: "The agent’s job is to understand need, gather evidence, and notice when a human should step in. It should not invent guarantees, rush a decision, or keep pressing after someone says they’re unsure. If a question needs verification or authority, it should say so." },
      { text: "Does that address the concern, or is there another line you don’t want an AI to cross?" },
    ],
    choices: [
      { id: "addressed", label: "That helps — thanks", next: "hesitant.close" },
      { id: "another", label: "I still want a human involved", next: "intervention.explain" },
      { id: "explore", label: "Show me how qualification works", next: "qualify.explain" },
    ],
    routes: [
      { keywords: ["helps", "ok", "good", "thanks"], next: "hesitant.close" },
      { keywords: ["human", "person", "rep"], next: "intervention.explain" },
    ],
    fallback: { text: "If you’d rather a person handle this, I can explain a handoff path. This demo will not contact anyone on your behalf.", next: "intervention.explain" },
  },
  "hesitant.close": {
    replies: [{ text: "Understood. You’re in control of what you share. If you want to look at qualification later, open this chat again — there’s no urgency from me." }],
    choices: [RESTART, { id: "qualify", label: "How does qualification work?", next: "qualify.explain" }],
    routes: [{ keywords: ["qualify", "how"], next: "qualify.explain" }],
    fallback: { text: "I’m here if you have another question. No need to continue if you’d rather not.", next: null },
  },

  // ---- Skeptic nodes: validate first, answer plainly, never defend ----
  "trust.identity": {
    replies: [
      { text: "I’m an AI. There is no person typing these replies. I’m the Northstar AI assistant, and in this prototype I follow a scripted flow." },
      { tone: "cue", text: "I’m telling you directly because you should always know who you’re talking to." },
      { text: "If you’d rather deal with a person, I can set that up. Otherwise I’m glad to keep going." },
    ],
    choices: [
      { id: "person", label: "I’d like to talk to a person", next: "intervention.explain" },
      { id: "what", label: "Tell me what Northstar does", next: "product.intro" },
      { id: "later", label: "I’ll come back later", next: "quiet.later" },
    ],
    routes: [],
    fallback: { text: "Still an AI, and happy to answer anything about how this works. Or I can bring in a person.", next: null },
  },
  "trust.skeptic": {
    replies: [
      { text: "That’s a reasonable stance, and I wouldn’t ask you to take my word for anything. The most honest way to judge me is to test me." },
      { text: "What would you most want to check?" },
    ],
    choices: [
      { id: "guarantee", label: "Ask it for a guarantee", next: "unsupported.honest" },
      { id: "who", label: "Ask who you’re talking to", next: "trust.identity" },
      { id: "cant", label: "What can’t it do?", next: "hesitant.boundaries" },
    ],
    routes: [],
    fallback: { text: "Take your time. Ask for something I shouldn’t promise, ask who I am, or ask what I can’t do.", next: null },
  },
  "trust.burned": {
    replies: [
      { text: "That sounds costly, and it makes sense to raise it up front. I won’t tell you this is different — you’d have no reason to believe me yet." },
      { text: "What went wrong with the last one, as far as you could tell?" },
    ],
    choices: [
      { id: "claims", label: "It claimed things it couldn’t back up", next: "trust.honest" },
      { id: "work", label: "It created more work for us", next: "trust.morework" },
      { id: "skip", label: "I’d rather not get into it", next: "trust.nosell" },
    ],
    routes: [
      { keywords: ["claim", "promis", "overstat", "oversold", "lied"], next: "trust.honest" },
      { keywords: ["more work", "work for"], next: "trust.morework" },
    ],
    fallback: { text: "Take your time. Even one specific thing helps me understand what you’d need to see.", next: null },
  },
  "trust.honest": {
    replies: [
      { text: "That’s the failure this agent is designed around: it’s meant to keep what it knows separate from what it’s guessing, and to say so. Describing that isn’t proof, though." },
      { text: "You can test it. Ask me for a guarantee, a conversion number, or an uptime promise, and see what I do." },
    ],
    choices: [
      { id: "guarantee", label: "Ask it for a guarantee", next: "unsupported.honest" },
      { id: "else", label: "Ask something else", next: "product.intro" },
      { id: "done", label: "That’s enough for now", next: "hesitant.close" },
    ],
    routes: [],
    fallback: { text: "Try a guarantee request, or ask what I can’t do.", next: null },
  },
  "trust.morework": {
    replies: [
      { text: "That’s one of the most common ways tools like this disappoint, so it’s the right thing to press on. I don’t have deployment evidence to point to, and I won’t claim less work without it." },
      { text: "What would need to be true for this to reduce work for your team rather than add to it?" },
    ],
    choices: [
      { id: "recheck", label: "Reps shouldn’t have to re-check everything", next: "trust.reps" },
      { id: "setup", label: "Setup can’t disrupt us", next: "setup.person" },
      { id: "trust", label: "Our team has to trust what it tells prospects", next: "hesitant.boundaries" },
    ],
    routes: [
      { keywords: ["re-check", "recheck", "review", "double"], next: "trust.reps" },
      { keywords: ["setup", "disrupt", "implement"], next: "setup.person" },
    ],
    fallback: { text: "Even a rough bar helps. What would you need to see before you’d call it less work?", next: null },
  },
  "trust.reps": {
    replies: [
      { text: "That’s a fair bar. The design intent is that a person receives the context — what was said, what the agent concluded, and what it couldn’t verify — so they aren’t starting from zero or redoing the work." },
      { text: "Whether that holds for your team is something to test with a person, not something I can promise." },
    ],
    choices: [
      { id: "person", label: "I want to talk to a person about that", next: "intervention.explain" },
      { id: "ok", label: "That helps", next: "hesitant.close" },
    ],
    routes: [],
    fallback: { text: "If you want that tested rather than described, a person on the team is the right next step.", next: null },
  },
  "trust.incentive": {
    replies: [
      { text: "Fair question. Northstar sells this software, so the company benefits if you become a customer, and I’m on its website. Weigh my answers with that in mind." },
      { text: "I don’t have pricing or business-model details, and I won’t guess. What I’m designed not to do is push, mirror urgency, or promise results I can’t back up. If an answer ever feels like steering, say so." },
    ],
    choices: [
      { id: "designed", label: "What are you designed to do?", next: "product.intro" },
      { id: "person", label: "I want to talk to a person", next: "intervention.explain" },
      { id: "fair", label: "That’s fair", next: "hesitant.close" },
    ],
    routes: [],
    fallback: { text: "If anything I say feels like steering, tell me and I’ll stop.", next: null },
  },
  "trust.nosell": {
    replies: [{ text: "Understood. No pitch from me — you asked for information and I’ll keep to that. I won’t steer you toward a next step or ask for contact details. Ask whatever you like." }],
    choices: [
      { id: "how", label: "How does it work?", next: "product.intro" },
      { id: "money", label: "How does Northstar make money?", next: "trust.incentive" },
      { id: "data", label: "What happens to my data?", next: "hesitant.privacy" },
    ],
    routes: [],
    fallback: { text: "Ask whatever you like. I’ll answer only what I can support.", next: null },
  },
  "trust.accountability": {
    replies: [
      { text: "That’s a fair thing to ask before anything is signed." },
      { text: "I can’t make accountability or refund promises. That would be a commitment, and commitments belong in an agreement a person can stand behind — not in a chat with an AI." },
      { text: "What I can say is how it’s designed: it flags what it doesn’t know, and decisions with real stakes go to a person with the context. If accountability is the deciding question, a person should answer it directly." },
    ],
    choices: [
      { id: "person", label: "I want that answered by a person", next: "intervention.explain" },
      { id: "flags", label: "What does it flag exactly?", next: "hesitant.boundaries" },
      { id: "fair", label: "That’s fair", next: "hesitant.close" },
    ],
    routes: [],
    fallback: { text: "I’d rather leave that to a person than answer it badly.", next: "intervention.explain" },
  },
  "trust.reviews": {
    replies: [{ text: "It makes sense to look at reviews and to ask how a company treats people who had a bad experience. I don’t have review data or customer case history to share, so I can’t speak to it with evidence, and I won’t offer testimonials I can’t verify. A person on the team can talk about that directly." }],
    choices: [
      { id: "person", label: "I’d like to talk to a person", next: "intervention.explain" },
      { id: "keep", label: "Keep exploring", next: "product.intro" },
      { id: "fair", label: "That’s fair", next: "hesitant.close" },
    ],
    routes: [],
    fallback: { text: "I can’t verify that from here. A person can.", next: "intervention.explain" },
  },

  // ============ C. Promising lead (+ Eager Buyer, Poor Fit) ============
  "qualify.explain": {
    replies: [
      { text: "In practice it works like this. The agent starts by listening: what the person is trying to do and why now. Along the way it gathers the evidence a sales team cares about — the size of the problem, the tools and process around it, who else is involved, and timing." },
      { text: "It keeps what it knows separate from what it’s guessing. Anything it can’t verify, or that needs a person’s judgment — pricing, contracts, commitments — goes to a human." },
      { tone: "cue", text: "I’m explaining this before asking you anything, so you know what the questions are for." },
      { text: "If you like, I can ask about your sales process the way the agent would with a prospect." },
    ],
    choices: [
      { id: "ask", label: "Ask me about our sales process", next: "__fit_next__" },
      { id: "cant", label: "What can’t it do?", next: "hesitant.boundaries" },
      { id: "concern", label: "I have a concern", next: "hesitant.ack" },
    ],
    routes: [
      { keywords: ["ask", "process", "go ahead", "sure", "yes"], next: "__fit_next__" },
      { keywords: ["concern", "worry", "risk"], next: "hesitant.ack" },
    ],
    fallback: { text: "Whenever you’re ready, I can start with a question about your process, or answer something about the agent first.", next: null },
  },
  "product.intro": {
    replies: [
      { text: "Short version: Northstar’s Lead Intelligence Agent is an AI that has the first conversation with people who show interest in your product. It asks one question at a time to understand what they need, keeps track of the evidence for and against fit, says plainly that it’s an AI, and brings in a person when a decision, commitment, or sensitive question comes up." },
      { text: "It isn’t built to pressure anyone or to promise results it can’t back up. What would you most like to understand?" },
    ],
    choices: [
      { id: "qualify", label: "How it qualifies someone", next: "qualify.explain" },
      { id: "cant", label: "What it won’t do", next: "hesitant.boundaries" },
      { id: "fit", label: "Whether it fits my team", next: "__fit_next__" },
    ],
    routes: [
      { keywords: ["qualif", "how"], next: "qualify.explain" },
      { keywords: ["won't", "wont", "can't", "cant", "limit"], next: "hesitant.boundaries" },
      { keywords: ["fit", "my team", "my company"], next: "__fit_next__" },
    ],
    fallback: { text: "Say what you’d like to look at first and I’ll start there.", next: null },
  },
  "promising.scale": {
    replies: [
      { tone: "cue", text: "Volume tells me whether a conversation like this is worth your time, so I’m asking early." },
      { text: "Roughly how many inbound inquiries do you get in a typical month?" },
    ],
    choices: [
      { id: "few", label: "A few dozen or fewer", next: "__fit_next__", fit: ["low_volume"] },
      { id: "hundreds", label: "A few hundred", next: "__fit_next__", fit: ["high_volume"] },
      { id: "thousands", label: "Over a thousand", next: "__fit_next__", fit: ["high_volume"] },
      { id: "unsure", label: "I’m not sure", next: "__fit_next__" },
    ],
    routes: [
      { keywords: ["dozen", "handful", "very few"], next: "__fit_next__", fit: ["low_volume"] },
      { keywords: ["hundred", "thousand"], next: "__fit_next__", fit: ["high_volume"] },
    ],
    fallback: { text: "A rough guess is fine. I’m only using it to see whether this fits.", next: "__fit_next__" },
  },
  "promising.process": {
    replies: [
      { tone: "cue", text: "I’ll ask one useful question at a time so this stays a conversation, not a form." },
      { text: "When a new inbound inquiry comes in, what happens first on your team?" },
    ],
    choices: [
      { id: "sdr", label: "An SDR reviews it", next: "__fit_next__", fit: ["triage_pain"] },
      { id: "auto", label: "It hits a sequence automatically", next: "__fit_next__", fit: ["existing_crm"] },
      { id: "inbox", label: "One person reads a shared inbox", next: "__fit_next__", fit: ["no_systems"] },
    ],
    routes: [
      { keywords: ["sdr", "bdr", "review", "triage"], next: "__fit_next__", fit: ["triage_pain"] },
      { keywords: ["sequence", "cadence", "automatic", "nurture"], next: "__fit_next__", fit: ["existing_crm"] },
      { keywords: ["founder", "ae", "account exec", "i handle", "inbox"], next: "__fit_next__" },
    ],
    fallback: { text: "Even a simple description works.", next: "__fit_next__" },
  },
  "promising.volume": {
    replies: [{ text: "What’s the harder problem today: too many unqualified inquiries, too few that are ready, or inconsistency in how they’re judged?" }],
    choices: [
      { id: "unqualified", label: "Too many unqualified inquiries", next: "__fit_next__", fit: ["triage_pain"] },
      { id: "few", label: "Too few that are actually ready", next: "__fit_next__" },
      { id: "inconsistent", label: "Judgment is inconsistent", next: "__fit_next__", fit: ["triage_pain"] },
    ],
    routes: [
      { keywords: ["unqualified", "junk", "spam", "volume"], next: "__fit_next__", fit: ["triage_pain"] },
      { keywords: ["few", "ready", "quality", "pipeline"], next: "__fit_next__" },
      { keywords: ["inconsistent", "subjective", "varies"], next: "__fit_next__", fit: ["triage_pain"] },
    ],
    fallback: { text: "I’ll treat that as a qualification-quality problem unless you say otherwise.", next: "__fit_next__" },
  },
  "promising.outcome": {
    replies: [{ text: "Last question from me on this thread: what would a better outcome look like — more time for reps on fit conversations, fewer wasted follow-ups, or a clearer picture of who is actually ready?" }],
    choices: [
      { id: "time", label: "More time for fit conversations", next: "__fit_next__", fit: ["wants_automation"] },
      { id: "waste", label: "Fewer wasted follow-ups", next: "__fit_next__", fit: ["triage_pain"] },
      { id: "picture", label: "A clearer picture of readiness", next: "__fit_next__", fit: ["wants_automation"] },
    ],
    routes: [
      { keywords: ["time", "rep", "conversation"], next: "__fit_next__", fit: ["wants_automation"] },
      { keywords: ["waste", "follow-up", "follow up"], next: "__fit_next__", fit: ["triage_pain"] },
      { keywords: ["picture", "ready", "signal", "visibility"], next: "__fit_next__", fit: ["wants_automation"] },
    ],
    fallback: { text: "That’s enough to describe a responsible next step.", next: "__fit_next__" },
  },

  "fit.ack": {
    replies: [{ text: "Thank you, that helps. I’ve noted {fit_new}." }],
    choices: [],
    routes: [],
  },
  "buyer.grounded": {
    replies: [
      { text: "Thank you. I’d rather understand your situation than assume it, so I’ll ask a few questions before we talk about anything else." },
      { tone: "cue", text: "Asking first protects you from committing to something that doesn’t fit." },
    ],
    choices: [],
    routes: [],
  },
  "buyer.fitcheck": {
    replies: [
      { tone: "cue", text: "I’m not slowing you down for its own sake. I only suggest a next step once there’s evidence it fits." },
      { text: "I don’t have enough yet to say Northstar fits your situation, so I’d rather ask than assume." },
    ],
    choices: [],
    routes: [],
  },
  "buyer.fitcheck_again": {
    replies: [{ text: "I hear that you’re ready. I still don’t have enough to say this fits, and a next step built on enthusiasm instead of evidence wouldn’t serve you. One more question." }],
    choices: [],
    routes: [],
  },
  "buyer.handoff": {
    replies: [
      { tone: "cue", text: "I’m suggesting a person now because the evidence supports it, not because I’m trying to close." },
      { text: "Here’s what I’ve heard: {fit_positive}. That’s enough for me to say a conversation with the Northstar team makes sense." },
      { text: "Pricing, contract terms, and timelines are theirs to answer, and I won’t quote any. I can pass this along — in this prototype that’s simulated, so no one will actually be contacted." },
    ],
    captureEmail: { company: "contact.saved", personal: "contact.personal" },
    choices: [
      { id: "email", label: "Share a work email", next: "contact.ask" },
      { id: "later", label: "Not yet", next: "buyer.later" },
      { id: "more", label: "Keep asking questions", next: "product.intro" },
    ],
    routes: [
      { keywords: ["email", "yes", "pass it", "go ahead"], next: "contact.ask" },
      { keywords: ["later", "not yet", "no"], next: "buyer.later" },
    ],
    fallback: { text: "No rush. I can pass this along whenever you’re ready, or we can keep talking.", next: null },
  },
  "buyer.mismatch": {
    replies: [
      { tone: "cue", text: "I’d rather say this now than after you’ve put time into it." },
      { text: "From what you’ve told me — {fit_negative} — Northstar probably isn’t the right fit yet. At that scale a person answering each inquiry is likely better than software, and I don’t want you paying for something you wouldn’t use. That isn’t a judgment of your company; it’s about timing." },
      { text: "I can’t give you a verified volume where it starts to make sense. A person on the team could. If your inbound grows, it’s worth revisiting." },
    ],
    choices: [
      { id: "grow", label: "I expect volume to grow soon", next: "buyer.growth" },
      { id: "fair", label: "That’s fair, thanks", next: "buyer.later" },
      { id: "what", label: "What does Northstar do?", next: "product.intro" },
    ],
    routes: [{ keywords: ["grow", "scaling", "soon"], next: "buyer.growth" }],
    fallback: { text: "I’d still rather be straight with you than say yes. If you’d like a person to weigh in, I can note that.", next: null },
  },
  "buyer.growth": {
    replies: [{ text: "That’s useful context. I won’t push you either way. A person could tell you roughly where this starts to pay off, and you’re welcome to come back when it’s closer." }],
    captureEmail: { company: "contact.saved", personal: "contact.personal" },
    choices: [
      { id: "email", label: "Share a work email", next: "contact.ask" },
      { id: "ok", label: "Okay, thanks", next: "buyer.later" },
    ],
    routes: [],
    fallback: { text: "No pressure. You can come back whenever it’s relevant.", next: "buyer.later" },
  },
  "buyer.unclear": {
    replies: [{ text: "I have part of the picture, but not enough to call this a fit or not, and I don’t want to guess. A person on the team can look at it with you, or we can keep talking here." }],
    choices: [
      { id: "person", label: "I’d like a person to look at it", next: "intervention.explain" },
      { id: "keep", label: "Keep talking here", next: "product.intro" },
    ],
    routes: [],
    fallback: { text: "Either works. I just won’t guess at fit.", next: null },
  },
  "buyer.urgency": {
    replies: [
      { tone: "cue", text: "I’m separating your timeline from what I can promise." },
      { text: "A deadline like that is useful to know, and I’ll treat it as your target. Go-live timing depends on things I can’t see from here — your tools, your process, who needs to approve — and I don’t have verified implementation details. A person should answer timing with you." },
    ],
    choices: [
      { id: "person", label: "I want to talk to a person", next: "intervention.explain" },
      { id: "know", label: "What would a person need to know?", next: "__fit_next__" },
      { id: "keep", label: "Keep exploring", next: "product.intro" },
    ],
    routes: [],
    fallback: { text: "I’ll leave your timeline with the people who can speak to it.", next: null },
  },
  "buyer.later": {
    replies: [{ text: "Understood. Nothing is lost by waiting, and there’s no deadline from my side." }],
    choices: [RESTART, { id: "what", label: "What does Northstar do?", next: "product.intro" }],
    routes: [],
    fallback: { text: "I’m here if you want to pick this up later.", next: null },
  },

  // ============ D. Unsupported commitment ============
  "unsupported.honest": {
    replies: [
      { text: "I can’t agree to that. I don’t have evidence for guarantees, conversion promises, or technical commitments that haven’t been verified for your environment." },
      { tone: "cue", text: "If I invented a number or an SLA here, that would be a claim — not qualification." },
      { text: "What I can do is explain how the agent is supposed to behave, and connect you with a person when a commitment needs to be real. What would be most useful?" },
    ],
    choices: [
      { id: "explain", label: "Explain how the agent behaves", next: "qualify.explain" },
      { id: "human", label: "I need a human for this", next: "intervention.explain" },
      { id: "ok", label: "Understood", next: "unsupported.close" },
    ],
    routes: [
      { keywords: ["behave", "how", "qualify"], next: "qualify.explain" },
      { keywords: ["human", "person", "legal"], next: "intervention.explain" },
    ],
    fallback: { text: "I still can’t make that commitment. A person on the team would need to review anything contractual.", next: "intervention.explain" },
  },
  "unsupported.timeline": {
    replies: [
      { text: "I can’t guarantee that timeline. Go-live depends on your tools, your process, and who needs to approve it, and I don’t have verified implementation details for your environment." },
      { tone: "cue", text: "Saying yes here would be a claim, not an answer." },
      { text: "I can note your target date and have a person review whether it’s realistic. What would you like?" },
    ],
    choices: [
      { id: "note", label: "Have a person review my target date", next: "intervention.explain" },
      { id: "explain", label: "Explain how the agent behaves", next: "qualify.explain" },
      { id: "ok", label: "Understood", next: "unsupported.close" },
    ],
    routes: [{ keywords: ["person", "human", "review", "note"], next: "intervention.explain" }],
    fallback: { text: "I still can’t promise a date. A person can look at what’s realistic.", next: "intervention.explain" },
  },
  "unsupported.close": {
    replies: [{ text: "Good. I’d rather leave a gap than fill it with a claim. Ask another question, or restart if you want a different path." }],
    choices: [RESTART, { id: "qualify", label: "How does qualification work?", next: "qualify.explain" }],
    routes: [{ keywords: ["qualify", "how"], next: "qualify.explain" }],
    fallback: { text: "I’m here for questions I can actually answer.", next: null },
  },

  // ============ E. Human intervention (Human Requester) ============
  "intervention.again": {
    replies: [
      { text: "Understood. A person is the right next step." },
      { text: "In this prototype the handoff is simulated, so no one has actually been contacted. You can share a work email, leave a note, or stop here." },
    ],
    choices: [
      { id: "email", label: "Share a work email", next: "contact.ask" },
      { id: "note", label: "Leave a note without contact details", next: "intervention.noted" },
      { id: "stop", label: "Stop here", next: "intervention.close" },
    ],
    routes: [
      { keywords: ["email", "contact"], next: "contact.ask" },
      { keywords: ["note", "handoff", "leave"], next: "intervention.noted" },
    ],
    fallback: { text: "A person should take this from here. I can leave a simulated note so you can see the pattern.", next: "intervention.noted" },
  },
  "intervention.explain": {
    repeat: "intervention.again",
    replies: [
      { text: "Of course. A person should help with this: legal review, security questionnaires, authorization, live commercial commitments, or simply wanting to talk with someone are all outside what I should settle in chat." },
      { tone: "cue", text: "I’m flagging that so you aren’t left talking to an assistant about something that needs a human." },
      { text: "I can describe a handoff path. In this prototype, that path is simulated — I will not contact a real sales representative." },
    ],
    choices: [
      { id: "email", label: "Share a work email", next: "contact.ask" },
      { id: "note", label: "Leave a note without contact details", next: "intervention.noted" },
      { id: "continue", label: "Keep exploring for now", next: "product.intro" },
      { id: "stop", label: "Stop here", next: "intervention.close" },
    ],
    routes: [
      { keywords: ["email", "contact"], next: "contact.ask" },
      { keywords: ["note", "handoff", "leave"], next: "intervention.noted" },
      { keywords: ["continue", "explore", "product"], next: "product.intro" },
    ],
    fallback: { text: "If you want a human involved for real, that would happen outside this demo. I can still leave a simulated note so you can see the pattern.", next: "intervention.noted" },
  },
  "intervention.noted": {
    replies: [{ text: "Simulated note filed: a specialist should review this thread before any commitment. No one has been contacted. You can restart, keep exploring, or close the widget." }],
    choices: [RESTART, { id: "explore", label: "Keep exploring", next: "product.intro" }],
    routes: [{ keywords: ["explore", "more"], next: "product.intro" }],
    fallback: { text: "The simulated note is the end of this handoff path. Restart anytime.", next: null },
  },
  "intervention.close": {
    replies: [{ text: "That’s a reasonable place to stop. A human should own the next step when you’re ready — not this chat." }],
    choices: [RESTART],
    routes: [],
    fallback: { text: "You can close the widget or restart from the header.", next: null },
  },

  // ---- Contact capture: only after real interest, company email only ----
  "contact.ask": {
    replies: [
      { tone: "cue", text: "I’m asking for a work email only so a person can follow up. This prototype does not store or send it." },
      { text: "Type a work email, or skip for now." },
    ],
    captureEmail: { company: "contact.saved", personal: "contact.personal" },
    choices: [{ id: "skip", label: "Skip for now", next: "intervention.noted" }],
    routes: [{ keywords: ["skip", "no", "later", "not now"], next: "intervention.noted" }],
    fallback: { text: "A work address like name@yourcompany.com is all that’s needed, or you can skip.", next: null },
  },
  "contact.personal": {
    replies: [{ text: "That looks like a personal address. A work email helps a specialist match this conversation to your company. Would you share a work address instead, or skip?" }],
    captureEmail: { company: "contact.saved", personal: "contact.personal" },
    choices: [{ id: "skip", label: "Skip for now", next: "intervention.noted" }],
    routes: [{ keywords: ["skip", "no", "later", "not now"], next: "intervention.noted" }],
    fallback: { text: "Just a work address, or skip. Either is fine.", next: null },
  },
  "contact.saved": {
    replies: [{ text: "Simulated: a specialist would receive this thread and your work email, so you wouldn’t have to repeat yourself. In this prototype nothing was stored or sent, and no one has been contacted." }],
    choices: [RESTART, { id: "more", label: "Keep exploring", next: "product.intro" }],
    routes: [],
    fallback: { text: "That’s the end of the simulated handoff. Restart anytime.", next: null },
  },

  // ============ Frustrated: ALERT. The agent stops answering on its own ============
  "alert.handoff": {
    replies: [
      { text: "I’m sorry. Going in circles isn’t acceptable, and you shouldn’t have to keep repeating yourself." },
      { tone: "cue", text: "I’m stepping back because a person can do something I can’t: take responsibility for solving this with you." },
      { text: "I’m going to stop trying to handle this myself and ask a person on the team to take it from here. In this prototype that handoff is simulated — no one has actually been contacted." },
    ],
    choices: [{ id: "note", label: "Leave a simulated note for the team", next: "alert.noted" }, RESTART],
    routes: [],
  },
  "alert.noted": {
    replies: [{ text: "Simulated note filed for a person to pick up: you’re frustrated, you’ve been going in circles, and the agent should not carry on alone. No one has been contacted." }],
    choices: [RESTART],
    routes: [],
    fallback: { text: "That’s the end of the simulated handoff. A person, not this chat, should pick up from here.", next: null },
  },
  "alert.hold": {
    replies: [{ text: "I’m holding here so a person can take this over. I won’t keep answering on my own, because that isn’t what would help." }],
    choices: [{ id: "note", label: "Leave a simulated note for the team", next: "alert.noted" }, RESTART],
    routes: [],
    fallback: { text: "Still holding for a person. I’m not going to answer product questions in the meantime.", next: null },
  },

  // ============ Evaluation, setup, pricing, stakeholders ============
  "setup.person": {
    replies: [{ text: "It makes sense to worry about disruption. I don’t have verified details about setup effort or timelines, and I won’t guess. That’s a question for a person who can look at your tools and process with you." }],
    choices: [
      { id: "person", label: "I want to talk to a person", next: "intervention.explain" },
      { id: "small", label: "We could start with one small area", next: "eval.pilot" },
      { id: "keep", label: "Keep exploring", next: "product.intro" },
    ],
    routes: [],
    fallback: { text: "I can’t answer setup questions reliably. A person can.", next: "intervention.explain" },
  },
  "pricing.person": {
    replies: [
      { text: "I don’t have verified pricing, and I won’t guess. Pricing and terms are something a person on the team should give you directly." },
      { tone: "cue", text: "Anything about money or contract terms is a commitment, so it shouldn’t come from me." },
    ],
    choices: [
      { id: "person", label: "I want to talk to a person", next: "intervention.explain" },
      { id: "keep", label: "Keep exploring", next: "product.intro" },
    ],
    routes: [],
    fallback: { text: "I can’t quote anything. A person can.", next: "intervention.explain" },
  },
  "eval.compare": {
    replies: [{ text: "Comparing options is the right way to decide. I can only speak to what Northstar is designed to do, not how other products behave — I haven’t verified their claims and I won’t guess. What would you compare on?" }],
    choices: [
      { id: "honesty", label: "How it handles honesty and handoffs", next: "hesitant.boundaries" },
      { id: "fit", label: "Fit with our sales process", next: "__fit_next__" },
      { id: "setup", label: "Setup effort", next: "setup.person" },
    ],
    routes: [],
    fallback: { text: "Tell me one thing that matters most to you and I’ll stay with that.", next: null },
  },
  "eval.pilot": {
    replies: [
      { text: "Having your own timeline is a good way to do this. It leaves room to look at it properly. There’s nothing for you to decide today, and I won’t try to bring your date forward." },
      { text: "When you do get to it, what would you want it to show first?" },
    ],
    choices: [
      { id: "time", label: "Less rep time on unqualified leads", next: "eval.pilot_next", fit: ["triage_pain"] },
      { id: "ai", label: "That prospects aren’t put off by an AI", next: "eval.pilot_next" },
      { id: "handoff", label: "That it hands off to us correctly", next: "eval.pilot_next" },
    ],
    routes: [{ keywords: ["pilot", "explore", "look like", "show"], next: "eval.pilot_next" }],
    fallback: { text: "No need to answer now. It’s a useful question to carry with you.", next: null },
  },
  "eval.pilot_next": {
    replies: [{ text: "That’s a clear way to frame it. A person on the team can help define what a pilot would involve and what “working” would look like. I can’t scope or schedule it myself, and this prototype won’t book anything." }],
    captureEmail: { company: "contact.saved", personal: "contact.personal" },
    choices: [
      { id: "email", label: "Share a work email", next: "contact.ask" },
      { id: "later", label: "Not now", next: "quiet.later" },
    ],
    routes: [],
    fallback: { text: "No rush. This will keep.", next: "quiet.later" },
  },
  "stakeholder.open": {
    replies: [{ text: "That’s a normal part of deciding. Whose approval matters most, and what would they want to be sure of?" }],
    choices: [
      { id: "safe", label: "Whether it’s safe in front of prospects", next: "hesitant.boundaries" },
      { id: "cost", label: "Cost and effort", next: "pricing.person" },
      { id: "summary", label: "I’d rather give them a short summary", next: "share.summary" },
    ],
    routes: [],
    fallback: { text: "Even a rough sense of their concern helps. Or I can write something short you can pass along.", next: null },
  },

  // ============ Ghoster: patient, no urgency ============
  "quiet.patient": {
    replies: [{ text: "No rush at all. I’m here whenever you want to pick this up, and it’s completely fine not to." }],
    choices: [
      { id: "what", label: "What does Northstar do?", next: "product.intro" },
      { id: "later", label: "I’ll come back later", next: "quiet.later" },
    ],
    routes: [],
    fallback: { text: "Still here, no pressure.", next: null },
  },
  "quiet.return": {
    replies: [{ text: "No problem at all. Things come up. We can pick this up wherever suits you, or leave it as it is." }],
    choices: [
      { id: "remind", label: "Remind me what Northstar does", next: "product.intro" },
      { id: "later", label: "Leave it for now", next: "quiet.later" },
    ],
    routes: [],
    fallback: { text: "No pressure either way.", next: null },
  },
  "quiet.later": {
    replies: [{ text: "That works. Nothing is saved or scheduled, and there’s no follow-up from me. Open the chat any time." }],
    choices: [RESTART],
    routes: [],
    fallback: { text: "Open the chat whenever you like.", next: null },
  },
  "pause.normalize": {
    replies: [
      { text: "Taking time to think, and bringing your team in, is a sensible way to make this kind of decision. There’s no clock on my side." },
      { text: "If it helps, I can put the essentials in a few lines you can share with them." },
    ],
    choices: [
      { id: "summary", label: "Give me a few lines to share", next: "share.summary" },
      { id: "later", label: "I’ll come back later", next: "quiet.later" },
      { id: "q", label: "I have a question first", next: "product.intro" },
    ],
    routes: [],
    fallback: { text: "No pressure to decide anything now.", next: null },
  },
  "share.summary": {
    replies: [
      { text: "Here’s a version you can pass along:" },
      { text: "Northstar’s Lead Intelligence Agent is an AI that holds the first conversation with people interested in your product. It asks one question at a time to understand their need, gathers qualification evidence, and is clear that it’s an AI. It doesn’t invent guarantees or pressure people, and it hands conversations to a person when a decision, commitment, or sensitive question comes up. Pricing, contract terms, and timelines come from the Northstar team, not the AI." },
      { text: "This chat itself is a scripted prototype." },
    ],
    choices: [{ id: "thanks", label: "Thanks", next: "quiet.later" }, RESTART],
    routes: [],
    fallback: { text: "That’s all I have. A person on the team can say more.", next: null },
  },
  "empathy.ack": {
    replies: [
      { text: "That sounds exhausting, and I’m not going to jump to a solution." },
      { text: "Where has it been hardest — getting inquiries that are worth your time, or dealing with the ones that come in?" },
    ],
    choices: [
      { id: "noise", label: "Too many that go nowhere", next: "__fit_next__", fit: ["triage_pain"] },
      { id: "few", label: "Not enough that are ready", next: "__fit_next__" },
      { id: "person", label: "I’d rather talk to a person", next: "intervention.explain" },
    ],
    routes: [],
    fallback: { text: "Take your time. I’m listening.", next: null },
  },
};
