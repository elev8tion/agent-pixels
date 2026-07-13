---
name: agentic-core
description: Sovereign Pi Agentic Layer Master Orchestrator. Single entrypoint for all complex work. Routes to ultraplan, karpathy, fairy-tales chains (feature-ship, bughunt, heal, onboard, research, release, migrate), multi-agent-maestro, subagents, graphify, and all specialized skills. Maintains persistent project memory and knowledge graph. Uses the global ~/.pi everywhere. Activated via pi-everywhere.
---

# Agentic Core

**Master Orchestrator for the sovereign Pi agentic layer.**

This is the single entrypoint. After `/pi-everywhere` and `/agentic-enable`, type `agentic-core "your task"` for any complex work.

## Automatic Routing Logic
- Vague or high-ambiguity task → `/ultraplan` (adversarial multi-lens planning)
- New feature or large change → `feature-ship` chain (spec → build → review → ship)
- Bugs or quality issues → `bughunt` chain (repro → diagnose → fix → verify)
- Code health or structural problems → `heal` chain (scan → plan → fix → verify)
- New project or onboarding → `onboard` chain (map → deepen → digest)
- Research or analysis → `research` chain (gather → synthesize → artifact)
- Release or publishing → `release` chain (changelog → bump → tag → publish → verify)
- Migration or refactoring → `migrate` chain (inventory → transform → verify)
- Anything large → `pi-multi-agent-maestro` with parallel subagents (explore/plan/build/review roles)
- Knowledge or architecture → `graphify` + `/understand`
- All steps use `karpathy` discipline (think → plan → implement → audit → retro)
- Persistent memory via `remember`/`forget`
- Safety enforced by `damage-control-rules.yaml`

## State Management
- Uses `.agentic-bootstrap-state.md` and `.pi/` sidecar
- One `todo` item in_progress at all times
- Updates `MEMORY.md` and topic files after major phases
- Knowledge graph via graphify for zero-token queries

## Project Context
This project (Agent-Pixel) is now part of the sovereign Pi agentic layer. The custom Node polling server is deprecated. All browser automation, visual RAG, and Chrome extension control is orchestrated through agentic-core skills.

**Your full sovereign Pi agentic system is active. Use `agentic-core` as the single command.**

**Handoff**: After any task, run `/handoff` to save state to memory.