# Bank Management System — Java to Python Migration

This project migrates a [Java Bank Management System](https://github.com/aljalo/BankManagementSystem) to modern Python, using Pydantic for runtime validation. The entire planning and implementation pipeline is driven by AI agents (Claude Code + the BMad method) to explore how far agentic tooling can carry a real codebase migration.

## What's in the repo

- **`/specs`** — All planning artifacts produced by the BMad agents: PRD, architecture decisions, epics, stories, and sprint plans.
- **`/docs/BankManagementSystem`** — A local copy of the original Java source, used as reference input for analysis.
- **`CLAUDE.md`** — Project-level instructions that guide Claude Code throughout the migration.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — the CLI that orchestrates the work
- [BMad Method](https://github.com/bmadcode/BMAD-METHOD) — installed via `npx` ; provides the agent skills used for planning

Optional:
- [`rtk`](https://github.com/contextvibes/rtk) (Rust Token Killer) — a CLI proxy that cuts token usage on dev commands

## Getting started

1. **Claude Code** — create `./CLAUDE.md` and `.claude/CLAUDE.local.md`, enable WebSearch, and set up the `commit-step` hook.
2. **BMad** — output folder is `/specs`. For background on the methodology, see [The Official BMad-Method MasterClass](https://www.youtube.com/watch?v=LorEJPrALcg).
3. **Git** — a `.gitignore` is already in place.

## Migration workflow (BMad agents)

The migration follows three BMad phases, each driven by a dedicated agent persona:

1. **Analysis** (`bmad-agent-analyst`) — Reads the Java source, extracts business rules (minimum balances, ID formats, transactional logic…), and identifies pain points. Produces a Product Requirements Document (`specs/prd.md`).
2. **Architecture** (`bmad-agent-architect`) — Takes the PRD and designs the Python target: package structure, Pydantic models, dependency choices. Outputs `specs/architecture.md` and `specs/epics.md`.
3. **Sprint planning** (`bmad-agent-sm`) — Breaks epics into implementation stories with clear acceptance criteria and a technical focus (e.g. *"US #1: Validate transaction input with Pydantic"*). Outputs individual story files and `specs/sprint.yaml`.