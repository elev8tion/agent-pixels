# Agent-Pixel — Current Extension UX Map

## Current architecture

Agent-Pixel is now a **Pi Everywhere-first Chrome extension UI**. The old local Node server, web UI, `/agentic-enable` endpoint, and project-local Pi glue are legacy paths preserved under `archive/` only.

Primary runtime expectation:

1. Run `/pi-everywhere` in this project.
2. Use the global `~/.pi` instance for models, skills, memory, and `agentic-core`.
3. Use the extension side panel as a guided project-building surface, not as the owner of a separate Pi implementation.

## Active flow

The active extension UI is in:

- `Agent-Pixel/extension/sidepanel.html`
- `Agent-Pixel/extension/sidepanel.css`
- `Agent-Pixel/extension/sidepanel.js`
- `Agent-Pixel/extension/background.js`
- `Agent-Pixel/extension/content.js`

Main visible tabs and Runtime source:

1. **Library** — register or demo toolchests; runtime source is extension state plus future folder registration, with agent interpretation through `/pi-everywhere`.
2. **Anatomy** — inspect and compare modules; runtime source is collected module data plus global `agentic-core` analysis.
3. **Blueprint** — collect modules for a new project; runtime source is extension blueprint state plus Pi Everywhere recommendations.
4. **Agents** — expose `/pi-everywhere` agent actions; runtime source is the global `~/.pi` instance after activation.
5. **Exports** — preview folder tree/conflicts before project generation; runtime source is selected blueprint data and Pi Everywhere-generated guidance.

Active runtime rule: new primary features must route to `/pi-everywhere`/global `~/.pi` or local extension state. Do not wire new primary features to legacy localhost endpoints.

## Archived flow

The old flow was extension UI → local Node server → provider/model endpoints → old web UI/project-local Pi glue. That path is archived or fallback-only.

Legacy/fallback surfaces include:

- local server connection settings
- `/api/providers`, `/api/chat`, `/api/captures`, and `/api/agentic-enable`
- `http://127.0.0.1:4317` and other localhost model-sync controls
- old web UI behavior in `Agent-Pixel/archive/`

These can be referenced only for migration, compatibility, or removal work; they are not the current runtime source.

## User-facing terms

- **Toolchest** — a folder of extracted reusable modules.
- **Blueprint** — selected modules for a new project.
- **Mint** — save a blueprint as a reusable library item.
- **Assay** — analyze quality and reuse potential.
- **Trade Routes** — find useful connections between toolchests.

## Guided workflow

The extension now presents one obvious main path:

1. Register a toolchest or load the demo library.
2. Inspect modules in Anatomy.
3. Add useful modules to Blueprint.
4. Run agent actions for recommendations, docs, and audit.
5. Preview export before generating a project.

Important UX rules:

- Empty states must explain what to do next and include direct action buttons.
- Agent actions should show clear success summaries and next steps.
- Export should be preview-first: selected modules, generated files, conflicts, missing docs/contracts, and dependencies before final generation.
- Local folder status should be visible: connected, missing, needs refresh, changed on disk, or permission lost.

## Legacy documentation

The previous extension↔server↔web UI data map documented the old local server architecture. It has been archived at:

- `Agent-Pixel/docs/archive/LEGACY-EXTENSION-UI-DATA-MAP.md`

Use it only to understand historical implementation details in `Agent-Pixel/archive/`.
