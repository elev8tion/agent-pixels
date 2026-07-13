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
