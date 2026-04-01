# Story 2.1: Create Account Command

Status: review

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

- [x] Task 1: Implement `BankServiceImpl.create_account()` in `src/bank/service.py` (AC: 1, 2, 3, 4)
  - [x] Check duplicate: if `self._repository.exists(account_number)` → raise `DuplicateAccountError`
  - [x] Construct `Account(account_number=account_number, owner=owner, balance=initial_balance)` — Pydantic validates at construction time
  - [x] Call `self._repository.save(account)` then return `account`
  - [x] Remove `# noqa: F401` from `DuplicateAccountError` import (it is now used); keep it on the others

- [x] Task 2: Implement `create_account` command body in `src/bank/cli.py` (AC: 1, 2, 3, 4)
  - [x] Wrap service call in try/except following the established error-handling pattern
  - [x] On success: `typer.echo("Account created successfully.")`
  - [x] On `ValidationError`: extract and print first error message (strip `"Value error, "` prefix)
  - [x] On `BankError`: print `str(exc)` and exit 1
  - [x] Remove `# noqa: F401` from `ValidationError` and `BankError` imports (both are now used)

- [x] Task 3: Run quality gates (AC: implicitly required by NFR-1 and NFR-2)
  - [x] `ruff check src/` → exit code 0
  - [x] `mypy --strict src/` → exit code 0

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

**QA Review — 2026-04-01 (needs-rework)**

- **AC4 FAIL — Negative balance CLI invocation rejected by Typer parser before reaching Pydantic:**
  Running `uv run bank create-account 001 Ali -100.0` causes Typer (v0.24.1) to interpret `-100.0` as a short option flag (`-1` with value `00.0`), producing the Typer built-in error `"No such option: -1"` and exit code 2. The Pydantic validation for `balance ≥ 0` is never reached. The underlying validation logic is correct (verified by running with `-- -100.0` separator, which produces the expected `"Input should be greater than or equal to 0"` message). Fix required: annotate `initial_balance` as `typer.Argument(...)` with `allow_dash` or restructure the argument to prevent Typer from treating negative numeric literals as flags. One common approach is to use `typer.Argument(parser=float)` or declare the type annotation as `Annotated[float, typer.Argument()]`.

- **AC5 FAIL — `show-accounts` command body is empty (stub), produces no output:**
  Running `uv run bank show-accounts` exits silently with code 0 and no output. The story's AC5 states "a subsequent `uv run bank show-accounts` lists the created account (persistence verified end-to-end)". The `show_accounts` function in `src/bank/cli.py` has no body. `BankServiceImpl.get_all_accounts()` also raises `NotImplementedError`. Story 2.4 is designated to implement the listing command, but AC5 is written as an acceptance criterion of this story (2.1). Either: (a) implement a minimal `show-accounts` body here using `get_all_accounts()` (if `get_all_accounts` is also in-scope), or (b) coordinate with story ordering and defer AC5 to Story 2.4 via a `bmad-correct-course` correction.

### Completion Notes List

- Task 1 (service.py): Implemented `BankServiceImpl.create_account()` following the two-tier validation strategy. Duplicate check runs before `Account(...)` construction, raising `DuplicateAccountError` (a `BankError`). Pydantic handles field-level validation (non-numeric account_number → `ValidationError`, negative balance → `ValidationError`). Updated import block: `DuplicateAccountError` is active; `AccountNotFoundError`, `InsufficientBalanceError`, `InvalidAmountError` keep `# noqa: F401` comments for future stories. Updated `test_service.py`: replaced the `NotImplementedError` test with 4 new tests covering success path, duplicate detection, invalid account number, and negative balance.
- Task 2 (cli.py): Implemented `create_account` command body with try/except pattern. `ValidationError` → extracts first error message, strips `"Value error, "` prefix, echoes, exits 1. `BankError` → echoes `str(exc)`, exits 1. Removed `# noqa: F401` from both `ValidationError` and `BankError` imports.
- Task 3 (quality gates): `ruff check src/` → exit 0. `mypy --strict src/` → exit 0. Full test suite: 73 tests passed (no regressions).

### File List

- `src/bank/service.py` — implemented `create_account()`, updated import block `# noqa` comments; implemented `get_all_accounts()` delegating to `repository.find_all()`
- `src/bank/cli.py` — implemented `create_account` command body, removed `# noqa: F401` from active imports; added `Annotated[float, typer.Argument()]` + `context_settings={"allow_interspersed_args": False}` to fix negative-number flag parsing; added `from typing import Annotated` import; implemented `show_accounts` body
- `tests/test_service.py` — replaced `test_bank_service_impl_create_account_raises` (NotImplementedError) with 4 new tests for the implemented behaviour; replaced `test_bank_service_impl_get_all_accounts_raises` with `test_bank_service_impl_get_all_accounts_delegates_to_repository`

### Change Log

- 2026-04-01: Story 2.1 implemented — `BankServiceImpl.create_account()` and `create_account` CLI command body. 4 new service tests added, all 73 tests pass, ruff and mypy --strict clean.
- 2026-04-01: QA rework iteration — fixed AC4 (negative balance flag-parsing) by adding `Annotated[float, typer.Argument()]` annotation and `context_settings={"allow_interspersed_args": False}` to prevent Typer/Click treating `-100.0` as a flag; fixed AC5 by implementing `BankServiceImpl.get_all_accounts()` and `show_accounts` CLI body (ahead-of-schedule from Story 2.4 to satisfy the AC); replaced `NotImplementedError` test for `get_all_accounts` with delegation test. All 73 tests pass, ruff and mypy --strict clean.