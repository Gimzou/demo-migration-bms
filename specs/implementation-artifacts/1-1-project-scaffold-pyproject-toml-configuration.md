# Story 1.1: Project Scaffold & pyproject.toml Configuration

Status: ready-for-dev

## Story

As a developer,
I want a correctly initialized Python package with all dependencies configured,
so that I can run `uv sync` and have the full dev environment ready without any manual steps.

## Acceptance Criteria

1. `uv sync` completes with no errors on a clean clone.
2. `uv run bank --help` exits with code 0 and lists all four commands.
3. `pyproject.toml` declares runtime deps: `pydantic >=2.12,<3` and `typer >=0.24,<1`.
4. `pyproject.toml` declares dev deps: `pytest >=9,<10`, `pytest-cov`, `ruff >=0.15`, `mypy >=1.19`.
5. `[project.scripts]` contains `bank = "bank.cli:app"`.
6. `ruff check src/` exits with code 0.
7. `mypy --strict src/` exits with code 0.

## Tasks / Subtasks

- [ ] Task 1: Initialize the uv project (AC: 1, 2)
  - [ ] Run `uv init --app --package bank --python ">=3.12"` in the project root
  - [ ] Remove `src/bank/__main__.py` if created by `uv init` (not in architecture spec)
  - [ ] Verify the generated `src/bank/__init__.py` exists

- [ ] Task 2: Configure pyproject.toml dependencies (AC: 3, 4, 5)
  - [ ] Add runtime deps: `uv add "pydantic>=2.12,<3" "typer>=0.24,<1"`
  - [ ] Add dev deps: `uv add --dev "pytest>=9,<10" pytest-cov "ruff>=0.15" "mypy>=1.19"`
  - [ ] Verify `[project.scripts]` has `bank = "bank.cli:app"` (may require manual edit)

- [ ] Task 3: Add tool configuration to pyproject.toml (AC: 6, 7)
  - [ ] Add `[tool.ruff.lint]` with `select = ["E", "F", "W", "I"]`
  - [ ] Add `[tool.mypy]` with `strict = true`
  - [ ] Add `[tool.pytest.ini_options]` with `testpaths = ["tests"]` and `addopts = "--cov=bank --cov-report=term-missing"`

- [ ] Task 4: Create module stubs — all 5 files (AC: 6, 7)
  - [ ] `src/bank/exceptions.py` — exception hierarchy stubs
  - [ ] `src/bank/model.py` — Account BaseModel stub
  - [ ] `src/bank/repository.py` — Protocol stub
  - [ ] `src/bank/service.py` — Protocol stub
  - [ ] `src/bank/cli.py` — typer app stub (MUST export `app`)

- [ ] Task 5: Create tests/ scaffold (AC: 7)
  - [ ] `tests/__init__.py` — empty
  - [ ] `tests/conftest.py` — empty placeholder (fixtures added in Epic 3)

- [ ] Task 6: Verify quality gates (AC: 6, 7)
  - [ ] Run `ruff check src/` → exit code 0
  - [ ] Run `mypy --strict src/` → exit code 0
  - [ ] Run `uv run bank --help` → exit code 0

## Dev Notes

### Critical: Project Root Context

This project root already contains planning artifacts (`specs/`, `docs/`, `.claude/`). Run `uv init` directly in this root — it will add `pyproject.toml`, `src/`, and `tests/` alongside existing dirs. Do NOT create a nested `bank/` subdirectory.

Check for existing `pyproject.toml` before running `uv init`. If one exists, manually craft the pyproject.toml instead of running `uv init`.

### pyproject.toml Target Shape

```toml
[project]
name = "bank"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "pydantic>=2.12,<3",
    "typer>=0.24,<1",
]

[project.scripts]
bank = "bank.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/bank"]

[dependency-groups]
dev = [
    "mypy>=1.19",
    "pytest>=9,<10",
    "pytest-cov",
    "ruff>=0.15",
]

[tool.ruff.lint]
select = ["E", "F", "W", "I"]

[tool.mypy]
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=bank --cov-report=term-missing"
```

> Note: `uv init --app --package` uses `uv_build` as build backend, not `hatchling`. Accept whatever backend uv init chooses — do not override it manually.

### Module Stubs — Minimum to Pass mypy --strict

Each stub must be fully type-annotated. `mypy --strict` rejects unannotated functions.

**`src/bank/exceptions.py`**
```python
class BankError(Exception):
    pass

class AccountNotFoundError(BankError):
    pass

class DuplicateAccountError(BankError):
    pass

class InsufficientBalanceError(BankError):
    pass

class InvalidAmountError(BankError):
    pass
```

**`src/bank/model.py`**
```python
from pydantic import BaseModel

class Account(BaseModel):
    account_number: str
    owner: str
    balance: float
```
(Validators added in Story 1.3 — stub only needs to pass mypy)

**`src/bank/repository.py`**
```python
from typing import Protocol
from bank.model import Account

class AccountRepository(Protocol):
    def find_all(self) -> list[Account]: ...
    def find_by_id(self, account_number: str) -> Account | None: ...
    def save(self, account: Account) -> None: ...
    def exists(self, account_number: str) -> bool: ...
```

**`src/bank/service.py`**
```python
from typing import Protocol
from bank.model import Account

class BankService(Protocol):
    def create_account(self, account_number: str, owner: str, initial_balance: float) -> Account: ...
    def deposit(self, account_number: str, amount: float) -> Account: ...
    def withdraw(self, account_number: str, amount: float) -> Account: ...
    def get_all_accounts(self) -> list[Account]: ...
```

**`src/bank/cli.py`** — CRITICAL: must export `app` for entry point to work
```python
import typer

app = typer.Typer()

@app.command()
def create_account(account_number: str, owner: str, initial_balance: float) -> None:
    """Create a new bank account."""
    pass

@app.command()
def deposit(account_number: str, amount: float) -> None:
    """Deposit funds into an account."""
    pass

@app.command()
def withdraw(account_number: str, amount: float) -> None:
    """Withdraw funds from an account."""
    pass

@app.command()
def show_accounts() -> None:
    """Display all accounts."""
    pass
```
> typer auto-converts `show_accounts` → `show-accounts` and `create_account` → `create-account` in the CLI.

### Architecture Constraints

- **Import style:** Always absolute — `from bank.model import Account`, never `from .model import Account`.
- **No `__main__.py`:** Entry point is via `[project.scripts]`, not `python -m bank`.
- **mypy --strict** requires: type annotations on ALL function signatures, no `Any` without explicit cast, no untyped defs.
- **Protocol classes** do NOT inherit from concrete implementations. `AccountRepository` and `BankService` are Protocols only.

### Project Structure After This Story

```
<project-root>/
├── pyproject.toml          ← new
├── src/
│   └── bank/
│       ├── __init__.py     ← new (may be empty)
│       ├── cli.py          ← new stub
│       ├── exceptions.py   ← new stub
│       ├── model.py        ← new stub
│       ├── repository.py   ← new stub
│       └── service.py      ← new stub
├── tests/
│   ├── __init__.py         ← new
│   └── conftest.py         ← new (empty)
├── specs/                  ← existing, untouched
└── docs/                   ← existing, untouched
```

### References

- [Source: specs/architecture.md#Starter Template Evaluation] — `uv init --app --package bank --python ">=3.12"` is the mandated init command
- [Source: specs/architecture.md#Module Structure] — flat layout in `src/bank/`, exactly 5 modules + `__init__.py`
- [Source: specs/architecture.md#Interface Patterns] — exact Protocol method signatures
- [Source: specs/architecture.md#Enforcement Guidelines] — run `ruff check src/` and `mypy --strict src/` before marking done
- [Source: specs/epics.md#Story 1.1] — acceptance criteria

## Dev Agent Record

### Agent Model Used

_to be filled by dev agent_

### Debug Log References

### Completion Notes List

### File List