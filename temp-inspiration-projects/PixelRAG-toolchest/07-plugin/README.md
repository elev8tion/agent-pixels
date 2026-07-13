# 07-plugin — `pixelbrowse` Claude Code plugin + skills

Gives **Claude Code** (and any agent that runs CLI tools) "eyes" — instead of fetching raw
HTML, it screenshots a page with `pixelshot` (from `01-render`) and reads the image, so it sees
charts, diagrams, tables, and layout the way a person does.

```bash
uv tool install pixelrag                            # pixelshot on PATH
claude plugin marketplace add StarTrail-org/PixelRAG
claude plugin install pixelbrowse@pixelrag-plugins
```

## Files

```
.claude-plugin/plugin.json     ← plugin manifest: name=pixelbrowse, version, author
commands/screenshot.md         ← the /screenshot slash command (usage + prompts)
skills/pixelbrowse/SKILL.md    ← ★ the pixelbrowse skill definition
setup.sh                       ← install script
README.md                      ← install/usage docs
pixelrag.md                    ← a standalone PixelRAG skill doc (from repo skill/)
marketplace/                   ← the .claude-plugin/marketplace.json (plugin marketplace entry)
```

## The `pixelbrowse` skill

`skills/pixelbrowse/SKILL.md` defines the skill (YAML frontmatter: `name: pixelbrowse`,
`allowed-tools: "Bash, Read"`). It instructs the agent to call:

```bash
pixelshot <url> --output /tmp/pixelbrowse --tile-height 1568 --wait-network-idle
```

**Two critical guardrails baked into the skill:**
1. **Always `--tile-height 1568`** for visually-read screenshots — Claude's vision downscales
   images with long edge >1568px (Sonnet/Haiku) or >2576px (Opus); the default 8192px tile
   would get downscaled and text becomes unreadable.
2. **Always `--wait-network-idle`** for URLs — without it, JS-heavy pages capture before
   content loads.

No MCP server, no backend — the skill just shells out to `pixelshot` (Playwright/CDP) on the
local machine.

## Internal dependencies

- **Requires the `pixelshot` CLI** from `01-render` on `PATH`. Recommends `uv tool install
  pixelrag` or `pipx install pixelrag` (a plain `pip install` into a project venv may leave
  `pixelshot` off PATH).

## Repurpose

The whole plugin is a clean, minimal template for a **"tool-backed Claude Code skill"**: a
plugin.json manifest + a SKILL.md that codifies the *correct* way to call a CLI tool (the
`--tile-height 1568` / `--wait-network-idle` guardrails are the real value — they encode
hard-won knowledge about the vision model's limits). Copy this shape to expose any CLI tool to
Claude Code with the right invocation baked in.

## Refinement Report

**Status:** non-code module — 0 AST-extractable items — config/ops/docs module (shell/YAML/JSON/systemd/nginx/markdown)

- Files scanned: 6 (none matched a supported language)
- Imports cleaned: 0
- Metadata stripped: 0
- Syntax validation: N/A (no AST-extractable code)
- Health score: N/A · Dead code: 0
- Package manifest: N/A

See `refined/REFINE_NOTES.md` for the full rationale. The module's value is its documentation/config — preserved verbatim from `_source/`.
