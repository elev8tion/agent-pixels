# 00-shared — `pixelrag` umbrella CLI

The root install unit and the `pixelrag <stage>` command. This is the **foundation module**
every other module hangs off of — it's what `pip install pixelrag` installs at its lightest
(core only, no torch), and it lazily dispatches to each pipeline stage's own CLI.

## What it does

`pixelrag` is an **umbrella dispatcher**. It does not contain any pipeline logic. It maps a
stage name → `(module, function, package, pip-extra)` and lazily imports the stage, printing
a clear install hint if the optional dependency is missing.

```python
# src/pixelrag/cli.py
STAGES = {
    "chunk":       ("pixelrag_embed.chunk",     "main", "pixelrag-embed",  "embed"),
    "embed":       ("pixelrag_embed.embed",     "main", "pixelrag-embed",  "embed"),
    "build-index": ("pixelrag_embed.index",     "main", "pixelrag-embed",  "embed"),
    "index":       ("pixelrag_index.pipelines", "main", "pixelrag-index",  "index"),
    "monitor":     ("pixelrag_index.monitor",   "main", "pixelrag-index",  "index"),
    "serve":       ("pixelrag_serve.api",       "main", "pixelrag-serve",  "serve"),
}
```

Note: **stage 0 (capture → screenshot tiles) is NOT here** — it's the standalone `pixelshot`
command (`01-render`), kept separate because it's the one primitive you run by hand and it
stays dependency-light.

## Files

- `src/pixelrag/__init__.py` — package docstring
- `src/pixelrag/cli.py` — the `main()` dispatcher (`pixelrag` entrypoint)

## Install

```bash
pip install pixelrag          # core only — pixelshot + the umbrella
```

## Cross-module note: the `Document`/`Source` contract

The other shared type in this codebase — `Document` (id, url, path, metadata) and the
abstract `Source` iterator — physically lives in `03-index/src/pixelrag_index/sources/base.py`
because it's tightly coupled to the orchestrator. It's the contract that all document sources
(local, web, pdf, kiwix) implement and that `03-index/pipelines.py` consumes. See that module
when you need the source interface.

## How to repurpose

This dispatcher pattern (umbrella CLI → lazily-import optional stages with install hints) is a
clean template for any multi-stage tool with heavy optional dependencies. Copy `cli.py` and
swap the `STAGES` table.

## Refinement Report

Ran the native cleansed pipeline (scan → clean → validate → analyze → package). Cleaned source, manifest, and full analysis live in `refined/`.

- **Items extracted:** 2  (python: 2)
- **Source files scanned:** 3
- **Syntax validation:** 2 valid / 0 invalid
- **Imports cleaned:** 38 lines of cleaned output from 69 raw lines (0 cleansed annotations; 0 relative-import TODOs flagged for manual resolution)
- **Health score:** 70/100 — Good — small, clean module.
  - Long functions: 1 · Duplications: 0 · High-coupling items: 0 · Cross-module deps: 0
- **Dead code:** 2 flagged (1 high-confidence) — ⚠️ totals are inclusive (count reverse-edge = 0 in the extracted symbol graph); many are public APIs, CLI entrypoints, `__main__` guards, or JSX-only UI refs. **Review only the high-confidence subset** before removing anything.
- **Package manifest:** generated (`requirements.txt`)

See `refined/README.md` for the full item table and `refined/manifest.json` for the machine-readable extraction manifest.
