# Story 2.0: BankService Protocol & BankServiceImpl Scaffold

Status: done

## Story

As a developer,
I want a `BankService` Protocol and a concrete `BankServiceImpl` stub wired into the CLI,
so that Banking Operations stories (2.1–2.4) have a clearly defined place to add business logic.

## Acceptance Criteria

1. `src/bank/service.py` defines a `BankService` Protocol with method signatures for `create_account`, `deposit`, `withdraw`, and `get_all_accounts`.
2. `BankServiceImpl` is a concrete class that satisfies `BankService` **without inheriting from it**.
3. Each `BankServiceImpl` method raises `NotImplementedError` at this stage (full implementations in Stories 2.1–2.4).
4. `BankServiceImpl.__init__` accepts an `AccountRepository` parameter and stores it as `self._repository`.
5. `src/bank/cli.py` wires `BankServiceImpl(JsonFileAccountRepository())` as the service instance via `_get_service()`.
6. `ruff check src/` and `mypy --strict src/` both exit with code 0.

## Tasks / Subtasks

> **Context: This story's implementation is already complete.** Story 1.5 delivered the full scaffold (see Dev Notes). The dev agent's job is verification only: confirm ACs pass against existing code, run quality gates.

- [x] Task 1: Verify `src/bank/service.py` against ACs 1–4
  - [x] `BankService` Protocol defines all four method signatures with correct types
  - [x] `BankServiceImpl` does **not** inherit from `BankService`
  - [x] All four methods raise `NotImplementedError`
  - [x] `__init__(self, repository: AccountRepository) -> None` is present

- [x] Task 2: Verify `src/bank/cli.py` against AC 5
  - [x] `_get_service()` returns `BankServiceImpl(JsonFileAccountRepository())`
  - [x] The function is the composition root (only place concrete implementations are wired)

- [x] Task 3: Run quality gates (AC 6)
  - [x] `ruff check src/` → exit code 0
  - [x] `mypy --strict src/` → exit code 0

## Dev Notes

### Critical Context: Already Implemented

All six ACs were delivered as part of Story 1.5 (`feat(1-5-cli-scaffold-command-discovery)` commit). The two files are in their final state for this story:

**`src/bank/service.py`** (current state — do not modify):
```python
from typing import Protocol

from bank.exceptions import (  # noqa: F401
    AccountNotFoundError,
    DuplicateAccountError,
    InsufficientBalanceError,
    InvalidAmountError,
)
from bank.model import Account
from bank.repository import AccountRepository


class BankService(Protocol):
    def create_account(
        self, account_number: str, owner: str, initial_balance: float
    ) -> Account: ...

    def deposit(self, account_number: str, amount: float) -> Account: ...

    def withdraw(self, account_number: str, amount: float) -> Account: ...

    def get_all_accounts(self) -> list[Account]: ...


class BankServiceImpl:
    def __init__(self, repository: AccountRepository) -> None:
        self._repository = repository

    def create_account(
        self, account_number: str, owner: str, initial_balance: float
    ) -> Account:
        raise NotImplementedError

    def deposit(self, account_number: str, amount: float) -> Account:
        raise NotImplementedError

    def withdraw(self, account_number: str, amount: float) -> Account:
        raise NotImplementedError

    def get_all_accounts(self) -> list[Account]:
        raise NotImplementedError
```

**`src/bank/cli.py`** (current state — do not modify):
```python
import typer
from pydantic import ValidationError  # noqa: F401

from bank.exceptions import BankError  # noqa: F401
from bank.repository import JsonFileAccountRepository
from bank.service import BankServiceImpl

app = typer.Typer()


def _get_service() -> BankServiceImpl:
    return BankServiceImpl(JsonFileAccountRepository())


@app.command()
def create_account(account_number: str, owner: str, initial_balance: float) -> None:
    """Create a new bank account."""


@app.command()
def deposit(account_number: str, amount: float) -> None:
    """Deposit funds into an account."""


@app.command()
def withdraw(account_number: str, amount: float) -> None:
    """Withdraw funds from an account."""


@app.command()
def show_accounts() -> None:
    """Display all accounts."""
```

### Architecture Constraints to Enforce

- `BankServiceImpl` satisfies `BankService` **structurally** (duck typing) — no `class BankServiceImpl(BankService)`.
- `cli.py` is the **only** file that imports both `BankServiceImpl` and `JsonFileAccountRepository`. Service layer imports only protocols.
- The exception imports in `service.py` use `# noqa: F401` because they are intentionally imported for Epic 2 — **do not remove them**.
- Same for `ValidationError` and `BankError` in `cli.py`.

### Protocol Signatures (must not change)

```python
class BankService(Protocol):
    def create_account(self, account_number: str, owner: str, initial_balance: float) -> Account: ...
    def deposit(self, account_number: str, amount: float) -> Account: ...
    def withdraw(self, account_number: str, amount: float) -> Account: ...
    def get_all_accounts(self) -> list[Account]: ...
```

These exact signatures are what Stories 2.1–2.4 will implement. Renaming or reordering parameters will break Epic 2.

### Epic 2 Handoff Pattern

Stories 2.1–2.4 will replace `raise NotImplementedError` in each method. The CLI command bodies follow this exact pattern (already documented in Story 1.5):
```python
@app.command()
def create_account(account_number: str, owner: str, initial_balance: float) -> None:
    """Create a new bank account."""
    try:
        _get_service().create_account(account_number, owner, initial_balance)
        typer.echo("Account created successfully.")
    except ValidationError as exc:
        msg = exc.errors()[0]["msg"].removeprefix("Value error, ")
        typer.echo(msg)
        raise typer.Exit(1)
    except BankError as exc:
        typer.echo(str(exc))
        raise typer.Exit(1)
```

### Project Structure Notes

- Files involved: `src/bank/service.py`, `src/bank/cli.py` — both already complete.
- No new test files for this story. CLI integration tests are in Epic 3 (Story 3.3). Service tests added by Stories 2.1–2.4.
- The existing `tests/test_service.py` and `tests/test_cli_scaffold.py` (from Story 1.5) cover the scaffold behavior.

### References

- [Source: specs/architecture.md#Interface Patterns] — `BankService` Protocol exact signatures
- [Source: specs/architecture.md#Module Structure] — `service.py` placement and role
- [Source: specs/architecture.md#Boundary 1] — CLI → Service composition root rule
- [Source: specs/architecture.md#Anti-Patterns] — No relative imports, no Protocol inheritance
- [Source: specs/epics.md#Story 2.0] — Acceptance criteria
- [Source: specs/implementation-artifacts/1-5-cli-scaffold-command-discovery.md#Dev Notes] — Existing implementation delivered here

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

_No issues encountered. Implementation was already complete from Story 1.5._

### Completion Notes List

- Verified `src/bank/service.py`: `BankService` Protocol has all four method signatures with correct return types and parameter names. `BankServiceImpl` does not inherit from `BankService` (structural duck typing). All four methods raise `NotImplementedError`. `__init__` accepts `AccountRepository` and stores it as `self._repository`.
- Verified `src/bank/cli.py`: `_get_service()` correctly wires `BankServiceImpl(JsonFileAccountRepository())` and is the sole composition root.
- Quality gates: `ruff check src/` → exit 0 (All checks passed!), `mypy --strict src/` → exit 0 (no issues in 6 source files), `pytest` → 70 passed, 100% coverage.

### File List

- src/bank/service.py (verified, no changes)
- src/bank/cli.py (verified, no changes)

## Change Log

| Date | Change |
|------|--------|
| 2026-04-01 | Verification-only story: confirmed all 6 ACs satisfied by Story 1.5 deliverable; quality gates (ruff, mypy --strict, pytest 70/70) all pass; story status set to review |