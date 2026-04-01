# Story 2.3: Withdrawal Command

Status: review

## Story

As a CLI operator,
I want to withdraw funds from an existing account,
so that I can process a customer disbursement.

## Acceptance Criteria

1. `uv run bank withdraw 001 200.0` on account `001` with balance `500.0` → prints `"Withdrawal successful."` and balance is now `300.0` in `accounts.json`.
2. `withdraw 001 800.0` on account `001` with balance `300.0` → fails with a message that includes both the attempted amount (`800.00`) and the current balance (`300.00`). Balance is unchanged.
3. `withdraw 999 100.0` on an unknown account → fails with an account-not-found error message.
4. `withdraw 001 0.0` → fails with a message stating the amount must be greater than 0. Balance is unchanged.
5. `ruff check src/` and `mypy --strict src/` pass.

## Tasks / Subtasks

- [x] Task 1: Implement `BankServiceImpl.withdraw()` in `src/bank/service.py` (AC: 1, 2, 3, 4)
  - [x] Validate `amount > 0` → raise `InvalidAmountError`
  - [x] Fetch account → raise `AccountNotFoundError` if `None`
  - [x] Check `amount <= account.balance` → raise `InsufficientBalanceError` with both amounts in message
  - [x] Compute updated account: `account.model_copy(update={"balance": account.balance - amount})`
  - [x] Call `self._repository.save(updated)` and return `updated`
  - [x] Remove `# noqa: F401` from `InsufficientBalanceError` import (last remaining one)

- [x] Task 2: Implement `withdraw` command body in `src/bank/cli.py` (AC: 1, 2, 3, 4)
  - [x] Wrap service call in try/except following the established error-handling pattern
  - [x] On success: `typer.echo("Withdrawal successful.")`
  - [x] On `BankError`: `typer.echo(str(exc))` and `raise typer.Exit(1)`

- [x] Task 3: Run quality gates (AC: 5)
  - [x] `ruff check src/` → exit code 0
  - [x] `mypy --strict src/` → exit code 0

## Dev Notes

### Implementation — `src/bank/service.py`

Replace the `withdraw` stub with:

```python
def withdraw(self, account_number: str, amount: float) -> Account:
    if amount <= 0:
        raise InvalidAmountError(
            f"Invalid amount: withdrawal amount must be greater than 0, got {amount:.2f}."
        )
    account = self._repository.find_by_id(account_number)
    if account is None:
        raise AccountNotFoundError(
            f"Account not found: no account with number {account_number}."
        )
    if amount > account.balance:
        raise InsufficientBalanceError(
            f"Insufficient balance: cannot withdraw {amount:.2f} from account "
            f"{account_number} (current balance: {account.balance:.2f})."
        )
    updated = account.model_copy(update={"balance": account.balance - amount})
    self._repository.save(updated)
    return updated
```

**AC 2 is strict about message content** — the assertion in test_cli.py (Story 3.3) will check for both `"800.00"` and `"300.00"` in the error output. The format above matches the architecture example exactly:
> `"Insufficient balance: cannot withdraw 800.00 from account 001 (current balance: 300.00)."`

**Guard ordering (three guards, one save):**
1. `amount > 0` — operation input is invalid regardless of account state; no DB read needed
2. `find_by_id` — only look up account after amount is confirmed valid
3. `amount <= balance` — overdraft check; only reached when account exists
4. `save()` — only after all three guards pass; AC 2 and AC 4 require no state change on failure

**`model_copy` for balance update** — same pattern as Story 2.2:
```python
updated = account.model_copy(update={"balance": account.balance - amount})
```
The new balance is `≥ 0` because the overdraft guard ensures `amount ≤ account.balance`. Pydantic's `ge=0.0` constraint on `balance` will not fire.

**Import cleanup — final state after this story:**
```python
from bank.exceptions import (
    AccountNotFoundError,
    DuplicateAccountError,
    InsufficientBalanceError,
    InvalidAmountError,
)
```
All four exceptions are now actively used. Remove all `# noqa: F401` annotations from this import block.

### Implementation — `src/bank/cli.py`

Replace the `withdraw` command body:

```python
@app.command()
def withdraw(account_number: str, amount: float) -> None:
    """Withdraw funds from an account."""
    try:
        _get_service().withdraw(account_number, amount)
        typer.echo("Withdrawal successful.")
    except BankError as exc:
        typer.echo(str(exc))
        raise typer.Exit(1)
```

No `ValidationError` handler — same reasoning as Story 2.2: `amount` is parsed by typer, and the `> 0` guard is service-level.

### Error Message Summary for This Story

| Scenario | Exception | Message |
|----------|-----------|---------|
| amount ≤ 0 | `InvalidAmountError` | `"Invalid amount: withdrawal amount must be greater than 0, got 0.00."` |
| account not found | `AccountNotFoundError` | `"Account not found: no account with number 999."` |
| overdraft | `InsufficientBalanceError` | `"Insufficient balance: cannot withdraw 800.00 from account 001 (current balance: 300.00)."` |

### Architecture Rules

- **Two amounts in `InsufficientBalanceError`** — this is the only exception that includes both the operation value and the account state. The test suite (Story 3.3) will assert on both numeric strings.
- **`model_copy` not direct mutation** — same constraint as Story 2.2; `Account` is an immutable Pydantic model.
- **No state change on any failure path** — `save()` is the last line, only reached after all three guards pass.
- **Service owns all business rule checks** — the repository just does find/save; it never raises domain exceptions.

### Files to Modify

```
src/bank/service.py    ← implement withdraw(), remove all remaining # noqa: F401
src/bank/cli.py        ← implement withdraw() body
```

### Existing Tests to Keep Green

- `tests/test_service.py` — any test asserting `NotImplementedError` for `withdraw` must be updated or removed.
- All Story 2.1 and 2.2 tests must still pass.

### References

- [Source: specs/architecture.md#Exception Hierarchy] — `InsufficientBalanceError`, `AccountNotFoundError`, `InvalidAmountError`
- [Source: specs/architecture.md#Naming & Format Patterns] — Error message format; overdraft example: `"Insufficient balance: cannot withdraw 800.00 from account 001 (current balance: 300.00)."`
- [Source: specs/architecture.md#Data Architecture] — Service owns operational guards; repository returns None
- [Source: specs/epics.md#Story 2.3] — Acceptance criteria (AC 2 explicitly requires both amounts in message)
- [Source: specs/implementation-artifacts/1-5-cli-scaffold-command-discovery.md#Epic 2 Handoff Note] — CLI error-handling pattern

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None.

### Completion Notes List

- Task 1: Implemented `BankServiceImpl.withdraw()` with three guards (amount > 0, account exists, amount <= balance) and `model_copy` for immutable balance update. Removed the last `# noqa: F401` from the `InsufficientBalanceError` import. Fixed line-length ruff violation by splitting the `InvalidAmountError` message across two string literals (matching the deposit pattern already used in the codebase).
- Task 2: Implemented `withdraw` CLI command body in `cli.py` following the established try/except pattern from deposit. Prints "Withdrawal successful." on success, echoes the exception message and exits with code 1 on any `BankError`.
- Task 3: `ruff check src/` and `mypy --strict src/` both exit 0. Full test suite: 88 passed, 0 failed.
- Tests written: 7 service-level tests in `tests/test_service.py` (replaced the `NotImplementedError` stub test with 7 behaviour-driven tests) and 5 CLI tests in `tests/test_withdraw.py`.

### File List

- `src/bank/service.py` — implemented `withdraw()`, removed `# noqa: F401` from `InsufficientBalanceError` import
- `src/bank/cli.py` — implemented `withdraw` command body
- `tests/test_service.py` — replaced `NotImplementedError` stub test with 7 withdraw behaviour tests
- `tests/test_withdraw.py` — new file: 5 CLI integration tests for the withdraw command

## Change Log

- 2026-04-01: Story 2.3 implemented by claude-sonnet-4-6 (Amelia). Implemented `BankServiceImpl.withdraw()` with three-guard pattern (amount, account, balance) and `model_copy` for immutable update. Implemented `withdraw` CLI command with try/except error-handling. Removed last `# noqa: F401` annotation. All 88 tests pass; ruff and mypy --strict exit 0.