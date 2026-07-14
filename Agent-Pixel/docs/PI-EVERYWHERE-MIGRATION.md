# Pi Everywhere Migration Notes

## Decision

Agent-Pixel uses `/pi-everywhere` as the project entrypoint. The global `~/.pi` instance provides models, skills, memory, `agentic-core`, safety behavior, and orchestration.

## Why

The previous project-local Pi implementation duplicated skills and bootstrap files inside the repo. That made the project harder to reason about and risked drift from the real Pi setup.

`/pi-everywhere` keeps one canonical Pi installation:

- `~/.pi/agent/models.json`
- `~/.pi/agent/skills/`
- `~/.pi/agent/memory/`
- global `agentic-core`

## Current expected usage

From this project:

```bash
/pi-everywhere
agentic-core "your task"
```

The extension UI should describe itself as Pi Everywhere powered. Any local server/model-sync controls are legacy fallback only.

## Deprecated paths

These are not primary runtime paths anymore:

- `/agentic-enable`
- project-local `.pi/agent/skills/agentic-core/`
- project-local `.pi/agent/skills/visual-rag/`
- local `/api/agentic-enable` server bootstrap
- old archived web UI as the main product surface

## Keep vs remove guidance

Keep:

- `.pi-everywhere`
- `Agent-Pixel/.pi-everywhere`
- active extension UI updates referencing `/pi-everywhere`

Archived for historical inspection:

- `Agent-Pixel/docs/archive/legacy-local-pi/agentic-core/`
- `Agent-Pixel/docs/archive/legacy-local-pi/agentic-enable/`
- `Agent-Pixel/docs/archive/legacy-local-pi/project-local-pi/`
- `Agent-Pixel/docs/archive/legacy-local-pi/agentic-bootstrap-state.md`

These archived files should not be referenced by active docs as the current path.
