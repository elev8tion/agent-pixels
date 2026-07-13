# PixelRAG — Cluster Manifest

**Target:** `https://github.com/StarTrail-org/PixelRAG` (GitHub repo)
**Extraction mode:** Source clone (GitHub repo → treat as project folder)
**Extraction date:** 2026-07-08
**Toolchest:** `~/PixelRAG-toolchest/`

## What PixelRAG is

PixelRAG is a **visual Retrieval-Augmented Generation** system from Berkeley SkyLab / BAIR /
NLP. Instead of parsing documents to text (which throws away tables, charts, layout), it
**renders documents (web pages, PDFs, images) as screenshot tiles** and retrieves over the
images directly with a LoRA-fine-tuned `Qwen3-VL-Embedding-2B` model. A pre-built index of
**8.28M Wikipedia pages** ships on Hugging Face and is served live at `api.pixelrag.ai`.

Paper: *PIXELRAG: Web Screenshots Beat Text for Retrieval-Augmented Generation*.

## Extraction summary

| Target type        | Strategy                                          | Result                       |
| ------------------ | ------------------------------------------------- | ---------------------------- |
| Source (Python/TS) | Clone → copy source into numbered modules         | ✅ direct copy               |
| Compiled binaries  | Magic-byte scan (`file -b` all files)             | ❌ none present              |
| Archives           | ZIP/GZip/TAR/RAR/7z/APK scan                      | ❌ none present              |
| Source maps (JS)   | `.js.map` lookup + `sourcesContent` extraction    | ❌ none (Next.js not bundled) |
| Encoded blobs      | base64/hex/URL-encoded scan, `strings` on bins    | ❌ none (incidental only)    |
| Nesting depth      | recurse to depth 3                                | depth 0 — nothing nested     |

**Verdict:** Pure application source. No decompilation, decoding, or archive extraction
required. Extraction is a faithful copy organized into dependency-ordered modules.

## Cluster registry

| #   | Module         | Package / Surface                         | Role                                                | Internal deps               |
| --- | -------------- | ----------------------------------------- | --------------------------------------------------- | --------------------------- |
| 00  | `00-shared`    | `pixelrag` (umbrella CLI)                 | The `pixelrag <stage>` dispatcher; root install     | (foundation)                |
| 01  | `01-render`    | `pixelrag_render` (`pixelshot`)           | Document → screenshot tiles (Playwright/CDP, PDF)   | none                        |
| 02  | `02-embed`     | `pixelrag_embed`                          | Tiles → vectors → FAISS index (chunk/embed/build)   | render output (data only)   |
| 03  | `03-index`     | `pixelrag_index`                          | Orchestrator: source → render → chunk → embed → idx | render + embed (code)       |
| 04  | `04-serve`     | `pixelrag_serve`                          | FAISS search API (FastAPI, text+image queries)      | index artifacts (data only) |
| 05  | `05-train`     | `wiki-screenshot-training` (separate env) | LoRA finetune Qwen3-VL-Embedding-2B + SFT recipes   | none (produces the adapter) |
| 06  | `06-web`       | Next.js + `agent-server.mjs`              | pixelrag.ai frontend + Claude Agent SDK chat backend| serve API + Anthropic       |
| 07  | `07-plugin`    | `pixelbrowse` Claude Code plugin + skill  | `/screenshot` command; `pixelshot` for agents       | pixelshot CLI               |
| 08  | `08-eval`      | `pixelrag-repro` (separate env)           | Paper Table-1 reproduction harness vs. live serves  | serve + reader serves       |
| 09  | `09-deploy`    | systemd + nginx + GitHub Actions          | CD, blue-green search API, CI, chromium build       | all runtime modules         |
| 10  | `10-demos`     | notebooks + scripts                       | Quickstart, e2e, render, agent-skill demos          | render + serve              |

## Reference directories (non-code context)

| Dir             | Contents                                                         |
| --------------- | ---------------------------------------------------------------- |
| `_source/`      | Raw clone of the repo (331 files, git history stripped)          |
| `_extracted/`   | This manifest + `links/` (URLs, domains, API endpoints, env) + `resources/` (integrations) + `decode/` (scan) |
| `build-config/` | Root `pyproject.toml` (umbrella wheel), `uv.lock`, `package.json`, dotfiles — the distribution that bundles modules 00–04 |
| `reference/`    | `README.md`, `LICENSE`, `CLAUDE.md`, `assets/`, `docs/`, `history/` |

## The five-package umbrella (modules 00–04)

The root `pyproject.toml` bundles **five Python packages into one `pixelrag` distribution**
(`[tool.hatch.build.targets.wheel] packages`). They share no import-time coupling except
where `03-index` calls `01-render` and `02-embed`:

```
render  ←──  index  ──→  embed       serve (independent)       train → serve (HTTP)
(pixelshot)  (orchestrator)          (FAISS search)             (separate env)
```

## Key coupling notes (gotchas)

1. **`pixelshot` is stage 0 and standalone.** It is the only primitive run by hand and stays
   light (no torch). Everything downstream either consumes its tiles or is invoked by the
   `pixelrag` umbrella.
2. **`05-train` is a separate `uv` project** (`wiki-screenshot-training`) with its own pinned
   env (`torch==2.9.1+cu129`, `transformers==4.57.1`, cuDNN 9.20). It is NOT installed from
   the root — run `cd train && uv sync`. Modules 00–04 never import it.
3. **`03-index` is the only orchestrator with cross-package imports** (`from pixelrag_render.render
   import render_urls, render_pdf`, and it shells out to `pixelrag_embed` chunk/embed/build CLIs).
4. **`04-serve` is runtime-independent of 02/03** — it loads a pre-built FAISS index + embeds
   queries itself with transformers. It never imports embed/index code.
5. **The trained adapter is published separately** (`Chrisyichuan/wiki-screenshot-embedding-lora`,
   `lora_vit/ckpt200`). `04-serve` and `05-train` reference it by HF path, not by local code.
6. **`06-web` runs the Claude Agent SDK** (`@anthropic-ai/claude-agent-sdk`) both as a Next.js
   `/api/chat` route and a standalone SSE `agent-server.mjs` — it proxies to the search API.
