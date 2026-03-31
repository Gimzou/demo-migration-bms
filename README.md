# Bank Management System — Java to Python Migration

> **Work in progress**

This project migrates a [Java Bank Management System](https://github.com/aljalo/BankManagementSystem) to modern Python, using Pydantic for runtime validation. The entire planning and implementation pipeline is driven by AI agents (Claude Code + the BMad method) to explore how far agentic tooling can carry a real codebase migration.

## Current status

Planning is complete. Implementation of Epic 1 is done; Epics 2 and 3 are in the backlog.

| Epic | Scope | Status |
|------|-------|--------|
| **Epic 1** — Runnable CLI Foundation | Project scaffold, exception hierarchy, account model, repository layer, CLI scaffold | ✅ Done (5 / 5 stories) |
| **Epic 2** — Core Banking Operations | BankService protocol & impl, create/deposit/withdraw/list commands | 🔲 Backlog |
| **Epic 3** — Migration Quality Assurance | Test foundation, service/repo tests, CLI integration tests, NFR gates | 🔲 Backlog |

Story-level detail is tracked in [`specs/implementation-artifacts/sprint-status.yaml`](specs/implementation-artifacts/sprint-status.yaml).

## What's in the repo

```
.
├── .claude/
│   ├── settings.json          # Claude Code permissions and hook configuration
│   ├── hooks/
│   │   └── commit-step.sh     # Auto-commit hook: fires on planning milestones
│   │                          #   and story status transitions (review / done)
│   └── skills/                # BMad agent and custom skill definitions loaded at runtime
├── docs/
│   └── BankManagementSystem/  # Original Java source (reference input for analysis)
├── specs/
│   ├── prd.md                 # Product Requirements Document
│   ├── architecture.md        # Python target architecture & ADRs
│   ├── epics.md               # Epics and user stories
│   └── implementation-artifacts/
│       ├── sprint-status.yaml # Live sprint tracker
│       └── *.md               # Individual story files
├── src/bank/                  # Python source package (Epic 1 output)
├── tests/                     # pytest test suite
├── pyproject.toml             # Project configuration (uv-managed)
└── CLAUDE.md                  # Project-level instructions for Claude Code
```

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — the CLI that orchestrates the work
- [BMad Method](https://github.com/bmadcode/BMAD-METHOD) — installed via `npx`; provides the agent skills used for planning

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

Implementation is then driven by the `/story-pipeline` skill, which chains a dev agent (Amelia) and a QA agent (Quinn) per story, auto-committing on each milestone via the `commit-step` hook.