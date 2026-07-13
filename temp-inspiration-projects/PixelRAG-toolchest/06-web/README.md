# 06-web — pixelrag.ai frontend + chat agent backend

The **Next.js 16** frontend at [pixelrag.ai](https://pixelrag.ai) (deployed on Vercel) plus a
standalone **Claude Agent SDK** chat-backend service. React 19, Tailwind v4, shadcn/ui,
framer-motion.

## Architecture

```
app/
├── layout.tsx, page.tsx          ← landing page
├── chat/{layout,page}.tsx        ← conversational agent UI (RAG chat)
├── docs/{layout,page}.tsx        ← API reference docs page
├── api/chat/route.ts             ← Next.js route: Claude Agent SDK agent loop (serverless)
├── icon.png, apple-icon.png, favicon.ico
components/
├── SearchBar.tsx, SearchControls.tsx, ResultGroup.tsx, TileCard.tsx, ComparePanel.tsx
├── ApiPlayground.tsx, AboutSection.tsx, NavLinks.tsx, StatusCard.tsx
├── ModeToggle.tsx, Lightbox.tsx, theme-provider.tsx
└── ui/                           ← shadcn/ui primitives (button, dialog, slider, badge, input, collapsible)
lib/
├── api.ts        ← typed client for the search API (PIXELRAG_SEARCH_URL)
├── types.ts      ← shared TypeScript types
├── history.ts    ← chat history persistence
└── utils.ts      ← cn() class merge
agent-server.mjs   ← ★ standalone SSE server: Claude Agent SDK w/ subscription auth
next.config.ts, tsconfig.json, eslint.config.mjs, postcss.config.mjs, components.json
```

## Two ways the agent runs

1. **`app/api/chat/route.ts`** — the Next.js serverless route. Runs the Claude Agent SDK
   inline (works where Anthropic API creds exist).
2. **`agent-server.mjs`** — a standalone Node SSE server for production. It uses the
   **logged-in `claude` CLI's subscription auth** (no `ANTHROPIC_API_KEY` needed) and exposes
   the same agent loop + pixelrag tools, so the Vercel frontend can proxy to it (the native
   CLI binary/creds don't exist in serverless). Includes **rate limiting** (per-IP, global
   daily, max concurrent) and a **per-conversation USD budget cap**.

Both expose the search API as an agent tool via `createSdkMcpServer` + `zod` schemas, so the
agent can call `/search` on the PixelRAG index as it reasons.

## Key env vars

```
NEXT_PUBLIC_API_URL        frontend → search API base (browser)
PIXELRAG_SEARCH_URL        server-side search API base (agent-server, route.ts)
AGENT_PORT                 agent-server listen port (default 30010)
CHAT_MAX_BUDGET_USD        per-conversation cost cap
CHAT_THINKING_TOKENS       extended-thinking token budget
RL_PER_IP / RL_WINDOW_MS / RL_GLOBAL_DAILY / RL_MAX_CONCURRENT   rate limiting
ALLOWED_ORIGIN             CORS origin
AGENT_BACKEND_URL          optional agent backend override
PIXELRAG_SEARCH_PROXY      optional search API proxy
```

## Internal dependencies

- **Calls `04-serve`'s `/search` endpoint** (the hosted `api.pixelrag.ai` in prod).
- **Depends on Anthropic** (`@anthropic-ai/claude-agent-sdk`, `@anthropic-ai/claude-code`) for
  the chat agent + reader model.

## Repurpose

`agent-server.mjs` is an excellent reference for: running the Claude Agent SDK on a long-lived
server with **subscription (not API-key) auth**, exposing custom tools as an MCP server,
budget-capped conversations, and multi-axis rate limiting on a public endpoint. The Next.js
`/api/chat` + standalone-server duality (same agent loop, two deployment shapes) is a clean
pattern for "agent that must run where its credentials live."

## Refinement Report

Ran the native cleansed pipeline (scan → clean → validate → analyze → package). Cleaned source, manifest, and full analysis live in `refined/`.

- **Items extracted:** 95  (javascript: 13, typescript: 82)
- **Source files scanned:** 48
- **Syntax validation:** 95 valid / 0 invalid
- **Imports cleaned:** 1345 lines of cleaned output from 4375 raw lines (0 cleansed annotations; 0 relative-import TODOs flagged for manual resolution)
- **Health score:** 54/100 — Moderate — React/Next.js components; high dead-code count reflects UI components only referenced in JSX (not caught by the JS regex scanner's call graph). Treat as candidates, not confirmed dead.
  - Long functions: 15 · Duplications: 20 · High-coupling items: 5 · Cross-module deps: 3
- **Dead code:** 93 flagged (93 high-confidence) — ⚠️ totals are inclusive (count reverse-edge = 0 in the extracted symbol graph); many are public APIs, CLI entrypoints, `__main__` guards, or JSX-only UI refs. **Review only the high-confidence subset** before removing anything.
- **Package manifest:** generated (`package.json`)

See `refined/README.md` for the full item table and `refined/manifest.json` for the machine-readable extraction manifest.
