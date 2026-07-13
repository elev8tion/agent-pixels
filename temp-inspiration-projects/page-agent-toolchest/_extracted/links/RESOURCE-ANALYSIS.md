# Link & Resource Analysis — alibaba/page-agent

## 1. LLM Providers (first-party supported)

| Provider | Base URL | Env / Config |
|----------|----------|--------------|
| OpenAI | `https://api.openai.com/v1` | `LLM_API_KEY` |
| DeepSeek | `https://api.deepseek.com` | `LLM_API_KEY` |
| Alibaba DashScope (qwen) | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `LLM_API_KEY` |
| OpenRouter | `https://openrouter.ai` | `LLM_API_KEY` |
| Ollama (local) | `http://localhost:11434/v1` | key = `'NA'` |
| Claude proxy example | `https://your-claude-proxy.example` | — |
| Local LM Studio / generic | `http://127.0.0.1:1234/v1`, `http://test.local/v1` | — |

## 2. Page Agent Demo / Testing Backend

- **`/api/llm-proxy`** — internal LLM proxy route (demo build)
- **`https://page-ag-testing-ohftxirgbn.cn-shanghai.fcapp.run`** — Alibaba Cloud Function Compute; the free testing LLM backing the demo IIFE script (`page-agent.demo.js`). Governed by `docs/terms-and-privacy.md`.
- **`https://hwcxiuzfylggtcktqgij.supabase.co`** — Supabase (website GitHub-stars integration)

## 3. CDN Mirrors (demo IIFE distribution)

| Mirror | URL |
|--------|-----|
| Global (jsDelivr) | `https://cdn.jsdelivr.net/npm/page-agent@1.11.0/dist/iife/page-agent.demo.js` |
| China (npmmirror) | `https://registry.npmmirror.com/page-agent/1.11.0/files/dist/iife/page-agent.demo.js` |

## 4. Distribution / Project URLs

- GitHub: `https://github.com/alibaba/page-agent`
- Docs site: `https://alibaba.github.io/page-agent/`
- Assets CDN: `https://page-agent.github.io/assets/readme/*.png`
- npm: `https://www.npmjs.com/package/page-agent` · bundlephobia badge
- Chrome Web Store: `https://chromewebstore.google.com/detail/page-agent-ext/akldabonmimlicnjlflnapfeklbfemhj`
- Social: `https://x.com/simonluvramen`

## 5. MCP / Extension Protocol

- **MCP server** (`@page-agent/mcp`): stdio transport, default HTTP+WS hub on `http://localhost:38401` (env `PORT`).
- **Hub ↔ Extension bridge**: WebSocket (`ws://localhost:*`) — MCP server talks to the Chrome extension's hub entrypoint over WS, extension then drives PageAgent in the active tab.
- Launcher HTML opened in default browser on MCP start.

## 6. Environment Variables

### Demo / Dev (Vite `import.meta.env`)
- `import.meta.env.LLM_BASE_URL`
- `import.meta.env.LLM_MODEL_NAME`
- `import.meta.env.LLM_API_KEY`
- `import.meta.env.VERSION`
- `import.meta.env.DEV`
- `LLM_CLOUD` (cloud-provider hint)

### CI Live-Model Test Fixtures
- `process.env.TESTING_ALIYUN_KEY`
- `process.env.TESTING_DEEPSEEK_KEY`
- `process.env.TESTING_OPENROUTER_KEY`
- `process.env.KEY` (generic test secret)

## 7. Static Assets

| Asset | Location |
|-------|----------|
| Logo 64px PNG | `extension/src/assets/page-agent-64.png`, `extension/public/assets/page-agent-64.png` |
| Logo 256px WebP | `extension/public/assets/page-agent-256.webp` |
| Cursor fill SVG | `page-controller/src/mask/cursor-fill.svg` |
| Cursor border SVG | `page-controller/src/mask/cursor-border.svg` |

## 8. Key Third-Party npm Dependencies (external)

| Package | Used by | Purpose |
|---------|---------|---------|
| `zod` (v4) | core, llms, mcp, page-agent, extension | Schema validation + LLM tool schemas |
| `chalk` | core, page-agent, extension | Console coloring |
| `ai-motion` | page-controller, extension | Cursor motion simulation (human-like) |
| `@modelcontextprotocol/sdk` | mcp | MCP server protocol |
| `ws` | mcp | WebSocket hub bridge |
| `wxt` | extension | Browser-extension framework |
| `react` / `react-dom` (v19) | extension, website | UI |
| `@radix-ui/*` | extension, website | Headless UI primitives |
| `motion` | extension, website | Animations |
| `tailwindcss` (v4) | extension, website | Styling |
| `idb` | extension | IndexedDB (history persistence) |
| `rough-notation` | extension, website | Hand-drawn annotations |
| `sonner` | extension, website | Toast notifications |
| `vite` (v8) | root | Build tooling |
| `vitest` (v4) | root | Unit tests |
