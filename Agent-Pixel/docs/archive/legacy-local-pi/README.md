# Legacy Local Pi Bootstrap Files

These files are archived from the pre-`/pi-everywhere` implementation.

They used to install or describe a project-local Pi layer:

- `agentic-core/`
- `agentic-enable/`
- `project-local-pi/`
- `agentic-bootstrap-state.md`

They are not the current runtime path. Current Agent-Pixel usage is:

```bash
/pi-everywhere
agentic-core "your task"
```

Use the global `~/.pi` instance as the source of truth for skills, models, memory, and orchestration. Do not copy these archived files back into active paths unless intentionally restoring the legacy project-local architecture.
