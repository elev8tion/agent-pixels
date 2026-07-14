# Agent-Pixel Strategy

Agent-Pixel is now a **Pi Everywhere-first guided project-building interface**. The Chrome extension side panel is the active user surface; the old local server and web UI are archived.

## Current source of truth

- Primary Pi layer: global `~/.pi` through `/pi-everywhere`.
- Primary orchestrator after activation: global `agentic-core`.
- Active UI: `Agent-Pixel/extension/`.
- Legacy UI/server: `Agent-Pixel/archive/`.

Do not reintroduce project-local Pi bootstrapping as the default. The repo should not depend on local `.pi/agent/skills/*` copies for normal operation.

## Product direction

Agent-Pixel helps users create projects from reusable module libraries/toolchests with less decision fatigue.

The main workflow is:

1. **Library** — register a toolchest or load a demo library.
2. **Anatomy** — inspect modules and compare reuse quality.
3. **Blueprint** — select modules for the new project.
4. **Agents** — ask `/pi-everywhere` powered actions to analyze, recommend, explain, document, and audit.
5. **Exports** — preview folder tree/conflicts/dependencies, then generate the project.

## UX principles

- First-run users should see a guided tour and a clear “Start here” panel.
- Empty states must explain the current state and include direct action buttons.
- Product terms need inline explanations:
  - Toolchest: folder of extracted reusable modules.
  - Blueprint: selected modules for a new project.
  - Mint: save blueprint as reusable library item.
  - Assay: analyze quality and reuse potential.
  - Trade Routes: find useful connections between toolchests.
- Exports must be preview-first before file generation.
- Agent features should be visible through an “Agent Actions” panel.
- Local folders should show reachability/freshness status.
- Advanced concepts belong behind Advanced surfaces, not in the first-run path.

## Legacy strategy notes

The original project combined browser-agent ideas, visual memory, provider adapters, a local Node server, and a web UI. Those ideas are preserved historically under:

- `Agent-Pixel/archive/`
- `Agent-Pixel/docs/archive/LEGACY-EXTENSION-UI-DATA-MAP.md`
- `Agent-Pixel/docs/archive/LEGACY-HEAL-REPORT.md`
- `Agent-Pixel/docs/archive/LEGACY-KARPATHY-AUDIT.md`

They should be treated as historical implementation notes, not current architecture guidance.
