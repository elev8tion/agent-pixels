# 03-index — `pixelrag_index`

**The orchestrator.** Drives the full end-to-end pipeline:
`source → ingest (render) → chunk → embed → build index`. This is the one module with
**cross-package imports** into `01-render` and `02-embed`.

```bash
pip install 'pixelrag[index]'
pixelrag index build      # reads pixelrag.yaml, runs all stages
pixelrag monitor          # live pipeline monitoring
```

## Architecture

```
src/pixelrag_index/
├── __init__.py
├── config.py        ← parse pixelrag.yaml; make_source() factory
├── pipelines.py     ← build(): the 4-stage orchestrator (entrypoint: main)
├── monitor.py       ← live progress monitor (entrypoint: main)
├── distributed.py   ← distributed/S3 ([distributed] extra, boto3)
└── sources/
    ├── __init__.py   ← SOURCES registry {local, web, pdf, kiwix}
    ├── base.py       ← ★ Document(id,url,path,metadata) + abstract Source iterator
    ├── local.py      ← local files / dirs (incl. PDFs)
    ├── web.py        ← crawl/fetch URLs
    ├── pdf.py        ← PDF source
    └── kiwix.py      ← Kiwix .zim archive source ([kiwix] extra, libzim)
```

## The shared contract: `Document` / `Source`

`sources/base.py` is the **cross-cutting type** of the whole orchestrator:

```python
@dataclass
class Document:
    id: str
    url: str | None = None
    path: str | None = None
    metadata: dict = field(default_factory=dict)

class Source:
    def __iter__(self) -> Iterator[Document]: ...
    def __len__(self) -> int: ...
```

Every source implements this; `pipelines.py` consumes it. (This is conceptually the
`00-shared` interface but physically lives here because nothing else outside index needs it.)

## Config: `pixelrag.yaml`

```yaml
source: { type: local, path: ./my_docs }   # or web / pdf / kiwix
ingest: { backend: cdp, quality: 85, tile_height: 8192 }
embed:  { model: Qwen/Qwen3-VL-Embedding-2B, device: auto }  # cuda / mps / cpu
output: ./my_index
```

`config.py` merges with `DEFAULT_CONFIG` and `make_source()` expands `~` in path-like values
and dispatches to `SOURCES[type]`.

## How `build()` wires the stages

`pipelines.py::build()` is the only place modules couple at the code level:

1. `make_source(config)` → materialize `list[Document]`
2. **Render:** `from pixelrag_render.render import render_urls, render_pdf` → batch by type
   (urls / pdfs / images / text), assign sequential IDs
3. **Chunk + Embed + Build:** shells out to the `pixelrag_embed` CLIs (`chunk`, `embed`,
   `build-index`) via subprocess
4. Writes `articles.json` (id→url/path/metadata) for `04-serve` to consume

## Internal dependencies

- **Imports `01-render`** directly (`pixelrag_render.render`).
- **Invokes `02-embed`** via CLI subprocess (chunk/embed/build-index).
- **Consumed by:** nothing at code level — it produces artifacts (`index/`, `tiles/`,
  `articles.json`) that `04-serve` loads.

## Repurpose

The `Source` plugin pattern (`SOURCES` registry + `Document` contract) is a clean template for
pluggable ingestion. To add a source: implement `Source`, register in `sources/__init__.py`.
The config-driven YAML → stage dispatch in `config.py` + `pipelines.py` is reusable for any
multi-stage data pipeline that shells out to sub-CLIs.

## Refinement Report

Ran the native cleansed pipeline (scan → clean → validate → analyze → package). Cleaned source, manifest, and full analysis live in `refined/`.

- **Items extracted:** 80  (python: 80)
- **Source files scanned:** 12
- **Syntax validation:** 76 valid / 4 invalid
  - ⚠️ 4 invalid — all `SyntaxError: unexpected indent (line 2)`: class attributes/properties/methods extracted *out of class context*, so the standalone fragment has a stray indent. **The source is valid**; only the extracted fragment is malformed. No action needed on `_source/`.
- **Imports cleaned:** 2831 lines of cleaned output from 2586 raw lines (0 cleansed annotations; 0 relative-import TODOs flagged for manual resolution)
- **Health score:** 56/100 — Moderate — the orchestrator. Long functions in `monitor.py` (367-line `render`, 327-line `main`) and `pipelines.py::build` (270 lines) dominate. Consider splitting the monitoring dashboard logic.
  - Long functions: 30 · Duplications: 6 · High-coupling items: 20 · Cross-module deps: 0
- **Dead code:** 70 flagged (15 high-confidence) — ⚠️ totals are inclusive (count reverse-edge = 0 in the extracted symbol graph); many are public APIs, CLI entrypoints, `__main__` guards, or JSX-only UI refs. **Review only the high-confidence subset** before removing anything.
- **Package manifest:** generated (`requirements.txt`)

See `refined/README.md` for the full item table and `refined/manifest.json` for the machine-readable extraction manifest.
