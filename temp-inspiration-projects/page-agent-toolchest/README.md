# Page Agent — Toolchest

> Brute-force extraction of **[alibaba/page-agent](https://github.com/alibaba/page-agent)** (v1.11.0)
> into numbered, repurposable modules.

**Page Agent** is "the GUI Agent living in your webpage" — one script gives any
web page its own AI agent. Text-based DOM manipulation (no screenshots), bring-
your-own-LLM, optional Chrome extension for multi-page tasks, and an MCP server
for external control.

---

## Module Index (dependency order)

| # | Module | npm name | LOC | Role |
|---|--------|----------|-----|------|
| 00 | [shared](./00-shared/) | — (tooling) | 457 | Build scripts + root configs + **4 interface contracts** |
| 01 | [llms](./01-llms/) | `@page-agent/llms` | 781 | OpenAI-compatible LLM client + retry layer |
| 02 | [page-controller](./02-page-controller/) | `@page-agent/page-controller` | 3,909 | DOM ops, browser-use-derived extraction engine, mask |
| 03 | [core](./03-core/) | `@page-agent/core` | 1,507 | **PageAgentCore** — the observe→think→act loop |
| 04 | [ui](./04-ui/) | `@page-agent/ui` | 1,022 | Vanilla-TS chat Panel + i18n (decoupled) |
| 05 | [page-agent](./05-page-agent/) | `page-agent` | 84 | Public entry = Core + Controller + Panel |
| 06 | [mcp](./06-mcp/) | `@page-agent/mcp` | 239 | MCP server → drives browser via extension |
| 07 | [extension](./07-extension/) | `@page-agent/ext` | 4,946 | Chrome extension (WXT+React) — multi-tab agent |
| 08 | [website](./08-website/) | `@page-agent/website` | 8,650 | Docs + landing + playground (private) |

**Total: ~21,000 LOC across 9 modules.**

---

## Dependency Graph

```
                    ┌───────────────────────────┐
                    │        00-shared          │  (build tooling + contracts)
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │          01-llms          │  Tool / Message / LLM client
                    └─────────────┬─────────────┘
                                  │
              ┌───────────────────┴───────────────────┐
              │                                       │
   ┌──────────▼──────────┐                 ┌──────────▼──────────┐
   │   02-page-controller │                 │      03-core        │
   │   (DOM ops + mask)   │◄─────────────── │  (PageAgentCore)    │
   └──────────┬──────────┘    uses both     └──────────┬──────────┘
              │                                         │
              │              ┌──────────────────────────▼┐
              │              │          04-ui            │  (Panel + i18n)
              │              └──────────────┬────────────┘
              │                             │
              └──────────────┬──────────────┘
                             │
                ┌────────────▼────────────┐
                │      05-page-agent       │  = Core + Controller + Panel
                └────────────┬────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
 ┌──────▼──────┐    ┌────────▼────────┐    ┌──────▼──────┐
 │   06-mcp    │    │  07-extension   │    │ 08-website  │
 │ (MCP server)│    │ (Chrome ext,    │    │ (docs,      │
 │  → ext hub  │    │  multi-tab)     │    │  no deps)   │
 └─────────────┘    └────────┬────────┘    └─────────────┘
                             │ WS
                      drives via hub
```

Read horizontally: each module only depends on modules above/around it. No cycles.
The 4 decoupling contracts live in [`00-shared/contracts.md`](./00-shared/contracts.md).

---

## How To Use This Toolchest

### Pick a module and drop it into a new project

Each numbered folder is self-contained with its own `package.json`, source, and
README. The dependencies between modules are clean npm imports
(`@page-agent/llms`, etc.) — recreate those package names or rewrite the imports.

### Common extraction targets

- **"I want a headless AI web agent"** → `01-llms` + `02-page-controller` +
  `03-core` (skip the UI).
- **"I want an LLM client with retry"** → `01-llms` alone.
- **"I want a text-based DOM extractor"** → `02-page-controller/src/dom/`
  (the `dom_tree/index.js` engine is a direct browser-use port).
- **"I want a chat panel for any agent"** → `04-ui` (it's agent-agnostic).
- **"I want to drive a Chrome extension from MCP"** → `06-mcp` +
  `07-extension/src/entrypoints/hub/` + `agent/RemotePageController*`.
- **"I want animated marketing components"** → `08-website/src/components/ui/`.

### Source-first monorepo pattern

`00-shared/scripts/{pre-publish,post-publish}.js` implements the clever
"exports point at `src/*.ts` in dev, swap to `dist/*.js` at publish" trick —
reusable for any TS library monorepo.

---

## Source & Provenance

- **Original:** https://github.com/alibaba/page-agent (commit at clone time, v1.11.0)
- **License:** MIT (Alibaba Group + SimonLuvRamen)
- **Built on:** [`browser-use`](https://github.com/browser-use/browser-use) — DOM
  processing + prompts derived from it (the `dom_tree/index.js` engine and
  `system_prompt.md` carry explicit `@edit`/port markers).
- **Raw clone:** [`_source/page-agent/`](./_source/page-agent/) (shallow git clone)
- **Scan artifacts:** [`_extracted/`](./_extracted/) — manifest, URLs, domains,
  env vars, API endpoints, npm packages.

## Extraction Notes

- This was a **pure source extraction** — no binaries, no build artifacts, no
  source maps to decompile. The 8 npm workspaces already formed clean module
  boundaries (documented in the repo's `AGENTS.md`), so the toolchest maps 1:1
  onto them.
- Test files (`*.test.ts`) were preserved in their modules so contracts stay
  documented by examples.
- See `_extracted/manifest.md` for the full phase-by-phase extraction log and
  `_extracted/links/RESOURCE-ANALYSIS.md` for every URL/provider/env var found.
