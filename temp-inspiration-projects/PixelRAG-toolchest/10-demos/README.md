# 10-demos — quickstart, e2e, render, agent-skill

Runnable examples showing how to use the pipeline end-to-end. The headline demo is the Colab
notebook referenced in the root README.

## Files

```
quickstart.ipynb        ← ★ Colab notebook: render a page + search the hosted index (images inline)
e2e/
├── run.py              ← full local end-to-end: pixelrag.yaml → index build → serve → search
├── pixelrag.yaml       ← sample config for the e2e run
└── README.md
render/
├── run.py              ← standalone render demo (pixelshot API)
└── README.md
agent_skill.py          ← demo: use the pixelbrowse agent skill to read a page
search_ui.html          ← static HTML UI for the search API
```

## How they fit

- **`quickstart.ipynb`** — the zero-setup path: renders one page with `pixelshot` and queries
  the **hosted** `api.pixelrag.ai` (no local index, no GPU).
- **`e2e/run.py`** — the full local path: uses `03-index`'s config to build an index from a
  local source, then `04-serve` to search it. `e2e/pixelrag.yaml` is a ready config.
- **`render/run.py`** — just `01-render`'s `render_url` API in isolation.
- **`agent_skill.py`** — exercises `07-plugin`'s pixelbrowse flow programmatically.

## Internal dependencies

- `quickstart.ipynb`, `search_ui.html`, `agent_skill.py` → **`04-serve`** (hosted API).
- `e2e/`, `render/` → **`01-render`** + **`03-index`** + **`04-serve`** (local stack).

## Repurpose

`e2e/run.py` + `e2e/pixelrag.yaml` is a copy-paste starter for "build a local PixelRAG index
from my documents and search it." `quickstart.ipynb` is the template for a no-setup hosted-API
demo notebook.

## Refinement Report

Ran the native cleansed pipeline (scan → clean → validate → analyze → package). Cleaned source, manifest, and full analysis live in `refined/`.

- **Items extracted:** 15  (html: 4, python: 11)
- **Source files scanned:** 9
- **Syntax validation:** 15 valid / 0 invalid
- **Imports cleaned:** 323 lines of cleaned output from 656 raw lines (0 cleansed annotations; 0 relative-import TODOs flagged for manual resolution)
- **Health score:** 70/100 — Good — small, clean module.
  - Long functions: 10 · Duplications: 0 · High-coupling items: 3 · Cross-module deps: 0
- **Dead code:** 13 flagged (10 high-confidence) — ⚠️ totals are inclusive (count reverse-edge = 0 in the extracted symbol graph); many are public APIs, CLI entrypoints, `__main__` guards, or JSX-only UI refs. **Review only the high-confidence subset** before removing anything.
- **Package manifest:** generated (`requirements.txt`)

See `refined/README.md` for the full item table and `refined/manifest.json` for the machine-readable extraction manifest.
