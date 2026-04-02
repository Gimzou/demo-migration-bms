# Bank Management System — Java → Python

A complete migration of [BankManagementSystem](https://github.com/aljalo/BankManagementSystem) from Java to modern Python, driven end-to-end by AI agents — from requirements analysis to test-covered code. Built with Pydantic for validation and Typer for the CLI.

**3 epics · 13 stories · 90 tests · 100% coverage**

## Quick start

```bash
uv sync
uv run pytest
uv run bank --help
```

## How it was built

The whole project — analysis, architecture, sprint planning, implementation — was orchestrated through the [BMad method](https://github.com/bmadcode/BMAD-METHOD). Each phase is owned by a dedicated agent and produces a concrete artifact:

| Phase | Agent | Artifact |
|-------|-------|----------|
| Analysis | `bmad-agent-analyst` | [`specs/prd.md`](specs/prd.md) |
| Architecture | `bmad-agent-architect` | [`specs/architecture.md`](specs/architecture.md) · [`specs/epics.md`](specs/epics.md) |
| Sprint planning | `bmad-agent-sm` | [Story files](specs/implementation-artifacts/) |
| Implementation | `/story-pipeline` | `src/bank/` · `tests/` |

Planning milestones were auto-committed via a `commit-step` hook — the git log doubles as a project journal through the planning phase.

Implementation ran as an autonomous Dev → QA loop per story: Amelia writes code and tests, Quinn runs ruff, mypy, pytest and checks each acceptance criterion. Story 2-1 needed two iterations — Quinn caught a Typer argument parsing issue that let negative amounts slip past Pydantic validation. Full traces in [`specs/audit/`](specs/audit/).

## Pydantic over manual validation

The Java `Account` validated by hand and left account number format entirely unchecked:

```java
public Account(String accountNumber, String ownerName, double balance) {
    if (balance < 0) {
        throw new IllegalArgumentException("balance cannot be negative");
    }
    // accountNumber format: never checked
}
```

The Python model replaces all of that declaratively:

```python
class Account(BaseModel):
    account_number: str = Field(min_length=1)
    owner: str = Field(min_length=1)
    balance: float = Field(ge=0.0)

    @field_validator("account_number")
    @classmethod
    def account_number_must_be_numeric(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("Account number must be a numeric string (e.g., '001').")
        return v
```

The model is immutable — updates go through `model_copy(update={...})` rather than in-place mutation.

## Project structure

```
.
├── docs/BankManagementSystem/       # Original Java source (reference input)
├── specs/
│   ├── prd.md
│   ├── architecture.md
│   ├── epics.md
│   ├── audit/                       # Pipeline execution traces, one file per epic
│   └── implementation-artifacts/
│       ├── sprint-status.yaml
│       └── *.md                     # Individual story files
├── src/bank/
│   ├── model.py                     # Account — Pydantic BaseModel
│   ├── repository.py                # In-memory AccountRepository
│   ├── service.py                   # BankService protocol + BankServiceImpl
│   ├── exceptions.py                # Domain exception hierarchy
│   └── cli.py                       # Typer CLI
├── tests/
├── .claude/
│   ├── hooks/
│   │   └── commit-step.sh           # Auto-commits planning milestones
│   └── skills/                      # BMad agent and pipeline skill definitions
└── pyproject.toml
```

## CLI

```bash
uv run bank create-account 001 "Alice" 500.0
uv run bank deposit 001 200.0
uv run bank withdraw 001 100.0
uv run bank show-accounts
```