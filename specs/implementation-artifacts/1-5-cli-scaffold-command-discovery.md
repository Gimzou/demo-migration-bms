# Story 1.5: CLI Scaffold & Command Discovery

Status: ready-for-dev

## Story

As a CLI operator,
I want all commands discoverable via `--help`,
so that I can learn the available commands and their arguments without reading source code.

## Acceptance Criteria

1. `uv run bank --help` lists all four commands: `create-account`, `deposit`, `withdraw`, `show-accounts`.
2. `uv run bank create-account --help` shows `ACCOUNT_NUMBER`, `OWNER`, `INITIAL_BALANCE` as required arguments.
3. `uv run bank deposit --help` and `uv run bank withdraw --help` show `ACCOUNT_NUMBER` and `AMOUNT` as required arguments.
4. `uv run bank show-accounts --help` confirms the command takes no arguments.
5. `cli.py` wires `BankServiceImpl(JsonFileAccountRepository())` as the composition root.
6. `ruff check src/` exits with code 0.
7. `mypy --strict src/` exits with code 0.

## Tasks / Subtasks

- [ ] Task 1: Add `BankServiceImpl` stub to `src/bank/service.py` (AC: 5)
  - [ ] Keep the `BankService` Protocol from Story 1.1 stub
  - [ ] Add `BankServiceImpl` class with `AccountRepository` constructor injection
  - [ ] All four methods raise `NotImplementedError` (full impl in Epic 2)

- [ ] Task 2: Update `src/bank/cli.py` with proper command signatures (AC: 1–5)
  - [ ] Replace Story 1.1 CLI stub with full scaffold
  - [ ] Register all four commands with correct argument names and types
  - [ ] Add `_get_service()` factory wiring `BankServiceImpl(JsonFileAccountRepository())`
  - [ ] Commands call `_get_service()` — bodies are stubs for now (`pass`)

- [ ] Task 3: Verify help output (AC: 1–4)
  - [ ] `uv run bank --help` → lists all four commands
  - [ ] `uv run bank create-account --help` → shows `ACCOUNT_NUMBER`, `OWNER`, `INITIAL_BALANCE`
  - [ ] `uv run bank deposit --help` → shows `ACCOUNT_NUMBER`, `AMOUNT`
  - [ ] `uv run bank show-accounts --help` → no arguments listed

- [ ] Task 4: Verify quality gates (AC: 6, 7)
  - [ ] `ruff check src/` → exit code 0
  - [ ] `mypy --strict src/` → exit code 0

## Dev Notes

### Implementation

**`src/bank/service.py`** — add `BankServiceImpl` below the existing Protocol:

```python
from typing import Protocol

from bank.exceptions import (
    AccountNotFoundError,
    DuplicateAccountError,
    InsufficientBalanceError,
    InvalidAmountError,
)
from bank.model import Account
from bank.repository import AccountRepository


class BankService(Protocol):
    def create_account(self, account_number: str, owner: str, initial_balance: float) -> Account: ...
    def deposit(self, account_number: str, amount: float) -> Account: ...
    def withdraw(self, account_number: str, amount: float) -> Account: ...
    def get_all_accounts(self) -> list[Account]: ...


class BankServiceImpl:
    def __init__(self, repository: AccountRepository) -> None:
        self._repository = repository

    def create_account(self, account_number: str, owner: str, initial_balance: float) -> Account:
        raise NotImplementedError

    def deposit(self, account_number: str, amount: float) -> Account:
        raise NotImplementedError

    def withdraw(self, account_number: str, amount: float) -> Account:
        raise NotImplementedError

    def get_all_accounts(self) -> list[Account]:
        raise NotImplementedError
```

> The exception imports are needed here for when Epic 2 fills in the implementations. Including them now avoids a mypy/ruff diff churn later. If ruff flags them as unused (F401), add `# noqa: F401` or import inside methods in Epic 2. Prefer importing now and suppressing rather than adding a second PR.

**`src/bank/cli.py`** — full scaffold replacing Story 1.1 stub:

```python
import typer
from pydantic import ValidationError

from bank.exceptions import BankError
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

> `ValidationError` and `BankError` are imported here even though unused in stubs — they will be used in Epic 2 command bodies. If ruff F401 fires, suppress with `# noqa: F401` per import.

### Typer Auto-naming

Typer converts Python function names to CLI command names automatically:

| Python function | CLI command |
|---|---|
| `create_account` | `create-account` |
| `show_accounts` | `show-accounts` |
| `deposit` | `deposit` |
| `withdraw` | `withdraw` |

**No manual `name=` override needed.** Do not rename functions.

### Argument Naming in `--help`

Typer derives argument display names from parameter names:

| Parameter | Displayed as |
|---|---|
| `account_number: str` | `ACCOUNT_NUMBER` |
| `owner: str` | `OWNER` |
| `initial_balance: float` | `INITIAL_BALANCE` |
| `amount: float` | `AMOUNT` |

All are positional and required — no `typer.Option()` wrappers. Typer uses `typer.Argument()` by default for plain parameters.

### mypy --strict Notes

- `raise NotImplementedError` has type `Never` — mypy accepts it as valid body for any return type
- `_get_service()` annotated `-> BankServiceImpl` satisfies mypy even if unused in stubs
- `ValidationError` and `BankError` imports: if flagged as unused, add `# noqa: F401` (ruff) — do NOT remove them, they are needed in Epic 2
- `AccountRepository` in `service.py` is used as a type annotation in `__init__` — mypy counts this as a usage, no `TYPE_CHECKING` guard needed

### Architecture Constraints

- **cli.py is the composition root** — the only file that imports concrete implementations (`JsonFileAccountRepository`, `BankServiceImpl`). Service layer imports only protocols.
- **Service layer never imports CLI** — one-way dependency.
- **Absolute imports only** throughout.
- **No business logic in cli.py** — command bodies are stubs now; Epic 2 adds calls to `_get_service()` methods, but the CLI only formats output and catches exceptions.

### Epic 2 Handoff Note

Epic 2 stories will fill in each command body following this pattern:
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

Dev agents working Epic 2 stories should follow this exact error-handling pattern.

### Project Structure

Files touched in this story:
```
src/bank/service.py    ← add BankServiceImpl stub (keep BankService Protocol)
src/bank/cli.py        ← replace Story 1.1 stub with full scaffold
```

No new test files in this story — CLI integration tests are Epic 3 (Story 3.3).

### Dependencies on Previous Stories

- Story 1.1: project scaffold, uv sync complete
- Story 1.2: `exceptions.py` (imported by service.py)
- Story 1.3: `model.py` — `Account` type used in service signatures
- Story 1.4: `repository.py` — `AccountRepository` Protocol + `JsonFileAccountRepository`

All prior stories must be complete before this one.

### References

- [Source: specs/architecture.md#Module Structure] — `cli.py` is composition root, imports everything
- [Source: specs/architecture.md#Boundary 1] — CLI → Service boundary, one-way
- [Source: specs/architecture.md#Error Handling Flow] — ValidationError and BankError caught at CLI boundary
- [Source: specs/architecture.md#CLI Output Format] — success messages, empty state phrasing
- [Source: specs/epics.md#Story 1.5] — acceptance criteria

## Dev Agent Record

### Agent Model Used

_to be filled by dev agent_

### Debug Log References

### Completion Notes List

### File List