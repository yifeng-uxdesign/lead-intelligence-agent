# Rep Workspace (human-rep-facing UI)

The lead operational workspace for sales reps: queue ("Needs your attention"), accounts,
lead detail, agent activity stream, and the conversation panel.

- Origin: Figma Make export (`Build History Modal`), imported as the baseline for redesign.
- Design spec: the "Lead Workspace — SLDS Design Prompt Pack (v2)" (not yet checked into the repo).
- Counterpart: the customer-facing conversation widget in `../northstar`.

## Run

```bash
cd rep-workspace
pnpm install
pnpm dev
```

Stack: React 19 + Vite 8 + Tailwind v4. Everything lives in `src/App.tsx` and `src/index.css` for now.
