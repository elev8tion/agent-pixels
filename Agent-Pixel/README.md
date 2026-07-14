# Agent-Pixel

Custom polling server, project-local Pi glue, and the old web UI are deprecated and archived.

`/pi-everywhere` is the primary entrypoint for this project. Agent-Pixel should use the global `~/.pi` instance directly instead of maintaining a separate project Pi implementation.

Your main `~/.pi` instance has been activated in this project.

You now have full access to all your models, skills, memory, and the complete agentic-core layer.

Simply type `agentic-core "your task"` after `/pi-everywhere` activation to use the full sovereign Pi agentic system.

This project is now permanently connected to your main `.pi` instance.

## Runtime contract

- Active runtime: `/pi-everywhere` activates the global `~/.pi` instance for models, skills, memory, and `agentic-core`.
- Active UI: `Agent-Pixel/extension/` is a guided Chrome extension side panel that should dispatch agent work to the active Pi Everywhere runtime.
- Not active runtime: the local Node server, project-local `.pi/agent/skills/*` copies, local provider/model polling, and the old web UI are removed, legacy, or fallback-only.
- Maintainers should not reintroduce local-server behavior as the default path for new features.

## Legacy paths

These paths are historical or fallback-only and must not be documented as the primary product runtime:

- `Agent-Pixel/archive/` — old local server and web UI implementation.
- `Agent-Pixel/docs/archive/` — archived design, heal, audit, and legacy data-map notes.
- `Agent-Pixel/docs/archive/legacy-local-pi/` — project-local Pi bootstrap/skill copies.
- Legacy endpoint patterns such as `/api/agentic-enable`, `/api/providers`, `/api/chat`, and `http://127.0.0.1:4317`.

## Verification checklist

- Run `/pi-everywhere` from this project and confirm the global `~/.pi` instance is active.
- Run `agentic-core "your task"` after activation to confirm global orchestration is available.
- Check active extension copy and docs identify Pi Everywhere/global `~/.pi` as the runtime source.
- Treat any localhost server/provider/model behavior as legacy fallback until it is removed or explicitly isolated.

## Current docs

- `docs/PI-EVERYWHERE-MIGRATION.md` — current Pi architecture, implementation contract, and deprecated paths.
- `docs/EXTENSION-UI-DATA-MAP.md` — current extension UX map and runtime sources.
- `docs/UX-ROADMAP.md` — implemented UX recommendations and file-targeted gap work.
- `docs/archive/` — legacy server/web UI/heal/audit notes from before the `/pi-everywhere` migration.
