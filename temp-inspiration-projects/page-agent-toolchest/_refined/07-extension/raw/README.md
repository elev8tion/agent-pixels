# 07-extension — Chrome Extension (`@page-agent/ext`)

A WXT + React browser extension that extends Page Agent across **multiple tabs**.
Adds a side-panel UI, a multi-page agent, tab orchestration, an MCP hub, and
IndexedDB-backed run history.

## What's Here

```
src/
├── entrypoints/
│   ├── background.ts                 # Service worker: tab lifecycle, message routing, auth tokens
│   ├── content.ts                    # Content script: injects RemotePageController, exposes agent to page on auth
│   ├── main-world.ts                 # Main-world script (runs in page context)
│   ├── sidepanel/{App.tsx,index.html,main.tsx}   # ⭐ The side-panel React UI
│   └── hub/{App.tsx,hub-ws.ts,index.html,main.tsx}  # MCP hub page (WebSocket bridge to 06-mcp)
├── agent/
│   ├── MultiPageAgent.ts             ← ⭐ PageAgentCore subclass for cross-tab automation
│   ├── TabsController.ts             # chrome.tabs orchestration (453 LOC) — open/switch/close/list tabs
│   ├── TabsController.background.ts  # SW-side tab operations
│   ├── RemotePageController.ts       # PageController proxy → forwards to content script per tab
│   ├── RemotePageController.content.ts  # Content-side impl receiving remote calls
│   ├── RemotePageController.background.ts
│   ├── tabTools.ts                   # Tab tools exposed to the agent (switch_tab, open_tab, close_tab…)
│   ├── useAgent.ts                   # React hook binding agent events → UI state
│   ├── constants.ts
│   └── system_prompt.md              # Extension-specific system prompt (adds tab concepts)
├── components/
│   ├── ConfigPanel.tsx               # LLM config form
│   ├── HistoryList.tsx, HistoryDetail.tsx, cards.tsx, misc.tsx, ErrorBoundary.tsx
│   └── ui/                           # Radix-based primitives (button, card, field, input, switch…)
├── lib/
│   ├── db.ts                         # IndexedDB history persistence (via `idb`)
│   ├── history-export.ts             # Export run history
│   └── utils.ts                      # cn() Tailwind-merge helper
└── types/, assets/

public/                  # Static assets (logos)
docs/                    # extension_api.md — API integration docs
wxt.config.js            # ⭐ WXT manifest + build config (Manifest V3)
components.json          # shadcn-style config
```

## Architecture — How Multi-Tab Works

```
Side Panel (React UI)
    │
    ▼
MultiPageAgent (extends PageAgentCore)
    │ uses
    ▼
TabsController ──chrome.tabs──▶ active tab
    │                              │
    ▼                              ▼
RemotePageController ──msg──▶ content script's local PageController ──▶ DOM
```

`RemotePageController` is a **drop-in for `PageController`** (02) that proxies
every async call over the extension message bridge to the content script, which
runs the real `PageController` in the page. This is why PageController's API is
100% async — it was designed for exactly this remoting.

## Entrypoints (Manifest V3)

| Entrypoint | Role |
|-----------|------|
| `background.ts` | Service worker — tab mgmt, message routing, auth-token gating |
| `content.ts` | Runs in every page; injects RemotePageController impl; optionally exposes agent to page world (auth-token matched) |
| `sidepanel` | The React UI (`useAgent` hook + ConfigPanel + History) |
| `hub` | The page the MCP server (06) opens; WebSocket-bridges MCP → extension |

## Dependencies

- Internal: `@page-agent/{core,llms,page-controller,ui}`
- Framework: `wxt`, `react`/`react-dom` v19, `@radix-ui/*`, `tailwindcss` v4, `motion`
- Data: `idb` (IndexedDB), `chalk`
- Peer: `zod`

## Repurpose Notes

- The `RemotePageController` ↔ `TabsController` pattern is a reusable recipe for
  "control N tabs from one extension agent."
- `useAgent.ts` is the clean React binding for agent events — copy it for any
  agent-in-React UI.
- Build: `npm run build:ext` → `wxt zip` → `page-agent-ext-{{version}}-{{browser}}.zip`.
