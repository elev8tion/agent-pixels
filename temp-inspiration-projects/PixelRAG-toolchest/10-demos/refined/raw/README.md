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
