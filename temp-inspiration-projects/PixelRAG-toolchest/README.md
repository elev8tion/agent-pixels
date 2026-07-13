# PixelRAG Toolchest

A **numbered, dependency-ordered toolchest** extracted from
[`StarTrail-org/PixelRAG`](https://github.com/StarTrail-org/PixelRAG) — the Berkeley SkyLab /
BAIR / NLP **visual Retrieval-Augmented Generation** system.

> **PixelRAG** renders documents (web pages, PDFs, images) as screenshot tiles and retrieves
> over the images directly with a LoRA-fine-tuned `Qwen3-VL-Embedding-2B`, so visual structure
> that text parsing throws away — tables, charts, layout, infographics — stays intact. A
> pre-built index of **8.28M Wikipedia pages** is served live at `api.pixelrag.ai`.
>
> Paper: *PIXELRAG: Web Screenshots Beat Text for Retrieval-Augmented Generation*.

---

## What's in here

```
PixelRAG-toolchest/
├── _source/        ← raw clone of the repo (331 files, git-stripped)
├── _extracted/     ← manifest.md + links/ + resources/ + decode/ (extraction analysis)
├── build-config/   ← root pyproject.toml (umbrella wheel), uv.lock, package.json, dotfiles
├── reference/      ← README, LICENSE, CLAUDE.md, assets/, docs/, history/
│
├── 00-shared/      ← `pixelrag` umbrella CLI (the `pixelrag <stage>` dispatcher)
├── 01-render/      ← `pixelrag_render` / `pixelshot` — document → screenshot tiles
├── 02-embed/       ← `pixelrag_embed` — tiles → vectors → FAISS index
├── 03-index/       ← `pixelrag_index` — orchestrator (source→render→chunk→embed→index)
├── 04-serve/       ← `pixelrag_serve` — FAISS search API (FastAPI)
├── 05-train/       ← `wiki-screenshot-training` (separate uv env) — LoRA finetune + SFT
├── 06-web/         ← Next.js frontend (pixelrag.ai) + Claude Agent SDK chat backend
├── 07-plugin/      ← `pixelbrowse` Claude Code plugin + skills
├── 08-eval/        ← `pixelrag-repro` (separate uv env) — paper Table-1 harness
├── 09-deploy/      ← CD, blue-green search API, CI, chromium build patches
└── 10-demos/       ← quickstart notebook + e2e + render + agent-skill demos
```

> Each numbered module also has a `refined/` subdir with the cleansed pipeline output:
> cleaned source, `manifest.json`, `requirements.txt`/`package.json`, and a full health
> analysis (long functions, duplications, coupling, dead-code). See **Refinement Summary**
> below and each module's appended *Refinement Report*.

## Module index

| #   | Module       | Package / Surface                  | Role · **Health**                                 | Depends on (internal)        |
| --- | ------------ | ---------------------------------- | ------------------------------------------------- | ---------------------------- |
| 00  | `00-shared`  | `pixelrag` CLI                     | Umbrella dispatcher; root install · **70**        | — (foundation)               |
| 01  | `01-render`  | `pixelrag_render` / `pixelshot`    | Document → screenshot tiles (CDP/PDF) · **34**    | —                            |
| 02  | `02-embed`   | `pixelrag_embed`                   | Tiles → vectors → FAISS index · **68**            | render output (data)         |
| 03  | `03-index`   | `pixelrag_index`                   | Orchestrator (only cross-package importer) · **56** | **render + embed (code)**  |
| 04  | `04-serve`   | `pixelrag_serve`                   | FAISS search API (text + image queries) · **68**  | index artifacts (data)       |
| 05  | `05-train`   | `wiki-screenshot-training`         | LoRA finetune + reader SFT · **49**               | — (produces the adapter)     |
| 06  | `06-web`     | Next.js + agent-server.mjs         | pixelrag.ai + Claude Agent SDK chat · **54**      | serve API + Anthropic        |
| 07  | `07-plugin`  | `pixelbrowse` plugin + skill       | `/screenshot` for Claude Code · *non-code (n/a)*  | pixelshot CLI                |
| 08  | `08-eval`    | `pixelrag-repro`                   | Paper Table-1 reproduction · **60**               | serve + reader serves        |
| 09  | `09-deploy`  | systemd + nginx + GH Actions       | CD, blue-green, CI · *non-code (n/a)*             | all runtime modules          |
| 10  | `10-demos`   | notebooks + scripts                | Quickstart, e2e, render · **70**                  | render + serve               |

## Dependency graph

```
                    ┌─────────────┐
                    │  00-shared  │  pixelrag umbrella CLI
                    └──────┬──────┘
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
   ┌─────────┐       ┌─────────┐       ┌─────────┐
   │01-render│       │02-embed │       │04-serve │   (independent)
   │pixelshot│       │chunk/   │       │FAISS API│
   └────┬────┘       │embed/idx│       └────┬────┘
        │            └────┬────┘            │
        │   (data: tiles) │                 │
        └──────►┌─────────┴──┐◄─────(data: index + articles.json)
               │  03-index   │              │
               │ orchestrator│              │
               └─────────────┘              │
                                            ▼
   ┌─────────┐                         ┌─────────┐    ┌─────────┐
   │05-train │ ──(adapter:HF)──▶ 04-serve │ 06-web  │    │08-eval  │
   │LoRA+SFT │                         └────┬────┘    └─────────┘
   └─────────┘                              │
                                  ┌─────────┴─────────┐
                                  ▼                   ▼
                             ┌─────────┐         ┌─────────┐
                             │07-plugin│         │10-demos │
                             │Claude eye│        │notebooks│
                             └─────────┘         └─────────┘

   09-deploy wraps 04-serve + 06-web agent in systemd/nginx/CD.
```

Solid arrow = code import. `(data: …)` = consumes artifacts, not code. `(adapter:HF)` =
references the trained LoRA by Hugging Face path.

## The five-package umbrella (00–04)

The root `pyproject.toml` (`build-config/`) bundles **five Python packages into one `pixelrag`
distribution** via `[tool.hatch.build.targets.wheel] packages`. Modules 00–04 share almost no
import-time coupling — the **only** cross-package code import is in `03-index`, which imports
`pixelrag_render.render` and shells out to `pixelrag_embed` CLIs. `04-serve` is fully
runtime-independent: it loads the index artifacts and embeds queries itself.

```
render  ←──  index  ──→  embed       serve (independent)       train → serve (HTTP)
```

## Extraction notes

- **Source-only repo.** Magic-byte scan confirmed every file is text (Python/TS/JS/shell/YAML/
  JSON/MD) or a media asset (PNG/JPEG/MP4/PDF/ICO). **No decompilation, no archives, no source
  maps, no encoded blobs** — extraction is a faithful copy (see `_extracted/manifest.md`).
- **Two separate `uv` projects** are preserved as-is: `05-train` (`wiki-screenshot-training`,
  torch 2.9.1+cu129 / transformers 4.57.1 / cuDNN 9.20) and `08-eval` (`pixelrag-repro`). They
  are NOT installed from the root — each has its own `uv.lock`.
- See `_extracted/links/` for all URLs, domains, API endpoints, and env vars; `_extracted/
  resources/integrations.md` for HF datasets/models, PyPI/npm deps, and cloud/AI providers.

## Refinement Summary

The native cleansed pipeline ran per-module (scan → clean → validate → analyze → package).
Results live in each module's `refined/` (cleaned source, `manifest.json`, package manifest,
and a health-analysis `README.md`). Per-module highlights are appended to each module README.

| Module | Health | Items | Valid/Invalid | Dead (total/high) | Long fns | Package |
| ------ | -----: | ----: | ------------ | -----------------: | -------: | ------- |
| 00-shared | **70** | 2 | 2/0 | 2 / 1 | 1 | requirements.txt |
| 01-render | **34** | 189 | 170/19 | 162 / 49 | 30 | requirements.txt |
| 02-embed | **68** | 58 | 58/0 | 55 / 47 | 30 | requirements.txt |
| 03-index | **56** | 80 | 76/4 | 70 / 15 | 30 | requirements.txt |
| 04-serve | **68** | 45 | 45/0 | 33 / 18 | 21 | requirements.txt |
| 05-train | **49** | 352 | 347/5 | 335 / 240 | 30 | requirements.txt |
| 06-web | **54** | 95 | 95/0 | 93 / 93 | 15 | package.json |
| 07-plugin | n/a | — | — | — | — | (non-code) |
| 08-eval | **60** | 270 | 262/8 | 235 / 127 | 30 | requirements.txt |
| 09-deploy | n/a | — | — | — | — | (non-code) |
| 10-demos | **70** | 15 | 15/0 | 13 / 10 | 10 | requirements.txt |

**Totals:** 1306 items extracted · 1268 valid / 36 invalid · 1338 dead-code flags (598 high-confidence) · 9 package manifests.

### How to read these numbers

- **Health score** blends long-function count, duplication (MinHash LSH), and coupling
  (forward/reverse edges in the symbol graph). Lower = more refactoring debt.
- **36 invalid items are all the same artifact**, not real bugs: `SyntaxError: unexpected
  indent (line 2)` on class attributes/properties/methods extracted *out of class context*.
  **The source in `_source/` is valid** — only the standalone extracted fragment is malformed.
- **Dead-code totals are inclusive** (any item with zero reverse edges). They over-count
  heavily because public APIs, CLI entrypoints, `__main__` guards, and JSX-only UI references
  all look "unreferenced" to the static scanner. **Review only the high-confidence column.**
- **07-plugin** and **09-deploy** are config/ops/docs modules (JSON, Markdown, shell, YAML,
  systemd, nginx, diffs) — the scanner supports none of these, so there's nothing to refine.
  See their `refined/REFINE_NOTES.md`.

### Highest-leverage refactors (if you act on this)

1. **`01-render` (health 34)** — 15 CDP capture-strategy variants with near-identical
   `_capture_one` bodies (high duplication). These are *intentional* throughput experiments
   (documented in `reference/docs/screenshot-throughput-optimization.md`) — consolidate only
   if you're committing to one strategy. `_run_render` (330 lines) is the single longest fn.
2. **`05-train` (health 49)** — the data-curation scripts (`generate_query_pairs.py`, the
   `filter_*` cascade, `mine_*`) share CLI/IO boilerplate; a shared `cli.py` would cut
   duplication. Many "dead" items are script `main()`s and upload helpers — keep them.
3. **`03-index` (health 56)** — `monitor.py` has a 367-line `render()` and 327-line `main()`;
   `pipelines.py::build` is 270 lines. Worth splitting for readability.

## Where to start reading

- **Want the product?** → `reference/README.md` + `10-demos/quickstart.ipynb`
- **Want to render pages?** → `01-render/` (start at `render.py` + `strategies/base.py`)
- **Want to build/search an index?** → `03-index/` (orchestrator) → `04-serve/` (search API)
- **Want the embedding model?** → `05-train/` (`train_contrastors.py` + `docs/reproduce_v8r.md`)
- **Want the web app / agent?** → `06-web/` (`agent-server.mjs` is the production agent)
- **Want to give Claude eyes?** → `07-plugin/` (`skills/pixelbrowse/SKILL.md`)
- **Want ops?** → `09-deploy/` (`api-switch.sh` blue-green + `deploy/README.md`)

## Reusability highlights

| If you want… | Take… |
| ------------ | ----- |
| A connection/strategy-abstraction for Chrome screenshot capture | `01-render/strategies/` |
| An images → typed-`.npz` → FAISS index pipeline | `02-embed/` |
| A pluggable `Source` ingestion + multi-stage YAML orchestrator | `03-index/` |
| A "load index + embed query + serve ranked images" FastAPI service | `04-serve/api.py` |
| A contrastive ViT-LoRA image/text embedding trainer | `05-train/train_contrastors.py` + `dataset.py` |
| Synthetic-RAG data curation (query gen + filter cascade + hard-neg mining) | `05-train/` data scripts |
| Claude Agent SDK on a server with subscription auth + budget caps + rate limits | `06-web/agent-server.mjs` |
| A tool-backed Claude Code skill template | `07-plugin/` |
| nginx blue-green cutover with health-check + graceful reload + rollback | `09-deploy/api-switch.sh` |
| A multi-benchmark Vis-RAG eval harness (SimpleQA/LiveVQA/Monaco) | `08-eval/lib/` |

## License

Apache-2.0 (see `reference/LICENSE`). Extraction is faithful to the original; per-module
READMEs cite upstream paths.
