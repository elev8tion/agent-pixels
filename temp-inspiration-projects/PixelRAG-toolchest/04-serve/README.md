# 04-serve — `pixelrag_serve`

**FAISS visual search API.** A FastAPI server that loads a pre-built index and answers text
**or image** queries by embedding them with `Qwen3-VL-Embedding-2B` and searching FAISS.

```bash
pip install 'pixelrag[serve]'
pixelrag serve --index-dir ./index --port 30001
```

## Endpoints

| Method | Path                                              | Purpose                                  |
| ------ | ------------------------------------------------- | ---------------------------------------- |
| POST   | `/search`                                         | Text or image query → top-k tiles        |
| GET    | `/tile/{article_id}/{tile_index}/{chunk_index}`   | Fetch a result tile image                |
| GET    | `/tile`                                           | Generic tile fetch                       |
| POST   | `/reconstruct`                                    | Reconstruct/retrieve tile data           |
| GET    | `/health`                                         | Liveness                                 |
| GET    | `/status`                                         | Index/model/device info                  |

## Architecture

```
src/pixelrag_serve/
├── __init__.py
├── api.py                ← ★ FastAPI app + pixelrag-serve CLI (main). Loads index, embeds queries.
├── render_ondemand.py    ← render a URL to tiles on-the-fly for live/unknown docs
├── zim_server.py         ← serve over a Kiwix .zim document store
└── zim_server_async.py   ← async variant
```

## Key design points

- **Runtime-independent of `02-embed`/`03-index`.** It never imports them. It loads the
  **artifacts** they produce (the FAISS index dir + `articles.json`) and embeds queries
  itself with a local transformers inference path (SDPA attention).
- **Query embedding** uses the same `Qwen/Qwen3-VL-Embedding-2B` model the index was built
  with, optionally loading the trained LoRA adapter (`Chrisyichuan/wiki-screenshot-embedding-lora`).
  Produces embeddings aligned with the `direct_gpu` pipeline (cosine = 1.0).
- **Per-request tracing:** a `contextvars.ContextVar` `_request_id_ctx` propagates a sanitized
  request ID across async context switches (`_sanitize_request_id` caps at 64 chars).
- **Device-aware:** `--device cuda|cpu|mps`. The hosted `api.pixelrag.ai` runs this on GPU
  behind nginx (blue-green — see `09-deploy`).
- Supports both **text queries** (`{"text": "..."}`) and **image queries** (visual search).

## Internal dependencies

- **Consumes (data only):** the FAISS index + `articles.json` produced by `03-index`.
- **Consumed by:** `06-web` (the chat agent calls `/search`), `08-eval` (paper repro), and
  `10-demos`.

## Repurpose

`api.py` is a textbook "load a vector index, embed a query, search, return ranked image
results with CORS + tracing" FastAPI service. The `/tile/{...}` path + on-demand render
(`render_ondemand.py`) is a reusable pattern for serving visual retrieval results to a browser.

## Refinement Report

Ran the native cleansed pipeline (scan → clean → validate → analyze → package). Cleaned source, manifest, and full analysis live in `refined/`.

- **Items extracted:** 45  (python: 45)
- **Source files scanned:** 6
- **Syntax validation:** 45 valid / 0 invalid
- **Imports cleaned:** 886 lines of cleaned output from 1040 raw lines (0 cleansed annotations; 0 relative-import TODOs flagged for manual resolution)
- **Health score:** 68/100 — Good — clean, well-factored. Minor long-function flags in the embedding/index CLIs.
  - Long functions: 21 · Duplications: 1 · High-coupling items: 20 · Cross-module deps: 0
- **Dead code:** 33 flagged (18 high-confidence) — ⚠️ totals are inclusive (count reverse-edge = 0 in the extracted symbol graph); many are public APIs, CLI entrypoints, `__main__` guards, or JSX-only UI refs. **Review only the high-confidence subset** before removing anything.
- **Package manifest:** generated (`requirements.txt`)

See `refined/README.md` for the full item table and `refined/manifest.json` for the machine-readable extraction manifest.
