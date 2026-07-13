# Refinement Report — page-agent toolchest

> Phase 2 of the forge-pipeline. Ran the native `refine` pipeline (cleansed-native:
> scan → extract → clean → format → analyze → export) on all 9 numbered modules.
> Per-module output in `_refined/<module>/`; per-module health reports appended to
> each module's `README.md`.

## Module Health Scorecard

| # | Module | Items | Health | Long fn | Dup | Coupling | Dead (†) | Syntax |
|---|--------|------:|------:|--------:|----:|---------:|---------:|:------:|
| 00 | shared | 5 | **80** | 1 | 0 | 0 | 5 | ✅ PASS |
| 01 | llms | 25 | **72** | 6 | 1 | 4 | 23 | ✅ PASS |
| 02 | page-controller | 47 | **66** | 24 | 2 | 3 | 46 | ✅ PASS |
| 03 | core | 22 | **70** | 11 | 0 | 7 | 17 | ✅ PASS |
| 04 | ui | 6 | **100** | 0 | 0 | 2 | 5 | ✅ PASS |
| 05 | page-agent | 1 | **100** | 0 | 0 | 0 | 1 | ✅ PASS |
| 06 | mcp | 7 | **70** | 0 | 6 | 2 | 6 | ✅ PASS |
| 07 | extension | 116 | **54** | 19 | 20 | 9 | 112 | ✅ PASS |
| 08 | website | 110 | **58** | 30 | 13 | 15 | 104 | ✅ PASS |

**† Dead code is inflated by per-module scope — see caveat below.**

**All 9 modules pass syntax validation.** Cleaning passes (metadata/lint-directive
stripping, unused-import pruning, relative-ref sanitization) applied to every
extracted block.

---

## How to read these numbers

### Health score (0–100)
Composite of long-function count, MinHash-LSH duplication, and coupling. Leaf
packages with few internal call sites (`04-ui`, `05-page-agent`) score 100; the
large UI packages (`07-extension`, `08-website`) score lower **mostly because
React components are referenced via JSX, not import-graph edges the analyzer
tracks** — this systematically understates real cohesion for React codebases.

### † Dead code is NOT a deletion list
The detector flags items with zero reverse-dependencies **within the module's
own item graph**. This is a monorepo: each package's value is its *public API*
consumed by **other packages**. So `01-llms`'s 23 "dead" items include `LLM`,
`Tool`, `parseLLMConfig`, `zodToOpenAITool`, `modelPatch` — the exact exports
that `03-core` and `07-extension` import. They are live. Read the dead-code
count as a **cross-module consumer inventory**, not dead code.

### The signals that DO matter
- **`02-page-controller` — 24 long functions.** Concentrated in
  `src/dom/dom_tree/index.js` (1745 LOC), a direct port of `browser-use` 0.5.9.
  Long by nature (a DOM walker); the `@edit` markers at the top document
  Alibaba's modifications for upstream-merge purposes.
- **`03-core` — `autoFixer.ts`** (`normalizeResponse` 101 LOC, `validateAction`
  39 LOC). LLM-response repair logic; legitimately complex, candidate for
  splitting if maintained.
- **`01-llms` — `modelPatch` (138 LOC).** Per-provider request-body fixes; grows
  with each new LLM vendor.
- **`06-mcp` — 6 duplication pairs.** Boilerplate across the 3 MCP
  `registerTool` calls — extractable into a helper.
- **`07-extension` / `08-website` — high dup counts.** Framework idiom
  (shadcn/Radix component patterns, animation wrappers), not bugs.

---

## Output layout

```
_refined/
├── REFINEMENT-REPORT.md        ← this file
├── refine-summary.json         ← machine-readable scorecard
├── _run_refine.py              ← the driver (re-runnable)
├── _append_reports.py          ← the README-append driver (re-runnable)
└── <module>/                   ← per-module pipeline output
    ├── README.md               # generated analysis (items table, validation)
    ├── manifest.json           # full item manifest
    ├── package.json            # ⚠ generic stub — real one is in <toolchest>/<module>/package.json
    ├── refinement-report.json  # health + dead-code + architecture
    ├── typescript/             # extracted/cleaned items (one file per function/class)
    └── raw/                    # full verbatim copy of the module's source
```

> **Note on `package.json`:** the pipeline generates a generic
> `{"name":"cleansed-modules"}` stub. The real, dependency-pinned manifests
> (with correct `@page-agent/*` names, `exports`, `publishConfig`) remain in each
> module root (`<toolchest>/<module>/package.json`) — use those for repurposing.

---

## Bug fixed during refinement

The pipeline's `copy_raw_source` step recursively swallowed its own output when
`output_dir` lived inside `source_dir` (`raw/refined/raw/refined/…` 17 levels,
inflating a 13-file module to 643 files). Fixed by writing each module's output
**outside** the module (`_refined/<module>/`), so neither the scanner nor the
raw copier ever encounters prior output.
