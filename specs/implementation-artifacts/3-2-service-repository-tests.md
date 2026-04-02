# Story 3.2: Service & Repository Tests

Status: review

## Story

As a developer,
I want complete tests for the service and repository layers,
so that business logic and persistence behavior are independently verified.

## Acceptance Criteria

1. `tests/test_repository.py` covers: `find_all()` on a missing file returns `[]`, `save()` + `find_by_id()` round-trip, `exists()` with known and unknown IDs, persistence across two `JsonFileAccountRepository` instances on the same temp file.
2. `tests/test_service.py` covers: `create_account` success, `DuplicateAccountError` on duplicate, `deposit` success and `InvalidAmountError` on zero/negative amount, `withdraw` success and `InsufficientBalanceError` on overdraft, `AccountNotFoundError` for deposit/withdraw on unknown account.
3. All four Java test scenarios (create, deposit, withdraw, overdraft rejection) have direct pytest equivalents.
4. `pytest --cov` reports coverage for `bank/service.py` and `bank/repository.py`.
5. `ruff check src/` and `mypy --strict src/` pass.

## Prerequisite

**Epic 2 must be fully implemented before these tests can pass.** Stories 2.0–2.4 implement the `BankServiceImpl` methods. At authoring time, `service.py` still raises `NotImplementedError` — the tests will fail until Epic 2 is complete.

## Tasks / Subtasks

- [x] Task 1: Replace `tests/test_service.py` with real service tests (AC: 2, 3, 4)
  - [x] Remove all `NotImplementedError` stub tests — they are no longer valid
  - [x] Write `test_create_account_success` — creates account, returns `Account`, persists
  - [x] Write `test_create_account_duplicate_raises` — `DuplicateAccountError`
  - [x] Write `test_create_account_invalid_account_number` — non-numeric triggers `ValidationError` from Pydantic (not `BankError`)
  - [x] Write `test_deposit_success` — balance increases, returns updated `Account`
  - [x] Write `test_deposit_invalid_amount_zero` — `InvalidAmountError`
  - [x] Write `test_deposit_invalid_amount_negative` — `InvalidAmountError`
  - [x] Write `test_deposit_account_not_found` — `AccountNotFoundError`
  - [x] Write `test_withdraw_success` — balance decreases, returns updated `Account`
  - [x] Write `test_withdraw_overdraft_raises` — `InsufficientBalanceError` with message containing amounts
  - [x] Write `test_withdraw_invalid_amount_zero` — `InvalidAmountError`
  - [x] Write `test_withdraw_account_not_found` — `AccountNotFoundError`
  - [x] Confirm 4 Java-scenario equivalents are covered (see Dev Notes)

- [x] Task 2: Update `tests/test_repository.py` to use conftest fixtures (AC: 1, 4)
  - [x] Replace inline `tmp_path / "accounts.json"` with the `json_file` fixture from conftest
  - [x] Use `sample_account` fixture where tests create `Account(account_number="001", owner="Ali", balance=500.0)`
  - [x] Confirm existing 8 tests still pass; add no new repository test if AC coverage is already met

- [x] Task 3: Run quality gates (AC: 4, 5)
  - [x] `uv run pytest` → all tests pass; check coverage for `bank/service.py` and `bank/repository.py`
  - [x] `ruff check src/` → exit code 0
  - [x] `mypy --strict src/` → exit code 0

## Dev Notes

### Critical: `test_service.py` Must Be Completely Replaced

The current `tests/test_service.py` (from Story 1.5) only checks that `BankServiceImpl` raises `NotImplementedError`:

```python
def test_bank_service_impl_create_account_raises() -> None:
    svc = BankServiceImpl(MagicMock())
    with pytest.raises(NotImplementedError):
        svc.create_account("ACC001", "Alice", 100.0)
```

**Delete the entire file content and write real tests.** These stubs are permanently obsolete once Epic 2 is done.

### `test_repository.py` Is Already Comprehensive — Just Add Fixture Usage

The existing `tests/test_repository.py` already covers all AC-1 scenarios with 8 tests:
- `test_find_all_returns_empty_when_file_missing`
- `test_save_and_find_by_id_roundtrip`
- `test_find_by_id_returns_none_for_unknown`
- `test_exists_returns_true_for_known_id`
- `test_exists_returns_false_for_unknown_id`
- `test_persistence_across_instances`
- `test_json_field_names_match_python_attributes`
- `test_save_updates_existing_account`

**Do NOT rewrite these tests.** The goal is to replace inline `tmp_path / "accounts.json"` patterns with the `json_file` fixture and `Account(account_number="001", ...)` constructions with `sample_account` where it reduces duplication, without changing test logic.

### Service Test Infrastructure — Use Real Repository

Inject a real `JsonFileAccountRepository` backed by `json_file` fixture. This gives authentic integration coverage (Pydantic round-trip + persistence) without mocking:

```python
import pytest
from pathlib import Path
from pydantic import ValidationError

from bank.exceptions import (
    AccountNotFoundError,
    DuplicateAccountError,
    InsufficientBalanceError,
    InvalidAmountError,
)
from bank.model import Account
from bank.repository import JsonFileAccountRepository
from bank.service import BankServiceImpl


@pytest.fixture
def svc(json_file: Path) -> BankServiceImpl:
    return BankServiceImpl(JsonFileAccountRepository(json_file))
```

The `json_file` fixture comes from `tests/conftest.py` (Story 3.1). Each test gets a fresh, isolated file in `tmp_path`.

### The Four Java-Equivalent Test Scenarios

The Java BMS had four core test cases. Each must have a direct pytest equivalent in `test_service.py`:

| Java Scenario | pytest test name (suggested) | Exception if failing |
|---|---|---|
| Create account | `test_create_account_java_scenario` | — success only |
| Deposit to account | `test_deposit_java_scenario` | — success only |
| Withdraw from account | `test_withdraw_java_scenario` | — success only |
| Overdraft rejection | `test_withdraw_overdraft_java_scenario` | `InsufficientBalanceError` |

These can be consolidated with the regular success/error tests — just add a docstring comment `# Java scenario equivalent`.

### Error Exception Assertions — Assert on `.message`, Not `str(exc)`

Every domain exception (`BankError` subtype) stores the formatted message in `.message`:

```python
class BankError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
```

Assert on `.message` directly:

```python
with pytest.raises(InsufficientBalanceError) as exc_info:
    svc.withdraw("001", 800.0)
assert "800.00" in exc_info.value.message
assert "300.00" in exc_info.value.message  # current balance
```

The overdraft message format (from architecture): `"Insufficient balance: cannot withdraw 800.00 from account 001 (current balance: 300.00)."`

**Do NOT assert on raw `str(exc_info.value)` or `repr()` — use `.message`.**

### Service Method Return Values

All mutation methods return the updated `Account`. Verify this in success tests:

```python
def test_deposit_success(svc: BankServiceImpl, sample_account: Account) -> None:
    svc.create_account(sample_account.account_number, sample_account.owner, sample_account.balance)
    result = svc.deposit("001", 200.0)
    assert isinstance(result, Account)
    assert result.balance == 700.0  # 500 + 200
```

`get_all_accounts()` returns `list[Account]` — useful for verifying persistence after create/deposit/withdraw.

### Pydantic ValidationError vs. Domain Exceptions

Non-numeric account number in `create_account` propagates a Pydantic `ValidationError` (raised by `Account` model constructor inside the service). It is **not** wrapped in a `BankError`. The CLI catches both separately — tests should reflect this:

```python
from pydantic import ValidationError

def test_create_account_non_numeric_account_number(svc: BankServiceImpl) -> None:
    with pytest.raises(ValidationError):
        svc.create_account("abc", "Ali", 500.0)
```

### Amount Validation Boundary

`InvalidAmountError` is raised for amount ≤ 0 (zero included). Test both boundaries:

```python
def test_deposit_zero_amount_raises(svc: BankServiceImpl, sample_account: Account) -> None:
    svc.create_account(...)
    with pytest.raises(InvalidAmountError):
        svc.deposit("001", 0.0)

def test_deposit_negative_amount_raises(svc: BankServiceImpl, sample_account: Account) -> None:
    svc.create_account(...)
    with pytest.raises(InvalidAmountError):
        svc.deposit("001", -50.0)
```

### Balance Unchanged on Error

After a failed deposit or withdraw, the balance must be unchanged. Verify with `get_all_accounts()` after the exception:

```python
with pytest.raises(InsufficientBalanceError):
    svc.withdraw("001", 800.0)
accounts = svc.get_all_accounts()
assert accounts[0].balance == 500.0  # unchanged
```

### mypy Considerations

- The `svc` fixture returns `BankServiceImpl` (concrete type), not `BankService` (Protocol). This is intentional for test files — tests test the implementation.
- All fixture functions require return type annotations: `def svc(json_file: Path) -> BankServiceImpl:`
- `exc_info.value` is typed as `InsufficientBalanceError` inside a `pytest.raises(InsufficientBalanceError)` block — `.message` access is valid.

### Files to Modify

```
tests/test_service.py     ← COMPLETELY REPLACE with real service tests
tests/test_repository.py  ← update to use json_file + sample_account fixtures
```

No source files (`src/bank/`) are modified in this story.

### Project Structure Notes

- Absolute imports: `from bank.service import BankServiceImpl`, `from bank.exceptions import InvalidAmountError`
- Conftest fixtures (`sample_account`, `json_file`, `populated_repo`) are auto-discovered — no import needed
- Tests should be functions or class methods — either style is fine, but match the existing style in `test_repository.py` (module-level functions)

### References

- [Source: specs/epics.md#Story 3.2] — Acceptance criteria
- [Source: specs/architecture.md#Error Handling Flow] — Pydantic ValidationError vs. BankError separation
- [Source: specs/architecture.md#Naming & Format Patterns] — Error message format: amounts to 2 decimal places
- [Source: specs/architecture.md#Interface Patterns] — `BankService` Protocol method signatures
- [Source: specs/architecture.md#Exception Hierarchy] — `BankError` with `.message` attribute
- [Source: specs/prd.md#FR-2, FR-3] — Java scenario baselines: deposit, withdraw, overdraft
- [Source: src/bank/exceptions.py] — `BankError.__init__` stores message in `.message`
- [Source: specs/implementation-artifacts/3-1-test-foundation-account-model-tests.md] — conftest fixtures (`sample_account`, `json_file`, `populated_repo`)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

_No blockers encountered._

### Completion Notes List

- Task 1: Completely replaced `tests/test_service.py` with 12 real integration tests. Each test injects a real `JsonFileAccountRepository` backed by the `json_file` fixture for authentic Pydantic round-trip coverage. All four Java-equivalent scenarios are covered (`test_create_account_success`, `test_deposit_success`, `test_withdraw_success`, `test_withdraw_overdraft_raises`) with `# Java scenario equivalent` docstring comments. Assertions on domain exceptions use `.message` attribute. Balance-unchanged-on-error verified via `get_all_accounts()` after the exception.
- Task 2: Updated `tests/test_repository.py` to replace all inline `tmp_path / "accounts.json"` patterns with the `json_file` fixture and all inline `Account(account_number="001", ...)` constructions with the `sample_account` fixture. All 8 existing tests still pass; no new tests added (AC-1 coverage was already met).
- Task 3: All 80 tests pass (12 service + 8 repository + 60 others). `bank/service.py` and `bank/repository.py` both at 100% coverage. `ruff check src/` exit 0. `mypy --strict src/` exit 0.

### File List

- `tests/test_service.py` — completely replaced with 12 real integration tests using `json_file` and `sample_account` fixtures
- `tests/test_repository.py` — updated to use `json_file` and `sample_account` conftest fixtures instead of inline `tmp_path` patterns

## Change Log

- 2026-04-02: Story 3.2 implemented — replaced stub-based test_service.py with 12 real service integration tests; updated test_repository.py to use conftest fixtures; all 80 tests pass, 100% coverage on service.py and repository.py, ruff and mypy clean

## Status

review