import { useEffect, useMemo, useRef, useState, type CSSProperties } from "react"

type IconName = "alert" | "building" | "settings" | "history" | "chevron" | "spark" | "close" | "search" | "send" | "check" | "clock" | "more" | "user" | "back" | "evidence"

const iconPaths: Record<IconName, React.ReactNode> = {
  alert: <path d="M12 3 2.8 20h18.4L12 3Zm0 6v5m0 3h.01" />,
  building: <path d="M4 21V4h10v17M8 8h2m-2 4h2m-2 4h2m6-6h4v11M3 21h19" />,
  settings: (
    <path d="M12 15.2a3.2 3.2 0 1 0 0-6.4 3.2 3.2 0 0 0 0 6.4Zm8-3.2 1.5-1.2-2-3.5-1.9.7a7 7 0 0 0-1.8-1L15.5 5h-4L11 7a7 7 0 0 0-1.8 1l-1.9-.7-2 3.5L6.8 12a7 7 0 0 0 0 2l-1.5 1.2 2 3.5 1.9-.7a7 7 0 0 0 1.8 1l.5 2h4l.5-2a7 7 0 0 0 1.8-1l1.9.7 2-3.5-1.5-1.2a7 7 0 0 0 0-2Z" />
  ),
  history: <path d="M4 5v5h5M5.2 9A8 8 0 1 1 4 13m8-5v5l3 2" />,
  chevron: <path d="m9 18 6-6-6-6" />,
  spark: (
    <path d="m12 2 1.4 5.1L18 9l-4.6 1.9L12 16l-1.4-5.1L6 9l4.6-1.9L12 2Zm7 13 .7 2.3L22 18l-2.3.7L19 21l-.7-2.3L16 18l2.3-.7L19 15Z" />
  ),
  close: <path d="m6 6 12 12M18 6 6 18" />,
  search: (
    <path d="m21 21-4.4-4.4m2.4-5.1a7.5 7.5 0 1 1-15 0 7.5 7.5 0 0 1 15 0Z" />
  ),
  send: <path d="m22 2-8.2 20-3.1-8.7L2 10.2 22 2Zm-11.3 11.3L22 2" />,
  check: <path d="m5 12 4 4L19 6" />,
  clock: <path d="M12 7v5l3 2m6-2a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />,
  more: <path d="M5 12h.01M12 12h.01M19 12h.01" />,
  user: <path d="M20 21a8 8 0 0 0-16 0m8-10a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z" />,
  back: <path d="m15 18-6-6 6-6" />,
  evidence: <path d="M4 3h12l4 4v14H4V3Zm12 0v5h5M8 13h8m-8 4h6" />,
}

function Icon({ name, size = 18 }: { name: IconName size?: number }) {
  return (
    <svg
      aria-hidden="true"
      className="icon"
      fill="none"
      height={size}
      viewBox="0 0 24 24"
      width={size}
    >
      {iconPaths[name]}
    </svg>
  )
}

const leads = [
  {
    name: "Maya Chen",
    initials: "MC",
    company: "Northstar Labs",
    reason: "Approval-authority conflict",
    detail: "Budget owner differs from the signer named in the approval flow.",
    score: 92,
    waiting: "3d 4h",
    tone: "critical",
    escalated: true,
  },
  {
    name: "Daniel Okafor",
    initials: "DO",
    company: "Lumon Industries",
    reason: "Economic buyer unconfirmed",
    detail: "Need your context on who holds final purchasing authority.",
    score: 86,
    waiting: "1d 18h",
    tone: "high",
  },
  {
    name: "Priya Raman",
    initials: "PR",
    company: "Aperture Systems",
    reason: "Compliance question",
    detail: "Agent needs approval before sharing the data residency brief.",
    score: 78,
    waiting: "19h",
    tone: "medium",
  },
  {
    name: "Sarah Lindqvist",
    initials: "SL",
    company: "Northwind Health",
    reason: "Economic buyer unconfirmed",
    detail: "Customer and CRM name different final approvers.",
    score: 81,
    waiting: "7h",
    tone: "low",
  },
]

const accounts = [
  ["Northwind Health", 2, 1, "10:30", "Jordan Bell"],
  ["Northstar Labs", 1, 1, "Yesterday", "Jordan Bell"],
  ["Lumon Industries", 1, 1, "Yesterday", "Jordan Bell"],
  ["Aperture Systems", 1, 1, "Oct 1", "Jordan Bell"],
  ["Sable & Co.", 1, 0, "Sep 30", "Jordan Bell"],
  ["Vertex Health", 0, 0, "Sep 27", "Jordan Bell"],
]

const Button = ({
  children,
  variant = "secondary",
  disabled,
  onClick,
  title,
}: {
  children: React.ReactNode
  variant?: "primary" | "secondary" | "quiet" | "danger"
  disabled?: boolean
  onClick?: () => void
  title?: string
}) => (
  <button
    className={`button ${variant}`}
    disabled={disabled}
    onClick={onClick}
    title={title}
    type="button"
  >
    {children}
  </button>
)

const Badge = ({
  children,
  tone = "neutral",
}: {
  children: React.ReactNode
  tone?: string
}) => <span className={`badge ${tone}`}>{children}</span>

function Rail({
  page,
  navigate,
}: {
  page: string
  navigate: (page: string) => void
}) {
  return (
    <nav className="rail" aria-label="Workspace">
      <button className="logo" aria-label="Workspace" title="Workspace">
        <Icon name="spark" size={22} />
      </button>
      <div className="rail-main">
        <button
          aria-label="Needs your attention"
          className={`rail-item ${page === "queue" ? "active" : ""}`}
          onClick={() => navigate("queue")}
          title="Needs your attention"
        >
          <Icon name="alert" />
          <span className="rail-count">4</span>
        </button>
        <button
          aria-label="Accounts"
          className={`rail-item ${
            page.includes("account") || page === "lead" ? "active" : ""
          }`}
          onClick={() => navigate("accounts")}
          title="Accounts"
        >
          <Icon name="building" />
        </button>
      </div>
      <div className="rail-footer">
        <button
          className="avatar small"
          aria-label="Jordan Bell"
          title="Jordan Bell"
        >
          JB
        </button>
        <button className="rail-item" aria-label="Settings" title="Settings">
          <Icon name="settings" />
        </button>
      </div>
    </nav>
  )
}

function Glance() {
  const modes = [
    ["7", "Agent-led"],
    ["4", "Needs review"],
    ["3", "Advisory"],
    ["1", "You're driving"],
  ]
  return (
    <section className="glance" aria-label="At a glance">
      <div className="glance-dominant">
        <div className="metric-number">4</div>
        <div>
          <strong>Need your review</strong>
          <span>Oldest waiting 3d 4h</span>
        </div>
      </div>
      <div className="glance-metric modes">
        <span className="metric-label">Lead modes</span>
        <div className="mode-grid">
          {modes.map(([count, label]) => (
            <span key={label}>
              <b>{count}</b> {label}
            </span>
          ))}
        </div>
      </div>
      <div className="glance-metric">
        <span className="metric-label">Active leads</span>
        <strong className="metric-value">15</strong>
        <span className="positive">+3 this week</span>
      </div>
      <div className="glance-metric">
        <span className="metric-label">Inquiry → lead</span>
        <strong className="metric-value">31.8%</strong>
        <span className="positive">+2.4% vs prior 30d</span>
      </div>
    </section>
  )
}

function QueuePage({ openLead }: { openLead: () => void }) {
  const [filter, setFilter] = useState("All blockers")
  const visible = useMemo(
    () =>
      filter === "All blockers"
        ? leads
        : leads.filter((lead) =>
            lead.reason
              .toLowerCase()
              .includes(filter.toLowerCase().replace(" authority", "")),
          ),
    [filter],
  )
  return (
    <main className="canvas">
      <header className="page-header">
        <span className="eyebrow">
          {new Intl.DateTimeFormat("en", {
            weekday: "long",
            month: "long",
            day: "numeric",
          }).format(new Date())}
        </span>
        <h1>Needs your attention</h1>
        <p>Clear the blockers your agent can't resolve without you.</p>
      </header>
      <Glance />
      <div className="section-heading">
        <div>
          <h2>Lead blockers</h2>
          <p>Oldest waiting first</p>
        </div>
        <div className="button-group" aria-label="Filter blockers">
          {[
            "All blockers",
            "Approval authority",
            "Economic buyer",
            "Compliance",
          ].map((item) => (
            <button
              className={filter === item ? "selected" : ""}
              key={item}
              onClick={() => setFilter(item)}
              type="button"
            >
              {item}
            </button>
          ))}
        </div>
      </div>
      <div className="record-list">
        {visible.length ? (
          visible.map((lead) => (
            <button
              className="record-row"
              key={lead.name}
              onClick={openLead}
              type="button"
            >
              <div className="identity">
                <span className="avatar">{lead.initials}</span>
                <span>
                  <strong>{lead.name}</strong>
                  <small>{lead.company}</small>
                </span>
              </div>
              <div className="blocker-copy">
                <strong>{lead.reason}</strong>
                <span>{lead.detail}</span>
              </div>
              <div className="row-meta">
                <span className="score">
                  <small>Score</small>
                  <b>{lead.score}</b>
                </span>
                <span className="waiting-stack">
                  <Badge tone={lead.tone}>
                    <Icon name="clock" size={14} /> {lead.waiting}
                  </Badge>
                  {lead.escalated && (
                    <Badge tone="warning">Escalated to manager</Badge>
                  )}
                </span>
                <Icon name="chevron" />
              </div>
            </button>
          ))
        ) : (
          <div className="empty-state">
            <div className="empty-illustration">
              <Icon name="check" size={32} />
            </div>
            <h2>You're caught up</h2>
            <p>No leads match this blocker.</p>
            <Button variant="quiet">View Accounts</Button>
          </div>
        )}
      </div>
      <p className="footnote">
        Escalation and archive timing are configurable. Archived leads leave
        this queue, but the agent keeps working them.
      </p>
    </main>
  )
}

function AccountsPage({ openAccount }: { openAccount: () => void }) {
  const [query, setQuery] = useState("")
  return (
    <main className="canvas">
      <header className="page-header compact">
        <span className="eyebrow">Workspace</span>
        <h1>Accounts</h1>
        <p>Accounts sorted by most recent activity.</p>
      </header>
      <div className="toolbar">
        <label className="search-box">
          <Icon name="search" />
          <input
            aria-label="Search accounts"
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search accounts"
            value={query}
          />
        </label>
        <label className="select-box">
          <span>Lead mode</span>
          <select defaultValue="All modes">
            <option>All modes</option>
            <option>Agent-led</option>
            <option>Needs review</option>
            <option>Advisory</option>
            <option>You're driving</option>
          </select>
        </label>
      </div>
      <div className="record-list account-list">
        {accounts
          .filter(([name]) => name.toLowerCase().includes(query.toLowerCase()))
          .map(([name, active, review, activity, owner]) => (
            <button
              className="record-row account-row"
              key={name}
              onClick={openAccount}
            >
              <div className="identity">
                <span className="account-icon">
                  <Icon name="building" />
                </span>
                <strong>{name}</strong>
              </div>
              <span>
                <small>Active leads</small>
                <b>{active}</b>
              </span>
              <span>
                <small>Needs review</small>
                <b>{review}</b>
              </span>
              <span>
                <small>Last activity</small>
                <b>{activity}</b>
              </span>
              <span>
                <small>Owner</small>
                <b>{owner}</b>
              </span>
              <Icon name="chevron" />
            </button>
          ))}
      </div>
    </main>
  )
}

function Breadcrumb({
  lead,
  navigate,
}: {
  lead?: boolean
  navigate?: (page: string) => void
}) {
  return (
    <nav className="breadcrumb" aria-label="Breadcrumb">
      <button onClick={() => navigate?.("accounts")}>Accounts</button>
      <Icon name="chevron" size={13} />
      <button onClick={() => navigate?.("account")}>Northwind Health</button>
      {lead && (
        <>
          <Icon name="chevron" size={13} />
          <span>Sarah Lindqvist</span>
        </>
      )}
    </nav>
  )
}

function AccountPage({
  openLead,
  navigate,
}: {
  openLead: () => void
  navigate: (page: string) => void
}) {
  return (
    <main className="canvas">
      <Breadcrumb navigate={navigate} />
      <header className="record-header">
        <div className="account-icon large">
          <Icon name="building" size={24} />
        </div>
        <div>
          <h1>Northwind Health</h1>
          <p>2 active leads · Last activity 10:30</p>
        </div>
      </header>
      <div className="section-heading">
        <div>
          <h2>Leads</h2>
          <p>Active leads at this account</p>
        </div>
      </div>
      <div className="record-list">
        {[
          [
            "Sarah Lindqvist",
            "SL",
            "VP Procurement",
            "Needs review",
            "Waiting on customer",
            81,
          ],
          ["Marcus Hale", "MH", "IT Director", "Agent-led", "Working", 64],
        ].map(([name, initials, title, mode, state, score]) => (
          <button
            className="record-row lead-row"
            key={String(name)}
            onClick={openLead}
          >
            <div className="identity">
              <span className="avatar">{initials}</span>
              <span>
                <strong>{name}</strong>
                <small>{title}</small>
              </span>
            </div>
            <Badge tone={mode === "Needs review" ? "warning" : "brand"}>
              {mode}
            </Badge>
            <span className="activity-state">
              <span className="status-dot" /> {state}
            </span>
            <span className="score">
              <small>Score</small>
              <b>{score}</b>
            </span>
            <Icon name="chevron" />
          </button>
        ))}
      </div>
    </main>
  )
}

function Readiness({ resumed }: { resumed: boolean }) {
  const rows = [
    ["Budget", "$240k", "Confirmed", "High"],
    ["Timeline", "Q3", "Confirmed", "High"],
    [
      "Economic buyer",
      resumed ? "Dan Whitfield (CFO)" : "Unconfirmed",
      resumed ? "Confirmed" : "Conflicting evidence",
      resumed ? "High" : "Medium",
    ],
    ["Decision process", "Unconfirmed", "Insufficient evidence", "—"],
  ]
  return (
    <section className="scorecard">
      <div className="scorecard-title">
        <div>
          <h2>Opportunity readiness</h2>
          <p>{resumed ? "3" : "2"} of 4 confirmed</p>
        </div>
        <div
          className="progress"
          aria-label={`${resumed ? "3" : "2"} of 4 confirmed`}
        >
          {[0, 1, 2, 3].map((step) => (
            <span
              className={step < (resumed ? 3 : 2) ? "complete" : ""}
              key={step}
            />
          ))}
        </div>
      </div>
      <div className="readiness-rows">
        {rows.map(([field, value, status, confidence]) => (
          <div className="readiness-row" key={field}>
            <span
              className={`state-icon ${
                status === "Confirmed" ? "confirmed" : "unconfirmed"
              }`}
            >
              <Icon
                name={status === "Confirmed" ? "check" : "alert"}
                size={15}
              />
            </span>
            <strong>{field}</strong>
            <span>{value}</span>
            <Badge tone={status === "Confirmed" ? "success" : "warning"}>
              {status}
            </Badge>
            <small>{confidence}</small>
          </div>
        ))}
      </div>
    </section>
  )
}

const milestoneSteps = [
  ["Observe", "Matched customer to account"],
  ["Understand", "Identified audit-compliance need"],
  ["Engage", "Asked about current workflow"],
  ["Understand", "Detected active evaluation intent"],
  ["Investigate", "Reviewed account history"],
  ["Investigate", "Found previous $240K opportunity"],
  ["Understand", "Identified approval stakeholders"],
  ["Evaluate", "Detected conflicting approval evidence"],
]

function ActivityStream({
  resumed,
  showEvidence,
  focusPanel,
}: {
  resumed: boolean
  showEvidence: () => void
  focusPanel: () => void
}) {
  const [expanded, setExpanded] = useState(false)
  return (
    <section className="activity">
      <div className="activity-header">
        <div>
          <h2>Agent activity</h2>
          <p>
            {resumed
              ? "Verifying decision process"
              : "Waiting for your guidance"}
          </p>
        </div>
        <Badge tone={resumed ? "success" : "neutral"}>
          {resumed ? "Working" : "Paused"}
        </Badge>
      </div>
      <div className="timeline">
        {resumed && (
          <>
            <article className="timeline-event resumed">
              <span className="timeline-icon">
                <Icon name="spark" size={15} />
              </span>
              <time>10:34</time>
              <div>
                <Badge tone="brand">Agent resumed</Badge>
                <h3>Updated stakeholder model</h3>
                <p>Economic buyer is Dan Whitfield (CFO), confidence High.</p>
                <small>3 activities · 2 min</small>
              </div>
            </article>
            <article className="timeline-event">
              <span className="timeline-icon">
                <Icon name="user" size={15} />
              </span>
              <time>10:32</time>
              <div>
                <Badge>Human input</Badge>
                <h3>Jordan clarified approval roles</h3>
                <p>Dan owns budget approval; Sarah owns procurement.</p>
              </div>
            </article>
          </>
        )}
        <article
          className={`timeline-event needs-input ${resumed ? "resolved" : ""}`}
        >
          <span className="timeline-icon">
            <Icon name="alert" size={15} />
          </span>
          <time>10:30</time>
          <div>
            <div className="event-topline">
              <Badge tone="warning">Needs your input</Badge>
              {resumed && <Badge tone="success">Resolved</Badge>}
            </div>
            <h3>Approval authority cannot be determined</h3>
            <p>
              Conflicting evidence prevented a confident economic-buyer
              decision.
            </p>
            <small>2 supporting activities</small>
            {!resumed && (
              <Button variant="quiet" onClick={focusPanel}>
                View details
              </Button>
            )}
          </div>
        </article>
        <article className="timeline-event">
          <span className="timeline-icon">
            <Icon name="user" size={15} />
          </span>
          <time>10:21</time>
          <div>
            <Badge>Customer response</Badge>
            <h3>Sarah replied about approval routing</h3>
            <Button variant="quiet" onClick={showEvidence}>
              View conversation
            </Button>
          </div>
        </article>
        <article className="timeline-event routine">
          <span className="timeline-icon">
            <Icon name="send" size={15} />
          </span>
          <time>10:06</time>
          <div>
            <h3>Asked Sarah who holds final approval</h3>
            <p>Waiting on customer</p>
          </div>
        </article>
        <article className="timeline-event milestone">
          <span className="timeline-icon">
            <Icon name="spark" size={15} />
          </span>
          <time>10:04</time>
          <div>
            <Badge tone="brand">Milestone</Badge>
            <h3>Qualification progressed</h3>
            <p>
              Business need, product fit, pain, and active intent confirmed.
            </p>
            <button
              className="expand-link"
              onClick={() => setExpanded(!expanded)}
            >
              8 activities · 14 min <span>{expanded ? "−" : "+"}</span>
            </button>
            {expanded && (
              <div className="stepper">
                {milestoneSteps.map(([family, description], index) => (
                  <div className="step" key={`${family}-${description}`}>
                    <span className="step-dot" />
                    <b>{family}</b>
                    <p>{description}</p>
                    {index > 0 && milestoneSteps[index - 1][0] === family && (
                      <span
                        className="loop"
                        aria-label="Repeated activity family"
                      >
                        ↻
                      </span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </article>
        <button className="older-events">
          Oct 1 · 6 events <Icon name="chevron" size={15} />
        </button>
      </div>
    </section>
  )
}

function LeadPage({
  navigate,
  resumed,
  setResumed,
  openModal,
  focusPanel,
}: {
  navigate: (page: string) => void
  resumed: boolean
  setResumed: (value: boolean) => void
  openModal: (modal: string) => void
  focusPanel: () => void
}) {
  const [autoOpen, setAutoOpen] = useState(false)
  return (
    <main className="canvas lead-canvas">
      <Breadcrumb lead navigate={navigate} />
      <header className="lead-header">
        <span className="avatar hero">SL</span>
        <div className="lead-title">
          <h1>Sarah Lindqvist</h1>
          <p>VP Procurement · Northwind Health</p>
        </div>
        <Badge tone={resumed ? "brand" : "warning"}>
          {resumed ? "Agent-led" : "Needs review"}
        </Badge>
        <div className="lead-facts">
          <span>
            <small>Score</small>
            <b>81</b>
          </span>
          <span>
            <small>Last activity</small>
            <b>{resumed ? "10:34" : "10:30"}</b>
          </span>
          <span>
            <small>Owner</small>
            <b>Jordan Bell</b>
          </span>
        </div>
        <button className="icon-button" aria-label="More actions">
          <Icon name="more" />
        </button>
      </header>
      {!resumed && (
        <div className="alert-banner">
          <Icon name="alert" />
          <strong>Needs your input — economic buyer unconfirmed</strong>
          <button onClick={focusPanel}>Respond in panel</button>
        </div>
      )}
      <section className="recommendation">
        <div className="recommendation-copy">
          <span className="eyebrow">Agent recommendation</span>
          <h2>Qualified — not yet opportunity-ready.</h2>
          <p>
            Strong need and intent are confirmed, but approval authority and
            decision process need clarification.
          </p>
        </div>
        <div className="recommendation-actions">
          <Button
            disabled={!resumed}
            title={
              resumed
                ? "Create opportunity"
                : "Economic buyer and decision process unconfirmed"
            }
            variant="primary"
          >
            Accept → create opportunity
          </Button>
          <Button onClick={() => setResumed(true)}>Nurture</Button>
          <Button onClick={() => openModal("reject")} variant="quiet">
            Reject
          </Button>
        </div>
      </section>
      <Readiness resumed={resumed} />
      <section className="auto-confirmed">
        <button onClick={() => setAutoOpen(!autoOpen)}>
          <span>
            <Icon name="check" size={16} />
            <strong>Automatically confirmed 4/4</strong>
          </span>
          <span>{autoOpen ? "−" : "+"}</span>
        </button>
        {autoOpen && (
          <div className="signal-grid">
            {[
              ["Business need", "Audit reporting", "High"],
              ["Product fit", "Confirmed", "High"],
              ["Pain", "Audit exposure", "High"],
              ["Active intent", "Confirmed", "Medium"],
            ].map(([label, value, confidence]) => (
              <div key={label}>
                <small>{label}</small>
                <strong>{value}</strong>
                <Badge tone="success">{confidence}</Badge>
              </div>
            ))}
          </div>
        )}
      </section>
      <ActivityStream
        focusPanel={focusPanel}
        resumed={resumed}
        showEvidence={() => openModal("evidence")}
      />
    </main>
  )
}

function AgentPanel({
  page,
  collapsed,
  setCollapsed,
  openHistory,
  resumed,
  setResumed,
}: {
  page: string
  collapsed: boolean
  setCollapsed: (value: boolean) => void
  openHistory: () => void
  resumed: boolean
  setResumed: (value: boolean) => void
}) {
  const [tagged, setTagged] = useState(true)
  const [draft, setDraft] = useState("")
  const [saveState, setSaveState] = useState("")
  const isLead = page === "lead"
  useEffect(() => {
    if (!draft) return setSaveState("")
    setSaveState("Saving…")
    const timer = window.setTimeout(() => {
      localStorage.setItem(isLead ? "draft-sarah" : "draft-general", draft)
      setSaveState("Draft saved")
    }, 1000)
    return () => window.clearTimeout(timer)
  }, [draft, isLead])
  useEffect(() => setTagged(true), [page])
  if (collapsed) {
    return (
      <button className="panel-launcher" onClick={() => setCollapsed(false)}>
        <span
          className={`presence-dot ${isLead && !resumed ? "waiting" : ""}`}
        />
        <span>Ask agent</span>
      </button>
    )
  }
  return (
    <aside className="agent-panel" id="agent-panel">
      <header className="panel-header">
        <div className="panel-title">
          <button
            aria-label="Collapse agent panel"
            className="collapse-button"
            onClick={() => setCollapsed(true)}
          >
            <Icon name="chevron" />
          </button>
          <div>
            <strong>
              {isLead
                ? "Accounts › Northwind Health › Sarah Lindqvist"
                : "General"}
            </strong>
            <span>
              <i
                className={`presence-dot ${
                  isLead && !resumed ? "waiting" : ""
                }`}
              />
              {isLead && !resumed ? "Waiting on you" : "Working autonomously"}
            </span>
          </div>
        </div>
        <button
          className="icon-button"
          aria-label="History"
          onClick={openHistory}
          title="History"
        >
          <Icon name="history" />
        </button>
      </header>
      <div className="panel-body">
        {isLead ? (
          <>
            <div className="switch-notice">
              <span>Switched to Sarah Lindqvist's conversation</span>
              <button aria-label="Dismiss">
                <Icon name="close" size={14} />
              </button>
            </div>
            {!resumed ? (
              <div className="request-card">
                <div className="agent-mark">
                  <Icon name="spark" />
                </div>
                <div>
                  <span className="eyebrow">I need your guidance</span>
                  <h2>Approval authority conflict</h2>
                  <p>
                    Sarah named herself as final approver, but the account
                    history points somewhere else.
                  </p>
                  <h3>What I found</h3>
                  <ul>
                    <li>
                      CRM lists Dan Whitfield (CFO) on a prior $240K
                      opportunity.
                    </li>
                    <li>Sarah named herself final approver.</li>
                    <li>Confidence is Medium.</li>
                  </ul>
                  <h3>Why I stopped</h3>
                  <p>
                    I can't determine the economic buyer without your account
                    context.
                  </p>
                  <h3>Who should I treat as the economic buyer?</h3>
                  <div className="stacked-actions">
                    <Button onClick={() => setResumed(true)} variant="primary">
                      Dan Whitfield (CFO)
                    </Button>
                    <Button onClick={() => setResumed(true)}>
                      Sarah Lindqvist
                    </Button>
                    <Button>Something else…</Button>
                  </div>
                </div>
              </div>
            ) : (
              <>
                <div className="chat-message rep">
                  <span className="avatar small">JB</span>
                  <div>
                    <strong>You</strong>
                    <p>Dan owns budget approval; Sarah owns procurement.</p>
                  </div>
                </div>
                <div className="chat-message">
                  <span className="agent-mark">
                    <Icon name="spark" />
                  </span>
                  <div>
                    <strong>Agent</strong>
                    <p>
                      Got it. I updated the stakeholder model and resumed
                      qualification. Dan Whitfield is now the economic buyer
                      with High confidence.
                    </p>
                  </div>
                </div>
                <div className="next-card">
                  <Badge tone="success">Nurtured</Badge>
                  <h3>Sarah moved to nurture.</h3>
                  <p>
                    Next up: Maya Chen, waiting 3d 4h and escalated. 3 more are
                    waiting. Open her lead?
                  </p>
                  <div>
                    <Button variant="primary">Open Maya Chen</Button>
                    <Button>Not now</Button>
                  </div>
                </div>
              </>
            )}
          </>
        ) : (
          <div className="welcome">
            <div className="agent-mark large">
              <Icon name="spark" size={24} />
            </div>
            <h2>Hi Jordan. I'm working your leads in the background.</h2>
            <p>
              I’ll bring you in when I need context, guidance, or authorization.
            </p>
            <div className="suggestions">
              <button>Which lead should I handle first?</button>
              <button>What changed since yesterday?</button>
              <button>Tell me how you like follow-ups written</button>
            </div>
          </div>
        )}
      </div>
      <footer className="composer">
        <div className="composer-box">
          {isLead && tagged && (
            <span className="lead-tag">
              lead: Sarah Lindqvist
              <button
                onClick={() => setTagged(false)}
                aria-label="Remove lead tag"
              >
                <Icon name="close" size={12} />
              </button>
            </span>
          )}
          {isLead && !tagged && (
            <button className="add-tag" onClick={() => setTagged(true)}>
              + Add tag: lead: Sarah Lindqvist
            </button>
          )}
          <textarea
            onChange={(event) => setDraft(event.target.value)}
            placeholder={isLead ? "Ask about this lead…" : "Ask Agent…"}
            value={draft}
          />
          <button className="send-button" aria-label="Send message">
            <Icon name="send" size={17} />
          </button>
        </div>
        <div className="composer-hint">
          <span>
            {isLead
              ? tagged
                ? "Asking about Sarah Lindqvist"
                : "General question · answers across your workspace"
              : "@ mention · / actions"}
          </span>
          <span>{saveState}</span>
        </div>
      </footer>
    </aside>
  )
}

function Modal({
  type,
  close,
  setResumed,
}: {
  type: string
  close: () => void
  setResumed: (value: boolean) => void
}) {
  const [tab, setTab] = useState("Conversation")
  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={close}>
      <section
        aria-modal="true"
        className={`modal ${type === "evidence" ? "large" : ""}`}
        onMouseDown={(event) => event.stopPropagation()}
        role="dialog"
      >
        {type === "reject" && (
          <>
            <header className="modal-header">
              <div>
                <h2>Reject lead?</h2>
                <p>Sarah Lindqvist · Northwind Health</p>
              </div>
              <button className="icon-button" onClick={close}>
                <Icon name="close" />
              </button>
            </header>
            <div className="modal-body">
              <p>
                If this customer re-engages, qualification restarts from
                scratch. This scorecard stays visible for context.
              </p>
            </div>
            <footer className="modal-footer">
              <Button onClick={close}>Cancel</Button>
              <Button
                onClick={() => {
                  setResumed(true)
                  close()
                }}
                variant="danger"
              >
                Reject lead
              </Button>
            </footer>
          </>
        )}
        {type === "history" && (
          <>
            <header className="modal-header">
              <div>
                <h2>History</h2>
                <p>Sarah Lindqvist</p>
              </div>
              <button className="icon-button" onClick={close}>
                <Icon name="close" />
              </button>
            </header>
            <div className="modal-body">
              <div className="history-tools">
                <div className="chip-group">
                  <button className="selected">This conversation</button>
                  <button>All conversations</button>
                </div>
                <label className="search-box">
                  <Icon name="search" />
                  <input placeholder="Search history" />
                </label>
              </div>
              <div className="history-list">
                {[
                  ["Prior opportunity check", "Aug 29", "9 messages"],
                  ["Approval authority clarification", "Aug 14", "6 messages"],
                ].map(([title, date, count]) => (
                  <button key={title}>
                    <span>
                      <strong>{title}</strong>
                      <small>
                        {date} · {count}
                      </small>
                    </span>
                    <Icon name="chevron" />
                  </button>
                ))}
              </div>
            </div>
            <footer className="modal-note">
              The window shows the last 30 days. Open requests and active
              instructions stay in view until resolved.
            </footer>
          </>
        )}
        {type === "evidence" && (
          <>
            <header className="modal-header">
              <div>
                <span className="eyebrow">Supporting evidence</span>
                <h2>Approval authority</h2>
              </div>
              <button className="icon-button" onClick={close}>
                <Icon name="close" />
              </button>
            </header>
            <div className="tabs">
              {["Conversation", "CRM record"].map((item) => (
                <button
                  className={tab === item ? "active" : ""}
                  key={item}
                  onClick={() => setTab(item)}
                >
                  {item}
                </button>
              ))}
            </div>
            <div className="modal-body evidence-body">
              {tab === "Conversation" ? (
                <div className="evidence-thread">
                  <div className="evidence-message agent-evidence">
                    <strong>Agent</strong>
                    <p>Who holds final approval for this purchase?</p>
                    <small>10:06</small>
                  </div>
                  <div className="evidence-message highlighted">
                    <strong>Sarah Lindqvist · Customer</strong>
                    <p>
                      Approvals route through procurement and my CFO, but I’m
                      the final approver for the evaluation.
                    </p>
                    <small>10:21 · Referenced message</small>
                  </div>
                  <Button variant="quiet">Open full conversation</Button>
                </div>
              ) : (
                <div className="crm-evidence">
                  <Badge>CRM</Badge>
                  <h3>Prior opportunity · $240K</h3>
                  <p>Approver: Dan Whitfield (CFO)</p>
                  <hr />
                  <Badge tone="brand">Customer-stated</Badge>
                  <h3>Final approver: Sarah Lindqvist</h3>
                  <p>Captured from the customer response at 10:21.</p>
                </div>
              )}
            </div>
          </>
        )}
      </section>
    </div>
  )
}

export default function App() {
  const [page, setPage] = useState("queue")
  const [collapsed, setCollapsed] = useState(
    () => localStorage.getItem("agent-panel-collapsed") === "true",
  )
  const [modal, setModal] = useState("")
  const [resumed, setResumed] = useState(false)
  const [split, setSplit] = useState(50)
  const shellRef = useRef<HTMLDivElement>(null)
  const navigate = (next: string) => setPage(next)
  const setPanelCollapsed = (value: boolean) => {
    localStorage.setItem("agent-panel-collapsed", String(value))
    setCollapsed(value)
  }
  const focusPanel = () => {
    setPanelCollapsed(false)
    window.setTimeout(
      () =>
        document
          .querySelector<HTMLTextAreaElement>(".composer textarea")
          ?.focus(),
      100,
    )
  }
  const startResize = (event: React.PointerEvent<HTMLDivElement>) => {
    const workspace = event.currentTarget.parentElement
    if (!workspace) return
    event.currentTarget.setPointerCapture(event.pointerId)
    const resize = (moveEvent: PointerEvent) => {
      const bounds = workspace.getBoundingClientRect()
      const nextSplit = ((moveEvent.clientX - bounds.left) / bounds.width) * 100
      const minimum = (560 / bounds.width) * 100
      setSplit(Math.min(100 - minimum, Math.max(minimum, nextSplit)))
    }
    const stop = () => {
      window.removeEventListener("pointermove", resize)
      window.removeEventListener("pointerup", stop)
    }
    window.addEventListener("pointermove", resize)
    window.addEventListener("pointerup", stop)
  }
  return (
    <div
      className={`app-shell ${collapsed ? "panel-collapsed" : ""}`}
      ref={shellRef}
    >
      <Rail navigate={navigate} page={page} />
      <div
        className="workspace"
        style={{ "--split": `${split}%` } as CSSProperties}
      >
        {page === "queue" && <QueuePage openLead={() => navigate("lead")} />}
        {page === "accounts" && (
          <AccountsPage openAccount={() => navigate("account")} />
        )}
        {page === "account" && (
          <AccountPage navigate={navigate} openLead={() => navigate("lead")} />
        )}
        {page === "lead" && (
          <LeadPage
            focusPanel={focusPanel}
            navigate={navigate}
            openModal={setModal}
            resumed={resumed}
            setResumed={setResumed}
          />
        )}
        {!collapsed && (
          <div
            aria-label="Resize canvas and conversation panel"
            className="divider"
            onPointerDown={startResize}
            role="separator"
          />
        )}
        <AgentPanel
          collapsed={collapsed}
          openHistory={() => setModal("history")}
          page={page}
          resumed={resumed}
          setCollapsed={setPanelCollapsed}
          setResumed={setResumed}
        />
      </div>
      {modal && (
        <Modal
          close={() => setModal("")}
          setResumed={setResumed}
          type={modal}
        />
      )}
    </div>
  )
}
