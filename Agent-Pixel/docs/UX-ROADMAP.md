# Agent-Pixel UX Roadmap

This document tracks the UX recommendations now reflected in the extension side panel.

## Implemented in the current extension UI

- First-run “Start here” panel.
- Single main workflow: **Create a project from toolchests**.
- Demo entrypoint: **Load demo library**.
- Main tabs reduced to:
  1. Library
  2. Anatomy
  3. Blueprint
  4. Agents
  5. Exports
- Stronger empty states with action buttons.
- Inline terminology hints for Toolchest, Blueprint, Mint, Assay, and Trade Routes.
- Agent Actions panel with common actions:
  - Analyze this toolchest
  - Recommend modules
  - Explain this module
  - Find missing pieces
  - Generate project docs
  - Audit blueprint
- Export Preview panel before final project generation.
- Success-card style feedback in the output panel with “what happened” and next-action summaries.

## Still product/back-end work, not just UI

The current side panel introduces the UX structure and placeholders. These items still need backing implementation:

- Real local folder picker/registration for toolchests.
- Persistent library registry.
- Reachability/freshness checks for local paths.
- Real assay scoring pipeline.
- Real module comparison data.
- Blueprint persistence and conflict detection.
- Export preview generated from actual module selections.
- Final project generation.
- Agent action wiring to `/pi-everywhere`/global `agentic-core` runs with provider status, cost/time, confidence, and raw expandable results.
- Command-center search across module names, README text, contracts, tags, roles, and health scores.
- Saved searches/smart collections.

## UX acceptance criteria for future work

- Every empty state explains the state and offers a next action.
- Every destructive or file-writing action has preview/confirmation and ideally undo.
- Every export exposes output paths and lets the user open the exported folder.
- Every local path shows one of: connected, missing, needs refresh, changed on disk, permission lost.
- Advanced features should remain behind Advanced surfaces unless they are required for first-run success.
