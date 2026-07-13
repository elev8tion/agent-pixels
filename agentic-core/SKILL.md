# Agentic Core

**Purpose**: This is the master orchestrator skill that turns any project into a full Pi-native agentic layer. It is the single entry point for all serious work.

**Trigger phrases**: 
- `agentic-core`
- `use agentic layer`
- `run the full agentic system`
- `orchestrate this project`
- `activate agentic mode`
- `nexus`

## Core Philosophy

This skill does **not** call Claude or external models directly for planning/coding. It routes everything through your Pi agentic stack:

- `ultraplan` or `karpathy` for disciplined planning
- `pi-multi-agent-maestro` for team orchestration
- Specialized skills (`heal`, `design-taste-frontend`, `surface-mine`, `dependency-diplomat`, etc.)
- `pi-subagents` for parallel/forked work
- Persistent memory via `remember`/`forget`
- Safety via damage-control rules

## How It Works

When invoked, `agentic-core` does the following automatically:

1. **Loads project context** using `understand` + docgraph
2. **Activates memory** — pulls relevant facts from persistent memory and the project's own `.pi/memory/`
3. **Chooses optimal workflow** using `loop-composer` (or directly calls `ultraplan` for complex tasks)
4. **Spawns the right subagents** (explore → plan → build → review pattern by default)
5. **Enforces discipline** — every build step goes through karpathy audit or deep-review
6. **Produces artifacts** — always ends with a clean `HEAL-REPORT.md` style summary or designed HTML artifact

## Default Behavior (when no specific task is given)

It will run an **onboard + health check** pass:
- Run `understand` to build live knowledge graph
- Run `heal-scan` to surface any immediate issues
- Generate a project-specific dashboard
- Ask you what you want to build next

## Installation in Any Project

1. Copy this entire `agentic-core` folder into `~/.pi/agent/skills/agentic-core/`
2. Run `/reload_runtime` once
3. In the target project, also install these packages (via `/pi-package-finder`):
   - `pi-multi-agent-maestro`
   - `pi-subagents`
   - `pi-fairy-tales`
   - `ultraplan`
   - `skill-system-creator`
   - `graphify` (for knowledge graphs)

4. (Recommended) Add a `.pi/damage-control-rules.yaml` (I can generate this too).

## Usage Examples

- `agentic-core: redesign the onboarding flow with premium taste`
- `agentic-core: audit dependencies and remove circular imports`
- `agentic-core: build a new feature that does X`
- Just saying `agentic-core` activates the full system on the current project.

This skill is intentionally named `agentic-core` so it does not collide with any official Pi tooling.

**Status**: Production-ready agentic layer bootstrap. All routing stays inside the Pi ecosystem.

---
**Version**: 1.0
**Author**: Generated for sovereign Pi usage
**License**: Use freely in all your projects.
