# Bank Management System — Java to Python Migration

Migrate the [Bank Management System](https://github.com/aljalo/BankManagementSystem) from Java to modern Python, using Pydantic for model validation and business rule enforcement.

## Tech stack

- Python 3.12+ with strong typing (`type` aliases, `TypeVar` defaults, `override`)
- Pydantic for validation, serialization, and runtime type safety
- pytest for unit tests
- `uv` for virtual environment and dependency management

## Planning (BMad method)

All planning artifacts are stored in `/specs`.

The migration is planned through three BMad phases:

1. **Analysis** — `bmad-agent-analyst`
   - Input: Java source code
   - Output: `specs/prd.md`
   - Extract business rules (minimum balance, ID formats, transactional logic) and identify Java pain points to fix in Python

2. **Architecture** — `bmad-agent-architect`
   - Input: `specs/prd.md`
   - Output: `specs/architecture.md`, `specs/epics.md`
   - Design the Python package structure; leverage Pydantic BaseModel for runtime type safety, validation, and serialization

3. **Sprint decomposition** — `bmad-agent-sm`
   - Input: `specs/epics.md`
   - Output: individual story files + `specs/sprint.yaml`
   - Each story has clear acceptance criteria and a technical focus (e.g. "US #1: Validate transaction input with Pydantic")

## Implementation pipeline

Implementation is driven by a `/story-pipeline` skill orchestrated by a BMad master agent. The pipeline chains two sub-agents in a develop-then-review loop. It can run one story at a time or chain all stories of an epic in sequence.

1. **Story-to-Code** — `bmad-agent-dev`
   - Input: a single User Story
   - Output: Python source code + pytest unit tests
   - Produce working code that satisfies all acceptance criteria

2. **Code-to-Review** — `bmad-agent-qa`
   - Input: code from step 1 + the original User Story
   - Output: corrected source code
   - Verify PEP 8 compliance, correct Pydantic usage, adherence to AC — auto-fix any issues found

## Technical objectives

The migration must demonstrate effective adoption of Pydantic as a replacement for Java's manual validation patterns:

- **Pydantic Validators** replace hand-written checks (null guards, range assertions, format validation)
- **Serialization / deserialization** uses `model_dump` / `model_validate` instead of ad-hoc converters
- **Strong typing** throughout, leveraging Python 3.12+ features for maximum static analysis coverage

## BMad configuration

```json
{
  "core": {
    "user_name": "Arnould",
    "communication_language": "English",
    "document_output_language": "English",
    "output_folder": "specs"
  },
  "bmm": {
    "planning_artifacts": "{project-root}/specs",
    "implementation_artifacts": "{project-root}/specs/implementation-artifacts"
  }
}
```

## Handling changes during implementation

If a spec issue is discovered mid-sprint, use `bmad-correct-course` (`[CC]`) — do not edit planning artifacts directly.

- **Small correction** (wrong AC, missing validation rule): CC proposes a targeted story/AC fix
- **Architectural gap**: CC escalates to re-doing just the affected architecture section and derived stories
- **Major pivot** (rare): CC may recommend going back to the PRD — but only as far back as the break actually is

The rule: fix at the lowest level that contains the problem. A wrong AC in Story 2.3 does not reopen the PRD.

## Commands

- Run BMad skill scripts: `uv run <script_path> [args...]`
  - All `.py` scripts under `.claude/skills/` use PEP 723 inline metadata — `uv run` resolves their dependencies automatically.