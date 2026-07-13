#!/usr/bin/env python3
"""Refine all numbered modules in the page-agent toolchest.

Outputs go to <toolchest>/_refined/<module>/ (OUTSIDE each module) to avoid the
copy_raw_source self-recursion bug. Collects per-module health/dead-code/manifest
into a summary the caller reads back.
"""
from __future__ import annotations
import json
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path.home()))
from refine.pipeline import run_refine

TOOLCHEST = Path.home() / "page-agent-toolchest"
OUT_ROOT = TOOLCHEST / "_refined"
OUT_ROOT.mkdir(parents=True, exist_ok=True)

MODULES = [
    "00-shared",
    "01-llms",
    "02-page-controller",
    "03-core",
    "04-ui",
    "05-page-agent",
    "06-mcp",
    "07-extension",
    "08-website",
]

summary = []
for mod in MODULES:
    src = TOOLCHEST / mod
    out = OUT_ROOT / mod
    # clear any prior run
    if out.exists():
        import shutil
        shutil.rmtree(out)
    rec = {"module": mod, "ok": False}
    try:
        result, analysis = run_refine(src, output_dir=out)
        rec["ok"] = True
        rec["files_created"] = len(result.files_created)
        rec["manifest"] = str(result.manifest_path.relative_to(TOOLCHEST)) if result.manifest_path else None
        if analysis:
            h = analysis.get("health", {})
            rec["health_score"] = h.get("score")
            rec["long_functions"] = len(h.get("long_functions", []))
            rec["duplications"] = len(h.get("duplications", []))
            rec["coupling"] = len(h.get("coupling", []))
            rec["dead_code"] = len(analysis.get("dead_code", []))
            arch = analysis.get("architecture", {})
            stats = arch.get("stats", {}) if isinstance(arch, dict) else {}
            rec["items"] = stats.get("total_items")
            rec["edges"] = stats.get("total_edges")
            rec["cross_module_edges"] = stats.get("cross_module_edges")
        print(f"  ✓ {mod}: score={rec.get('health_score')} items={rec.get('items')} dead={rec.get('dead_code')} files={rec['files_created']}")
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {e}"
        rec["traceback"] = traceback.format_exc()[-400:]
        print(f"  ✗ {mod}: {rec['error']}")

    summary.append(rec)

(OUT_ROOT / "refine-summary.json").write_text(json.dumps(summary, indent=2))
print(f"\nWrote {OUT_ROOT / 'refine-summary.json'}")
