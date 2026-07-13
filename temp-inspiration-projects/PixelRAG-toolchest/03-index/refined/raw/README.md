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
