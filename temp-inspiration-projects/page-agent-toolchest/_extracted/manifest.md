# Cluster Manifest — alibaba/page-agent

**Target:** https://github.com/alibaba/page-agent (v1.11.0)
**Type:** TypeScript monorepo (npm workspaces)
**Extracted:** clean shallow git clone → `_source/page-agent/`
**Format profile:** Pure source project — no compiled binaries, no build artifacts, no source maps to decompile.

## Extraction Summary

| Phase | Action | Result |
|-------|--------|--------|
| 0.5 — Magic byte scan | `file -b` on every file | ✅ All text. Only assets: 3 images (PNG/WebP) + 2 SVG cursors |
| 0.5 — Decompile | N/A (source, not bundle) | No `.js.map`, no Mach-O/ELF/PE, no APK/IPA |
| 0.5 — Decode | base64/hex/strings scan | 6 long base64 strings (all in test fixtures / encoded test keys), 0 hex blobs |
| 0.5 — Archive extraction | N/A | No nested archives in source tree |
| 0.75 — URLs | grep across source | **50 unique URLs** → `links/all-urls.txt` |
| 0.75 — Domains | URL host extraction | **24 domains** → `links/domains.txt` |
| 0.75 — API endpoints | pattern scan | `/v1/chat/completions`, `/api/llm-proxy`, `ws://localhost:*` |
| 0.75 — Env vars | `process.env.*` / `import.meta.env.*` | 13 references → `links/env-vars.txt` |
| 0.75 — npm packages | scoped import + package.json | 18 scoped refs + deps → `resources/npm-scoped.txt` |
| 2.5 — Cluster recurse | depth check | Max depth 1 reached (no nested encoded blobs) |

## What Was NOT Needed (and why)

- **No binary decompilation** — this is published open-source TypeScript, shipped as source.
- **No source-map extraction** — no `dist/` or `.output/` present in the clone; the repo is the source itself.
- **No archive extraction** — no zip/tar/7z bundles inside the tree.

## Discovered Architecture (depth 1)

8 npm workspaces in topological order. See `../README.md` for the full module index.

```
alibaba/page-agent (monorepo root, v1.11.0)
├── packages/llms/            @page-agent/llms      (781 LOC)  LLM client + OpenAI compat
├── packages/page-controller/ @page-agent/page-controller (3909 LOC) DOM ops + mask
├── packages/core/            @page-agent/core      (1507 LOC) PageAgentCore + tools
├── packages/ui/              @page-agent/ui        (1022 LOC) Panel + i18n
├── packages/page-agent/      page-agent            (84 LOC)   Main entry = Core+Ctrl+UI
├── packages/mcp/             @page-agent/mcp       (239 LOC)  MCP server + hub bridge
├── packages/extension/       @page-agent/ext       (4946 LOC) Chrome extension (WXT+React)
└── packages/website/         @page-agent/website   (8650 LOC) Docs + landing (React)
```

## Notable Discoveries

- **Source-first monorepo**: `package.json` `exports` point at `src/*.ts` in dev, swapped to `dist/*` only at publish time (`scripts/pre-publish.js` / `post-publish.js`).
- **Reflection-before-action model**: every LLM call is forced through a single `MacroTool` (`AgentOutput`) that bundles `evaluation_previous_goal` + `memory` + `next_goal` + `action`. Adapted from `browser-use`.
- **Third-party LLM providers** supported out of the box: OpenAI, DeepSeek, Alibaba DashScope (qwen), OpenRouter, Ollama (local).
- **Demo testing API**: `page-ag-testing-ohftxirgbn.cn-shanghai.fcapp.run` (Alibaba Cloud Function Compute) — free testing LLM used by the demo IIFE build.
- **Analytics**: `hwcxiuzfylggtcktqgij.supabase.co` (Supabase) — used by website for star count / GitHub integration.
- **Mask test keys**: `process.env.TESTING_ALIYUN_KEY`, `TESTING_DEEPSEEK_KEY`, `TESTING_OPENROUTER_KEY` — CI live-model test fixtures (see `packages/llms/src/live-models.test.ts`).
