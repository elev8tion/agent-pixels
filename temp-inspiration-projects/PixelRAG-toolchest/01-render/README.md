# 01-render — `pixelrag_render` / `pixelshot`

**Stage 0.** Renders documents (web pages, PDFs, local HTML/images) to **tiled JPEG/PNG
images**. This is the capture primitive the entire pipeline is built on, and it ships as the
standalone `pixelshot` CLI (`pip install pixelrag`).

```python
from pixelrag_render import render_url
tiles = render_url("https://en.wikipedia.org/wiki/Python", "./tiles")
```

## Architecture

Two-layer design: **connections** (how to talk to Chrome) × **strategies** (how to capture tiles).

```
src/pixelrag_render/
├── __init__.py            ← public API: render_url, render_pdf, render_file
├── render.py              ← public API + pixelshot CLI entrypoint (main)
├── chrome.py              ← Chrome/Chromium binary discovery (system/Playwright/CHROME_PATH)
├── strategies/
│   ├── base.py            ← TileCapture, ArticleCapture, ChromeConnection + CaptureStrategy protocols
│   ├── connection.py      ← WebsocketConnection (raw CDP), PlaywrightConnection
│   ├── cdp_sequential.py  ← ← shipped/used strategies
│   ├── cdp_directclip.py
│   ├── cdp_pertile_imgwait.py
│   └── cdp_oneshot.py
│   # (also present: cdp_fullpage, cdp_dc_single, cdp_pipelined_tabs, cdp_noscroll,
│   #  cdp_phased, cdp_pipelined_dc, cdp_dynamic, cdp_parallel, cdp_overlap,
│   #  cdp_multitab — experimental throughput variants documented in docs/screenshot-throughput-optimization.md)
├── backends/
│   ├── cdp.py             ← CDP backend (default, fastest)
│   ├── pdf.py             ← PDF → tiles (requires poppler; `pip install 'pixelrag[pdf]'`)
│   └── fast_cdp.py        ← turbo headless_shell path (linux-x64 auto-install)
└── bench/
    └── bench_throughput.py ← rendering throughput benchmark
```

## Key design points

- **`strategies/base.py`** defines the contracts: `ChromeConnection` (Protocol: `cdp()`,
  `close()`) and `CaptureStrategy` (Protocol). `TileCapture`/`ArticleCapture` dataclasses
  hold raw capture results + timing metadata (`shot_ms`, `nav_ms`, `clip_y`, `clip_h`).
- **Connection abstraction** lets strategies be backend-agnostic: a strategy works against
  either a raw CDP websocket or a Playwright session.
- **`chrome.py`** auto-detects Chrome across platforms — bundled turbo `headless_shell`
  (linux-x64 only), else system Chrome/Chromium/Playwright, else `CHROME_PATH` env. Each
  render runs in an isolated throwaway profile.
- **Output layout:** `{output_dir}/{stem}.png.tiles/` → `tile_XXXX.png` (+ `chunks.json`
  written later by `02-embed`'s chunker).

## Dependencies

`pillow`, `websockets`, `pymupdf`, `pyturbojpeg`, `cef-capi-py`, `anthropic`. Optional extras:
`[playwright]`, `[pdf]`. **No torch** — this is the light stage.

## CLI

```bash
pixelshot <url|file> [<url2> ...] -o ./tiles [--tile-height 8192] [--quality 85]
    [--viewport-width 875] [--workers 4] [--backend cdp] [--dpi 200]  # for PDFs
```

Also includes `chrome-build/` — a Chromium source patch (`pixelrag-chrome.patch`) and a
`build-headless-shell.sh` for building a patched `headless_shell` with screenshot optimizations
(see `09-deploy/chromium/` and `docs/screenshot-throughput-optimization.md` for the rationale).

## Internal dependencies

**None.** This module consumes nothing internal — it's the foundation primitive.

## Repurpose

The connection/strategy split is the reusable gem: drop in any new capture strategy
(implement `CaptureStrategy`) and it works against either CDP or Playwright connections.
The tile-output contract (`{stem}.png.tiles/tile_XXXX.png`) is what `02-embed` and `03-index`
expect.

## Refinement Report

Ran the native cleansed pipeline (scan → clean → validate → analyze → package). Cleaned source, manifest, and full analysis live in `refined/`.

- **Items extracted:** 189  (python: 189)
- **Source files scanned:** 27
- **Syntax validation:** 170 valid / 19 invalid
  - ⚠️ 19 invalid — all `SyntaxError: unexpected indent (line 2)`: class attributes/properties/methods extracted *out of class context*, so the standalone fragment has a stray indent. **The source is valid**; only the extracted fragment is malformed. No action needed on `_source/`.
- **Imports cleaned:** 7058 lines of cleaned output from 7298 raw lines (0 cleansed annotations; 0 relative-import TODOs flagged for manual resolution)
- **Health score:** 34/100 — Low — 15 capture-strategy variants share near-identical `_capture_one` structure (high duplication); many long methods (330-line `_run_render`, 201-line `_capture_one`). The variants are intentional throughput experiments (see docs/screenshot-throughput-optimization.md), not accidental copy-paste — refactor only if consolidating to a single strategy.
  - Long functions: 30 · Duplications: 20 · High-coupling items: 20 · Cross-module deps: 0
- **Dead code:** 162 flagged (49 high-confidence) — ⚠️ totals are inclusive (count reverse-edge = 0 in the extracted symbol graph); many are public APIs, CLI entrypoints, `__main__` guards, or JSX-only UI refs. **Review only the high-confidence subset** before removing anything.
- **Package manifest:** generated (`requirements.txt`)

See `refined/README.md` for the full item table and `refined/manifest.json` for the machine-readable extraction manifest.
