# Story 1.1: Project Scaffold & pyproject.toml Configuration

Status: done

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

- [x] Task 1: Initialize the uv project (AC: 1, 2)
  - [x] Run `uv init --app --package bank --python ">=3.12"` in the project root
  - [x] Remove `src/bank/__main__.py` if created by `uv init` (not in architecture spec)
  - [x] Verify the generated `src/bank/__init__.py` exists

- [x] Task 2: Configure pyproject.toml dependencies (AC: 3, 4, 5)
  - [x] Add runtime deps: `uv add "pydantic>=2.12,<3" "typer>=0.24,<1"`
  - [x] Add dev deps: `uv add --dev "pytest>=9,<10" pytest-cov "ruff>=0.15" "mypy>=1.19"`
  - [x] Verify `[project.scripts]` has `bank = "bank.cli:app"` (may require manual edit)

- [x] Task 3: Add tool configuration to pyproject.toml (AC: 6, 7)
  - [x] Add `[tool.ruff.lint]` with `select = ["E", "F", "W", "I"]`
  - [x] Add `[tool.mypy]` with `strict = true`
  - [x] Add `[tool.pytest.ini_options]` with `testpaths = ["tests"]` and `addopts = "--cov=bank --cov-report=term-missing"`

- [x] Task 4: Create module stubs — all 5 files (AC: 6, 7)
  - [x] `src/bank/exceptions.py` — exception hierarchy stubs
  - [x] `src/bank/model.py` — Account BaseModel stub
  - [x] `src/bank/repository.py` — Protocol stub
  - [x] `src/bank/service.py` — Protocol stub
  - [x] `src/bank/cli.py` — typer app stub (MUST export `app`)

- [x] Task 5: Create tests/ scaffold (AC: 7)
  - [x] `tests/__init__.py` — empty
  - [x] `tests/conftest.py` — empty placeholder (fixtures added in Epic 3)

- [x] Task 6: Verify quality gates (AC: 6, 7)
  - [x] Run `ruff check src/` → exit code 0
  - [x] Run `mypy --strict src/` → exit code 0
  - [x] Run `uv run bank --help` → exit code 0

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

claude-sonnet-4-6

### Debug Log References

- `uv init --app --package bank` created a nested `bank/` subdirectory instead of initializing in-place. Resolved by moving pyproject.toml, .python-version, and src/bank/ to project root, then removing the nested directory.
- `uv_build` was used as build backend (as noted in story Dev Notes). Added `[tool.uv.build-backend]` with `module-name = "bank"` and `source = "src"` to ensure the package is found correctly.
- typer `registered_commands` stores `cmd.name = None` at decoration time; names are derived from callback `__name__` at invocation. Test adapted to derive CLI names via the same `__name__.replace("_", "-")` convention.

### Completion Notes List

- All 6 tasks and 17 subtasks complete.
- 9 tests written covering: exception hierarchy, Pydantic model fields, Protocol class membership, typer app instance, four CLI commands, and Protocol markers for repository/service.
- `uv sync` completes cleanly; `uv run bank --help` lists all four commands.
- `ruff check src/` exits 0; `mypy --strict src/` exits 0 (6 source files).
- Full test suite: 9 passed, 89% coverage.

### File List

- `pyproject.toml` — new: full project config with deps, scripts, tool config
- `.python-version` — new: Python version pin (>=3.12)
- `src/bank/__init__.py` — new: empty package init
- `src/bank/exceptions.py` — new: BankError hierarchy stubs
- `src/bank/model.py` — new: Account Pydantic BaseModel stub
- `src/bank/repository.py` — new: AccountRepository Protocol stub
- `src/bank/service.py` — new: BankService Protocol stub
- `src/bank/cli.py` — new: typer app with 4 command stubs
- `tests/__init__.py` — new: empty test package init
- `tests/conftest.py` — new: empty conftest placeholder
- `tests/test_scaffold.py` — new: 9 tests covering all module stubs and CLI

## Change Log

- 2026-03-30: Story 1.1 implemented — project scaffold complete. Created pyproject.toml with all required deps and tool config, 5 module stubs (exceptions, model, repository, service, cli), tests/ scaffold, and verified all quality gates (ruff, mypy --strict, pytest, uv run bank --help).