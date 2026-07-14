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

## Runtime gap checklist

File targets:

- `extension/background.js` — remove primary dependency on `http://127.0.0.1:4317`, `/api/chat`, `/api/captures`, and legacy direct-execute flows; expose Pi Everywhere activation/dispatch as the active runtime path.
- `extension/sidepanel.js` — stop treating `/api/providers` and `http://localhost:17321/pi-models` as primary data sources; route agent actions to `/pi-everywhere`/global `agentic-core` or label them unimplemented/fallback.
- `extension/sidepanel.html` — keep visible copy aligned with the actual runtime: Pi Everywhere primary, local server fallback-only or removed.
- `extension/content.js` — keep page interaction/browser context concerns only; remove any old polling or orchestration assumptions if found.

## UX gap checklist

File targets:

- `extension/sidepanel.html` — preserve the guided first-run path, inline terminology, and preview-first export language.
- `extension/sidepanel.js` — replace mock success cards with real results, failure states, provider status, cost/time, confidence, and raw expandable output once runtime wiring exists.
- `extension/sidepanel.css` — keep advanced/fallback controls visually secondary to the main Pi Everywhere workflow.
- `docs/EXTENSION-UI-DATA-MAP.md` — document runtime source for each active surface and keep archived flow separate.

## UX acceptance criteria for future work

- Every empty state explains the state and offers a next action.
- Every destructive or file-writing action has preview/confirmation and ideally undo.
- Every export exposes output paths and lets the user open the exported folder.
- Every local path shows one of: connected, missing, needs refresh, changed on disk, permission lost.
- Advanced features should remain behind Advanced surfaces unless they are required for first-run success.
