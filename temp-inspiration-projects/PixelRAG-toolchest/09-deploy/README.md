# 09-deploy — CD, blue-green search API, CI, chromium build

How PixelRAG runs in production. Host-specific secrets/state are intentionally **not** here
(they live in an out-of-repo file the root `CLAUDE.md` imports on the deploy host).

## Topology

```
Vercel ── web/ (Next.js frontend)
           │
           ├──▶ agent-server (port 30010, Claude Agent SDK) ──┐
           │                                                    ▼
nginx upstream (blue-green) ──▶ pixelrag serve (port 30001, FAISS search API)
```

## Files

```
deploy.sh                        ← CD restart logic (invoked by the Deploy workflow)
api-switch.sh                    ← ★ blue-green cutover + rollback (health/smoke-check + nginx reload)
pixelrag-api.service             ← systemd unit: blue search-API slot
pixelrag-api-green.service       ← systemd unit: green search-API slot
pixelrag-agent.service           ← systemd unit: chat agent
pixelrag-api-upstream.conf       ← nginx upstream the switch script rewrites
README.md                        ← full deploy topology doc
workflows/                       ← .github/workflows (copied from .github/)
├── ci.yml                       ← CI (GitHub-hosted runners)
├── deploy.yml                   ← CD (self-hosted runner, push-to-main only, never on PR)
├── release.yml                  ← release publishing
└── chrome-build.yml             ← patched Chromium build
chromium/                        ← patched-headless-shell build assets
├── README.md
└── screenshot-patches.diff      ← Chromium source patches for screenshot optimizations
```

## Key design points

### Blue-green search API (the gem)
Two slots — **blue** and **green** — each an independent `pixelrag serve` on its own port,
fronted by an nginx `upstream`. Zero-downtime rollout:
1. Bring up the idle slot with the new config.
2. `api-switch.sh <port>` — health- & smoke-checks the target, flips the nginx upstream with a
   **graceful reload** (no dropped connections), repoints + restarts the agent.
3. **Rollback = `api-switch.sh <other-port>`.**

Preferred over restarting a slot in place (reloading the large FAISS index = minutes of downtime).

### Egress-only self-hosted runner
The CD runner dials **out** to GitHub (no inbound, no SSH keys/hostnames in repo). `deploy.yml`
triggers **only on push to `main`** (post-merge = trusted) + manual dispatch — **never
`pull_request`** — so fork PRs can't run on it. All CI stays on GitHub-hosted runners.

### `deploy.sh` restart granularity
Fast-forwards the checkout and restarts **only what changed**: `uv.lock` → `uv sync`;
`web/agent-server.mjs` → restart agent (cheap); `serve/**` → flagged only (use blue-green).

Refuses to run unless the checkout is on a clean `main` (the box doubles as a dev machine).

## Internal dependencies

Depends on all runtime modules — it's the glue that runs `04-serve`, `06-web`'s agent-server,
and uses `01-render`'s chromium patches.

## Repurpose

`api-switch.sh` is a reusable **nginx blue-green cutover with health-check + graceful reload +
automatic rollback** script — adaptable to any service behind an nginx upstream where reloads
are expensive. The egress-only-self-hosted-runner + push-to-main-only CD pattern is a strong
security template for open-source projects that deploy from a private box.

## Refinement Report

**Status:** non-code module — 0 AST-extractable items — config/ops/docs module (shell/YAML/JSON/systemd/nginx/markdown)

- Files scanned: 13 (none matched a supported language)
- Imports cleaned: 0
- Metadata stripped: 0
- Syntax validation: N/A (no AST-extractable code)
- Health score: N/A · Dead code: 0
- Package manifest: N/A

See `refined/REFINE_NOTES.md` for the full rationale. The module's value is its documentation/config — preserved verbatim from `_source/`.
