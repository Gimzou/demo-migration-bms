# Story 2.2: Deposit Command

Status: ready-for-dev

## Story

As a CLI operator,
I want to deposit funds into an existing account,
so that I can increase the account balance.

## Acceptance Criteria

1. `uv run bank deposit 001 200.0` on account `001` with balance `500.0` → prints `"Deposit successful."` and balance is now `700.0` in `accounts.json`.
2. `deposit 999 100.0` on an unknown account → fails with an account-not-found error message.
3. `deposit 001 0.0` or `deposit 001 -50.0` → fails with a message stating the amount must be greater than 0. Balance is not modified.
4. `ruff check src/` and `mypy --strict src/` pass.

## Tasks / Subtasks

- [ ] Task 1: Implement `BankServiceImpl.deposit()` in `src/bank/service.py` (AC: 1, 2, 3)
  - [ ] Validate `amount > 0` → raise `InvalidAmountError`
  - [ ] Fetch account via `self._repository.find_by_id(account_number)` → raise `AccountNotFoundError` if `None`
  - [ ] Compute updated account using `account.model_copy(update={"balance": account.balance + amount})`
  - [ ] Call `self._repository.save(updated_account)` and return `updated_account`
  - [ ] Remove `# noqa: F401` from `AccountNotFoundError` and `InvalidAmountError` imports

- [ ] Task 2: Implement `deposit` command body in `src/bank/cli.py` (AC: 1, 2, 3)
  - [ ] Wrap service call in try/except following the established error-handling pattern
  - [ ] On success: `typer.echo("Deposit successful.")`
  - [ ] On `BankError`: `typer.echo(str(exc))` and `raise typer.Exit(1)`
  - [ ] No `ValidationError` handler needed — deposit has no Pydantic-validated inputs

- [ ] Task 3: Run quality gates (AC: 4)
  - [ ] `ruff check src/` → exit code 0
  - [ ] `mypy --strict src/` → exit code 0

## Dev Notes

### Implementation — `src/bank/service.py`

Replace the `deposit` stub with:

```python
def deposit(self, account_number: str, amount: float) -> Account:
    if amount <= 0:
        raise InvalidAmountError(
            f"Invalid amount: deposit amount must be greater than 0, got {amount:.2f}."
        )
    account = self._repository.find_by_id(account_number)
    if account is None:
        raise AccountNotFoundError(
            f"Account not found: no account with number {account_number}."
        )
    updated = account.model_copy(update={"balance": account.balance + amount})
    self._repository.save(updated)
    return updated
```

**Critical: how to update balance on a Pydantic model.**
`Account` is a Pydantic `BaseModel`. Direct mutation (`account.balance += amount`) fails at runtime — Pydantic models are immutable by default. Use `model_copy(update={...})` which returns a new instance with the field overridden. The updated balance passes the `ge=0.0` constraint automatically (since both `account.balance ≥ 0` and `amount > 0`).

**Guard ordering matters:**
1. `amount > 0` check first — validates the operation input regardless of account state (AC 3: balance must not be modified on failure).
2. `find_by_id` second — only look up the account after the amount is confirmed valid.
3. `save()` only runs after both guards pass — no partial state changes.

**Import cleanup after this task:**
```python
from bank.exceptions import (
    AccountNotFoundError,             # now used here and will be used in 2.3
    DuplicateAccountError,            # used since 2.1
    InsufficientBalanceError,  # noqa: F401  (used in Story 2.3)
    InvalidAmountError,               # now used here and will be used in 2.3
)
```

### Implementation — `src/bank/cli.py`

Replace the `deposit` command body:

```python
@app.command()
def deposit(account_number: str, amount: float) -> None:
    """Deposit funds into an account."""
    try:
        _get_service().deposit(account_number, amount)
        typer.echo("Deposit successful.")
    except BankError as exc:
        typer.echo(str(exc))
        raise typer.Exit(1)
```

**No `ValidationError` handler here.** `amount` is a `float` typer argument — typer validates it is parseable as float before calling the function. Amount business logic (`> 0`) is a service-level guard, raising `InvalidAmountError` (a `BankError` subtype), caught by the `BankError` handler.

The `ValidationError` import (`from pydantic import ValidationError # noqa: F401`) in `cli.py` was added in Story 1.5 for Epic 2 use. It **is** needed in `create_account` (Story 2.1). Leave it in place — it is already active after Story 2.1.

### Error Message Format

Following `architecture.md` format — `"{What failed}: {context with values}."`:

| Scenario | Exception | Message |
|----------|-----------|---------|
| amount ≤ 0 | `InvalidAmountError` | `"Invalid amount: deposit amount must be greater than 0, got 0.00."` |
| account not found | `AccountNotFoundError` | `"Account not found: no account with number 999."` |

The CLI prints `str(exc)` which resolves to `exc.message` (set in `BankError.__init__`).

### Architecture Rules

- **`amount > 0` is a service-level guard**, not a Pydantic field — it is an operation parameter, not a structural invariant of `Account`. No `Field(gt=0)` anywhere.
- **Repository returns `None` for missing accounts** — the service converts that to `AccountNotFoundError`. Never raise domain exceptions inside `JsonFileAccountRepository`.
- **`model_copy(update={...})`** is the correct Pydantic v2 pattern for creating a modified copy of an immutable model. Do not use `account.balance = ...` (raises `ValidationError` with `model_config` default) or `dict(**account.model_dump(), balance=new_val)` + re-validation (works but verbose).
- **No balance written on failure** — AC 3 requires this. The guard ordering above guarantees it: `save()` is only reached when both checks pass.

### Files to Modify

```
src/bank/service.py    ← implement deposit(), update # noqa comments
src/bank/cli.py        ← implement deposit() body
```

No new source files. No test files in this story (tests are Epic 3).

### Existing Tests to Keep Green

- `tests/test_service.py` — any test asserting `NotImplementedError` for `deposit` must be updated or removed.
- `tests/test_cli_scaffold.py` — help output tests unaffected.
- Story 2.1's new tests for `create_account` must still pass.

Run `pytest` before and after to identify impacted tests.

### References

- [Source: specs/architecture.md#Data Architecture] — Two-tier validation; service owns operational guards
- [Source: specs/architecture.md#Exception Hierarchy] — `InvalidAmountError`, `AccountNotFoundError`
- [Source: specs/architecture.md#Naming & Format Patterns] — Error message format
- [Source: specs/architecture.md#Anti-Patterns] — No domain exceptions in repository
- [Source: specs/epics.md#Story 2.2] — Acceptance criteria
- [Source: specs/implementation-artifacts/1-5-cli-scaffold-command-discovery.md#Epic 2 Handoff Note] — CLI error-handling pattern

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List