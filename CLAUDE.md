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

Implementation is driven by the `/story-pipeline` skill (`.claude/skills/story-pipeline/`). The pipeline is fully autonomous — it runs without user interaction unless a story exceeds 3 dev/QA iterations or hits an unrecoverable error.

> **Note:** Skill design is an emerging technique to enhance agent behavior. Quality documentation can be retrieved from [Anthropic](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#open-source-skills) and [cc.bruniaux.com/guide](https://cc.bruniaux.com/guide/ultimate-guide/05-skills/#53-skill-template).

### Invocation

| Command | Behavior |
|---------|----------|
| `/story-pipeline` | Auto-discovers the next `ready-for-dev` story |
| `/story-pipeline path/to/story.md` | Runs a single specific story |
| `/story-pipeline epic-N` | Chains all ready stories of that epic in order |

### Per-story loop

1. **Dev** — `bmad-dev-story` (Amelia): implements the story; story reaches `review` status
2. **QA** — `bmad-agent-qa` (Quinn) in pipeline mode: runs `ruff --fix`, `mypy --strict`, `pytest`, and verifies each AC; auto-fixes what it can
3. **Outcome check**: `clean` (all tests pass, all ACs met, zero ruff violations) → advance; `needs-rework` → loop back to step 1
4. After 3 failed iterations → escalate: extend / skip / halt

### Escalation

The pipeline only interrupts when:
- A story exhausts all 3 iterations without reaching clean status
- An unrecoverable error occurs (missing story file, broken test environment, conflicting ACs)
- The full pipeline completes

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