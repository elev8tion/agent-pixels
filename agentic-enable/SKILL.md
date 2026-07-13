---
name: agentic-enable
description: >
  One-command bootstrapper that installs the full Pi agentic layer into any project.
  Run `/agentic-enable` in any folder and it will create the complete agentic-core
  system (orchestrator, subagent support, memory, safety rules, chains, and
  project onboarding). This is the skill you copy into every new project when you
  want the same powerful agentic layer you have here. Uses only Pi-native tools
  and skills — no Claude involved.
---

# Agentic Enable

**One-command installer for the full Pi agentic layer.**

Chain version: 1

This is an **orchestrator-style** skill — it runs all bootstrap phases in one session
and leaves the project with a working `agentic-core` master skill.

**Trigger**: `/agentic-enable`, `install agentic layer`, `enable agentic mode in this project`, or any request to "add the agentic layer to this project".

## What It Does

When you run `/agentic-enable` in any project, it will:

1. Create `.pi/agent/skills/agentic-core/` and install the master orchestrator
2. Install the core agentic packages (`pi-multi-agent-maestro`, `pi-subagents`, `pi-fairy-tales`, `ultraplan`, `skill-system-creator`, `graphify`)
3. Install safety rules (`.pi/damage-control-rules.yaml`)
4. Run `understand` + `onboard` to build live knowledge graph and project memory
5. Create a project-specific welcome note so future sessions know this is an agentic project
6. Verify everything and print clear next steps

After this runs once, you only ever need to type `agentic-core` (or `use agentic layer`) in that project to activate the full system.

## Workflow

### Step 1 — Check Current Project

- Confirm we are in a real project directory (has `package.json`, `Cargo.toml`, `pyproject.toml`, `README.md`, etc.)
- Check if `.pi/` already exists. If it does, ask whether to upgrade or skip existing files.
- Create `.agentic-bootstrap-state.md` to track progress (atomic write).

### Step 2 — Scaffold the Agentic Core

Create the following files (using precise content from the templates):

- `.pi/agent/skills/agentic-core/SKILL.md` — the master orchestrator (the one previously generated)
- `.pi/damage-control-rules.yaml` — safety rules optimized for agentic work
- `.pi/prompt-templates/agentic-onboard.md` — project-specific onboarding template

### Step 3 — Install Required Packages

Use the `pi-package-finder` skill (or direct installation commands) to ensure these are available:

- `pi-multi-agent-maestro`
- `pi-subagents`
- `pi-fairy-tales`
- `ultraplan`
- `skill-system-creator`
- `graphify`

### Step 4 — Prime the Project

- Run `/understand` to build the knowledge graph
- Run `/onboard` to generate project-specific onboarding guide
- Run `/remember` to store key facts about this project being agentic-enabled

### Step 5 — Verify & Handoff

Run a final check that `agentic-core` is now available and print:

> Agentic layer successfully installed.
> Type `agentic-core` (or `/agentic-core`) to use the full system in this project.

Update state file to `status: complete` and delete any temporary lock.

## Handoff

After completing, output exactly:

> Agentic layer successfully installed in this project.
> Type `agentic-core` to activate the full Pi agentic system.
> You now only need one slash command in any project to have the complete agentic layer.

Do not continue. Stop here.
