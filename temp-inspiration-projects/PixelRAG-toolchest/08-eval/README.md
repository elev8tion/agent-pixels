# 08-eval — `pixelrag-repro` (separate uv project)

The **paper-reproduction harness**. Drives the PixelRAG paper's Table-1 evaluation against
**live retrieval + reader serves** (no local torch/vLLM needed — the model serves are remote
HTTP endpoints). Separate `uv` project, pinned deps.

```bash
cd 08-eval && uv sync
```

## What it reproduces

PixelRAG paper: *PIXELRAG: Web Screenshots Beat Text for Retrieval-Augmented Generation*.
The harness drives the paper's own scripts (`yichuan-w/Vis-RAG @ e591fd0`) —
`run_naive_simpleqa.py`, `simpleqa/`, `evaluate.py` — against live serves.

## Files

```
run_bench.py            ← main benchmark runner
run_livevqa.py          ← LiveVQA / WorldVQA evaluation
run_monaco.py           ← Monaco benchmark
reproduce.sh            ← one-shot reproduction script
serve_up.sh             ← bring up the retrieval/reader serves
repro_assets/           ← judge prompts (judge_worldvqa_prompt.txt, simpleqa_grader_template.txt)
PAPER_EXPERIMENT_MAP.md ← maps paper experiments → scripts
REPRODUCE.md            ← full repro recipe
REPRODUCE_PROGRESS.txt  ← progress log
pyproject.toml          ← pinned: aiohttp, datasets, openai, selenium, litellm, fastmcp, trafilatura, ...
lib/
├── retrievers.py     ← retrieval backends (PixelRAG + text baselines)
├── retrieval.py      ← retrieval orchestration
├── benchmarks.py     ← benchmark definitions (SimpleQA, LiveVQA, Monaco, ...)
├── simpleqa_data.py, simpleqa_filter.py  ← SimpleQA dataset loading/filtering
├── pixel_query.py    ← PixelRAG-specific query construction
├── screenshot.py     ← screenshot capture for eval
├── llm.py            ← LLM client (openai/litellm) for the reader + grader
├── grader.py         ← answer grading (SimpleQA-style)
└── model_config.py   ← model registry (reader models, endpoints)
```

## Key design points

- **Serve-driven, not local-model-driven.** Retrieval and reading both run as remote HTTP
  serves, so this env needs no GPU/torch — just API clients (`openai`, `litellm`,
  `fastmcp` for MCP-served models).
- **Selenium** for live page capture where needed; **trafilatura** for text baselines.
- **Multi-benchmark** via `lib/benchmarks.py`; grader uses the SimpleQA template.

## Internal dependencies

- **Calls `04-serve`'s `/search`** (the PixelRAG retriever) + remote reader serves.
- Standalone otherwise (separate pinned env).

## Repurpose

`lib/` is a reusable **multi-benchmark Vis-RAG evaluation harness**: pluggable retrievers
(`retrievers.py`), a model registry (`model_config.py`), an LLM client abstraction, and a
SimpleQA-style grader. Swap in your own retriever/reader and benchmark on SimpleQA / LiveVQA /
Monaco without standing up the training stack.

## Refinement Report

Ran the native cleansed pipeline (scan → clean → validate → analyze → package). Cleaned source, manifest, and full analysis live in `refined/`.

- **Items extracted:** 270  (python: 270)
- **Source files scanned:** 24
- **Syntax validation:** 262 valid / 8 invalid
  - ⚠️ 8 invalid — all `SyntaxError: unexpected indent (line 2)`: class attributes/properties/methods extracted *out of class context*, so the standalone fragment has a stray indent. **The source is valid**; only the extracted fragment is malformed. No action needed on `_source/`.
- **Imports cleaned:** 13431 lines of cleaned output from 13613 raw lines (0 cleansed annotations; 0 relative-import TODOs flagged for manual resolution)
- **Health score:** 60/100 — Moderate — eval harness with large `retrieval.py` (4000+ lines, many benchmark-specific methods). Dead code flags are benchmark-specific helpers; review before removing.
  - Long functions: 30 · Duplications: 19 · High-coupling items: 20 · Cross-module deps: 48
- **Dead code:** 235 flagged (127 high-confidence) — ⚠️ totals are inclusive (count reverse-edge = 0 in the extracted symbol graph); many are public APIs, CLI entrypoints, `__main__` guards, or JSX-only UI refs. **Review only the high-confidence subset** before removing anything.
- **Package manifest:** generated (`requirements.txt`)

See `refined/README.md` for the full item table and `refined/manifest.json` for the machine-readable extraction manifest.
