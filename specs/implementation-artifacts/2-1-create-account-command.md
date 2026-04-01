# Story 2.1: Create Account Command

Status: ready-for-dev

## Story

As a CLI operator,
I want to create a bank account with a validated account number, owner name, and initial balance,
so that I can start managing funds for a new customer.

## Acceptance Criteria

1. `uv run bank create-account 001 Ali 500.0` → prints `"Account created successfully."` and the account is persisted to `accounts.json`.
2. Running `create-account 001 ...` when account `001` already exists → fails with a duplicate account error message (no raw traceback).
3. `create-account abc Ali 500.0` (non-numeric account number) → fails with a message naming the account number format rule.
4. `create-account 001 Ali -100.0` (negative balance) → fails with a message naming the balance ≥ 0 rule.
5. A subsequent `uv run bank show-accounts` lists the created account (persistence verified end-to-end).

## Tasks / Subtasks

- [ ] Task 1: Implement `BankServiceImpl.create_account()` in `src/bank/service.py` (AC: 1, 2, 3, 4)
  - [ ] Check duplicate: if `self._repository.exists(account_number)` → raise `DuplicateAccountError`
  - [ ] Construct `Account(account_number=account_number, owner=owner, balance=initial_balance)` — Pydantic validates at construction time
  - [ ] Call `self._repository.save(account)` then return `account`
  - [ ] Remove `# noqa: F401` from `DuplicateAccountError` import (it is now used); keep it on the others

- [ ] Task 2: Implement `create_account` command body in `src/bank/cli.py` (AC: 1, 2, 3, 4)
  - [ ] Wrap service call in try/except following the established error-handling pattern
  - [ ] On success: `typer.echo("Account created successfully.")`
  - [ ] On `ValidationError`: extract and print first error message (strip `"Value error, "` prefix)
  - [ ] On `BankError`: print `str(exc)` and exit 1
  - [ ] Remove `# noqa: F401` from `ValidationError` and `BankError` imports (both are now used)

- [ ] Task 3: Run quality gates (AC: implicitly required by NFR-1 and NFR-2)
  - [ ] `ruff check src/` → exit code 0
  - [ ] `mypy --strict src/` → exit code 0

## Dev Notes

### Implementation — `src/bank/service.py`

Replace the `create_account` stub with:

```python
def create_account(
    self, account_number: str, owner: str, initial_balance: float
) -> Account:
    if self._repository.exists(account_number):
        raise DuplicateAccountError(
            f"Duplicate account: account number {account_number} already exists."
        )
    account = Account(
        account_number=account_number,
        owner=owner,
        balance=initial_balance,
    )
    self._repository.save(account)
    return account
```

**Why this order matters:**
1. Duplicate check runs **before** `Account(...)` construction. This raises `DuplicateAccountError` (a `BankError`) rather than `ValidationError`, ensuring the CLI catches it in the right handler.
2. `Account(...)` construction triggers Pydantic validation for AC 3 and AC 4 — no manual `if` guards anywhere.
3. `save()` only runs after both guards pass.

**Import cleanup:** After this task, `DuplicateAccountError` is actively used. Update the import block:
```python
from bank.exceptions import (
    AccountNotFoundError,  # noqa: F401  (used in Stories 2.2–2.3)
    DuplicateAccountError,
    InsufficientBalanceError,  # noqa: F401  (used in Story 2.3)
    InvalidAmountError,  # noqa: F401  (used in Stories 2.2–2.3)
)
```

### Implementation — `src/bank/cli.py`

Replace the `create_account` command body (currently empty):

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

Both `ValidationError` and `BankError` imports are now active — remove `# noqa: F401` from both.

### Pydantic Error Message Behaviour (AC 3 & 4)

Understanding what messages the user sees is critical for test assertions:

| Input | Validator | Raw Pydantic msg | After `removeprefix("Value error, ")` |
|-------|-----------|------------------|-----------------------------------------|
| `account_number="abc"` | `@field_validator` raises `ValueError("Account number must be a numeric string (e.g., '001').")` | `"Value error, Account number must be a numeric string (e.g., '001')."` | `"Account number must be a numeric string (e.g., '001')."` |
| `balance=-100.0` | `Field(ge=0.0)` built-in | `"Input should be greater than or equal to 0"` | `"Input should be greater than or equal to 0"` (no prefix to strip) |
| `owner=""` | `Field(min_length=1)` built-in | `"String should have at least 1 character"` | `"String should have at least 1 character"` |

The `removeprefix` is a no-op on Pydantic field constraint messages (they don't have the prefix). This is correct and intentional.

### Architecture Rules

- **`Account(...)` is the validation boundary** — no `if` guards for field-level checks in service code. The two-tier strategy is:
  - Tier 1 (structural invariants): `Account` model rejects invalid `account_number`, `owner`, `balance` via Pydantic
  - Tier 2 (operational guards): `BankServiceImpl` detects duplicate accounts via repository check
- **CLI is the only error-message author** — `DuplicateAccountError` message is authored in service (the exception string), formatted by CLI as `str(exc)`.
- **`save()` upserts**: `JsonFileAccountRepository.save()` will update an existing record if `account_number` matches. The duplicate guard in the service prevents creating two accounts with the same number — do not rely on the repository for this.
- **Absolute imports only**: `from bank.exceptions import DuplicateAccountError` — no relative imports.

### Files to Modify

```
src/bank/service.py    ← implement create_account(), update # noqa comments
src/bank/cli.py        ← implement create_account() body, remove # noqa F401 from used imports
```

No new source files. No test files in this story (tests are Epic 3).

### Existing Tests to Keep Green

Story 1.5 created:
- `tests/test_service.py` — 7 tests covering `BankServiceImpl` stubs (all `NotImplementedError`). After this story, `create_account` will no longer raise `NotImplementedError` — **any test asserting `NotImplementedError` for `create_account` must be updated or removed**.
- `tests/test_cli_scaffold.py` — 9 tests for CLI composition root and help output. Should remain unaffected.

Run `pytest` before and after to identify which tests need updating.

### References

- [Source: specs/architecture.md#Data Architecture] — Two-tier validation strategy
- [Source: specs/architecture.md#Exception Hierarchy] — `DuplicateAccountError` maps to duplicate detection
- [Source: specs/architecture.md#Error Handling Flow] — CLI catches `ValidationError` and `BankError`
- [Source: specs/architecture.md#Naming & Format Patterns] — Error message format: `"{What failed}: {context}."`
- [Source: specs/architecture.md#Anti-Patterns] — No `raise AccountNotFoundError` in repository; no manual `if` guards for Pydantic fields
- [Source: specs/epics.md#Story 2.1] — Acceptance criteria
- [Source: specs/implementation-artifacts/1-5-cli-scaffold-command-discovery.md#Epic 2 Handoff Note] — CLI error-handling pattern (canonical source)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List