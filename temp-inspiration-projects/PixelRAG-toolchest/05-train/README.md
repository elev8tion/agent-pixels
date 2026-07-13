# 05-train — `wiki-screenshot-training` (separate uv project)

**LoRA fine-tuning** of `Qwen/Qwen3-VL-Embedding-2B` for visual webpage retrieval, plus the
**data-curation pipeline** (LLM-augmented query generation, filtering, hard-negative mining)
and **SFT recipes** for Qwen3-VL reader models. This is a **separate `uv` project** with its
own pinned environment — it is NOT installed from the repo root.

```bash
cd 05-train && uv sync      # torch==2.9.1+cu129, transformers==4.57.1, cuDNN 9.20
```

> You don't need to retrain to use the model — trained adapters are published at
> [`Chrisyichuan/wiki-screenshot-embedding-lora`](https://huggingface.co/Chrisyichuan/wiki-screenshot-embedding-lora)
> (`lora_vit/ckpt200` is the best checkpoint).

## Architecture

This is the largest module (137 files). It breaks into **four sub-systems**:

### A. Embedding fine-tune (LoRA on Qwen3-VL-Embedding-2B)
| File | Role |
| ---- | ---- |
| `train_contrastors.py` | **Main contrastive trainer** (ViT LoRA + text warmup + hard negatives) |
| `train.py`, `train_swift.py` | Alt training entrypoints (ms-swift integration) |
| `dataset.py` | Dataset / collator (positive + hard-negative sampling) |
| `model.py`, `models/biqwen3.py` | Model wrappers (BiQwen3-style dual encoder) |
| `evaluate.py`, `eval_checkpoint.py` | Retrieval eval at checkpoints |
| `mine_hard_negatives.py`, `mine_text_hard_negatives.py` | Hard-negative mining |
| `recipes/v8s_ablation.sh` | The v8 reference ablation recipe |

Peak result: **QA score ≈ 0.785** on `miniv8` (400 SimpleQA Qs, 7426 candidate tiles) vs.
~0.715–0.730 for the untrained base. Original W&B run linked in `README.md`.

### B. Data curation pipeline → `train/docs/synthetic_data_pipeline.md`
Generates & filters the training set:
- `generate_query_pairs.py`, `generate_text_query_pairs.py` — LLM-augmented query generation
- `filter_*.py` (v2, hard, passage, entity_queries, strict, self_contained) — multi-stage filtering
- `mine_*`, `run_filter_*_chunks.py` — hard-negative mining at scale
- `prepare_hf_dataset*.py`, `package_hf_image_shards.py`, `extract_hf_image_shards.py` — HF packaging
- `upload_*`, `clean_queries_simpleqa_style.py`, `split_first5_chunks.py`, `validate_images.py`

Released dataset: `Chrisyichuan/screenshot-training-natural-filtered-v2`.

### C. SFT recipes for the Qwen3-VL reader → `sft/`
Supervised fine-tune of Qwen3-VL reader models that *read* the retrieved tiles. ~50 YAML
configs (`train_qwen3vl_{2x,3x,5x,9x,mixed,compressed,top6}_*.yaml`) + data-prep scripts
(`prepare_sft_data_*.py`, `prepare_think_data.py`, `generate_think_traces*.py`) + eval
(`eval_*.sh`, `eval_baseline.py`, `eval_multiimage.py`). `sft/RESULTS.md` has outcomes.

### D. Tests, docs, serving
- `tests/` — grad equivalence, multi-GPU, ms-swift equivalence
- `docs/` — full reproduce recipe (`reproduce_v8r.md`), `natural_filtered_v2.md`,
  `swift_training.md`, `training_report_2026-04-02.md`, `v8_ablation_results.md`
- `serving/vllm/` — vLLM serving config for the embedder
- `CONTRASTORS.md` — contrastive-training design notes

## Internal dependencies

**None at import time.** This is an isolated project. Its *output* — the trained adapter — is
referenced by `04-serve` and `05-train`'s own eval by HF path, not by local code.

## Repurpose

- `train_contrastors.py` + `dataset.py` is a complete contrastive image/text embedding
  fine-tuner (ViT-LoRA + hard negatives + text warmup) adaptable to any vision-language
  embedding backbone.
- The data-curation scripts (`generate_query_pairs.py`, the `filter_*` cascade,
  `mine_hard_negatives.py`) are a reusable synthetic-RAG-data pipeline.
- `sft/`'s YAML recipe collection is a reference for Qwen3-VL SFT hyperparameter sweeps.

## Refinement Report

Ran the native cleansed pipeline (scan → clean → validate → analyze → package). Cleaned source, manifest, and full analysis live in `refined/`.

- **Items extracted:** 352  (python: 352)
- **Source files scanned:** 137
- **Syntax validation:** 347 valid / 5 invalid
  - ⚠️ 5 invalid — all `SyntaxError: unexpected indent (line 2)`: class attributes/properties/methods extracted *out of class context*, so the standalone fragment has a stray indent. **The source is valid**; only the extracted fragment is malformed. No action needed on `_source/`.
- **Imports cleaned:** 6312 lines of cleaned output from 18070 raw lines (0 cleansed annotations; 0 relative-import TODOs flagged for manual resolution)
- **Health score:** 49/100 — Moderate — large research/training codebase with many standalone scripts (query-gen, filter cascade, hard-neg mining) that share boilerplate. High dead-code count is mostly __main__ guards, CLI entrypoints, and script-level helpers that are entry points, not dead — review high-confidence subset only.
  - Long functions: 30 · Duplications: 20 · High-coupling items: 20 · Cross-module deps: 15
- **Dead code:** 335 flagged (240 high-confidence) — ⚠️ totals are inclusive (count reverse-edge = 0 in the extracted symbol graph); many are public APIs, CLI entrypoints, `__main__` guards, or JSX-only UI refs. **Review only the high-confidence subset** before removing anything.
- **Package manifest:** generated (`requirements.txt`)

See `refined/README.md` for the full item table and `refined/manifest.json` for the machine-readable extraction manifest.
