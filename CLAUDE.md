# Bank Management System for Python

Migrate the [Bank Management System](https://github.com/aljalo/BankManagementSystem) codebase from Java to a modern Python architecture leveraging Pydantic for model validation.

## Methodology

Apply the Bmad method to plan the migration :

- Agent Analyst (bmad-agent-analyst):
  - Input: Java source code of the Bank Management System library
  - Output: prd.md (Product Requirement Document)
  - Goals: 
    - Extract business rules (i.e. : minimum balance, ID format, transactional logic, ...)
    - Identify the pains of the Java code to correct them in Python
- Agent Architect (bmad-agent-architect):
  - Input: PDR.md
  - Output: architecture.md & epics.md
  - Goals:
    - Define the global structure of the Python codebase
    - Leverage Pydantic BaseModel to guarantee typesafety at runtime
- Agent ScrumMaster (bmad-agent-sm):
  - Input: epics.md
  - Output: List of detailed stories & sprint.yaml
    - Format: Each Story must contain clear acceptance criteria (AC) and a technical focus (i.e.: "US #1: Validate transaction input with Pydantic")

> **Note**: All artifacts from the BMAD methodology (.md files, story backlog) shall be stored in the `/specs` directory

Bmad project initialization answers :

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

## Implementation

- Prefer `uv` for virtual environment management
- Use `pydantic` and `python 3.12+`


## Commands

- Run BMad skill scripts: `uv run <script_path> [args...]`
  - All `.py` scripts under `.claude/skills/` use PEP 723 inline metadata — `uv  
  run` resolves their dependencies automatically.



