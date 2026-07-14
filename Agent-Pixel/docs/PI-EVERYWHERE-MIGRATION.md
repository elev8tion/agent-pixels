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

## Implementation contract

- Runtime ownership belongs to `/pi-everywhere` plus global `~/.pi`; this repo must not own a separate Pi runtime.
- Agent execution should route through global `agentic-core` after activation.
- Active extension work may provide UX, browser context, capture, previews, and status, but must not make the local server the default orchestrator.
- Localhost endpoints, provider polling, and project-local skill folders are compatibility or archive concerns only.

## File-level mapping

| File/path | Active contract |
| --- | --- |
| `README.md` | Declares Pi Everywhere/global `~/.pi` as active runtime and lists legacy paths. |
| `docs/EXTENSION-UI-DATA-MAP.md` | Separates active extension flow from archived local-server flow. |
| `docs/STRATEGY.md` | Assigns runtime ownership and cleanup priorities. |
| `docs/UX-ROADMAP.md` | Tracks runtime vs UX gaps against concrete extension files. |
| `extension/background.js` | Should remove default local-server orchestration and expose one Pi Everywhere dispatch path. |
| `extension/sidepanel.js` | Should stop primary provider/model polling from localhost and route actions to active runtime. |
| `extension/sidepanel.html` | Should label Pi Everywhere as primary and fallback/legacy controls as non-primary. |
| `extension/content.js` | Should keep browser-page interaction concerns only, without old polling assumptions. |
| `Agent-Pixel/archive/` and `docs/archive/` | Historical reference only; not normative active architecture. |

## Done when

- `/pi-everywhere` is the only documented active entrypoint and global `~/.pi` is the only documented active Pi state store.
- No primary extension action requires `http://127.0.0.1:4317`, `/api/providers`, `/api/chat`, or project-local Pi skills.
- Any remaining local-server behavior is labeled fallback-only, isolated from the main flow, or removed.
- Active docs do not point to archived files as current implementation guidance.
- Verification confirms activation, agent action routing, and UI status without a required local Node server.

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
