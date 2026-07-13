# 02-embed — `pixelrag_embed`

**Stages: chunk → embed → build-index.** Consumes the tile directories that `01-render`
produces and turns them into a searchable FAISS vector index.

```bash
pip install 'pixelrag[embed]'
pixelrag chunk   --tiles-dir ./tiles
pixelrag embed   --shard-dir ./tiles --output-dir ./embeddings --gpu-ids 0,1
pixelrag build-index --embeddings-dir ./embeddings --output-dir ./index
```

## Architecture

```
src/pixelrag_embed/
├── __init__.py
├── chunk.py     ← Stage: pre-chunk tile images into model-sized (≤1024px) pieces
├── embed.py     ← Stage: embed chunks with Qwen3-VL (vLLM / sglang / transformers) → .npz
├── embed_cpu.py ← CPU/MPS embedding path (for the [index] local-build flow)
└── index.py     ← Stage: merge shard .npz → build FAISS IVF index + test
```

Each stage is an independently runnable `main()` CLI (the `pixelrag` umbrella in `00-shared`
dispatches `chunk`/`embed`/`build-index` here).

## Key design points

### `chunk.py` — the chunker
Splits each `tile_XXXX.png` into a grid of **≤1024px-tall × ≤viewport_width-wide** chunks
(`chunk_XXXX_YY.png`), writing a `chunks.json` manifest with each chunk's
`x_offset/y_offset/width/height`. Narrow web tiles keep single-column strips; wider sources
(PDFs, landscape) also split along width. Constants: `CHUNK_HEIGHT=1024`,
`MIN_CHUNK_HEIGHT=28` (one Qwen3-VL patch). Chunking reduces visual tokens ~8×.

### `embed.py` — the embedder
Scans a shard dir, embeds chunks, writes **`.npz` shards** with a rich typed schema:
```
embeddings[N,D] float16   article_ids[N] int64   tile_indices[N] int32
chunk_indices[N] int32    y_offsets[N] int32     tile_heights[N] int32
page_heights[N] int32     viewport_widths[N] int32
image_hashes[N] S32       (MD5 — dedup & patching)
tile_paths[N] S512        shard_id scalar int32
```
Lookup key: `(article_id, tile_index, chunk_index)` lexsorted. Supports multiple backends
(`--backend sglang|vllm|transformers`), multi-GPU (`--gpu-ids`), multiprocessing with careful
atexit cleanup (kills persistent pools before multiprocessing's join handler can hang).
Manages a vLLM/sglang embedding server subprocess.

### `index.py` — the indexer
Merges all `shard_*.npz`, dedups by `image_hashes`, builds a FAISS `IndexIVFFlat` (configurable
`--nlist`/`--nprobe`), tests search. DiskANN backend available.

## Internal dependencies

- **Consumes (data only):** `01-render`'s tile output format (`*.png.tiles/`). Does **not**
  import any render code.
- **Consumed by:** `03-index` (which shells out to these CLIs) and `04-serve` (which loads the
  resulting index).

## Repurpose

`chunk.py` + `embed.py`'s `.npz` schema + `index.py`'s FAISS builder are a complete,
reusable "images → searchable vector index" pipeline independent of PixelRAG's document
rendering. The typed `.npz` contract (especially `image_hashes` for dedup/patching and the
`(article_id, tile_index, chunk_index)` key) is the stable interface between embed and serve.
