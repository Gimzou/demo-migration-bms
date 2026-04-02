d# Story 3.3: CLI Integration Tests & Error Message Assertions

Status: review

## Story

As a developer,
I want CLI-level tests that verify command output and error message content,
so that the user-facing UX is regression-protected.

## Acceptance Criteria

1. `tests/test_cli.py` uses typer's `CliRunner` for all test invocations.
2. Success paths are tested: `create-account` prints `"Account created successfully."`, `deposit` prints `"Deposit successful."`, `withdraw` prints `"Withdrawal successful."`, `show-accounts` prints a formatted table, empty state prints `"No accounts found."`.
3. Error paths assert on message content (not just exit code): duplicate account message, overdraft message containing both amounts, non-numeric account number message, account-not-found message.
4. No test asserts on raw Pydantic `ValidationError` format — all assertions target the reformatted user-facing string.
5. `pytest --cov` reports coverage for `bank/cli.py`.
6. `ruff check src/` and `mypy --strict src/` pass.

## Prerequisite

**Epic 2 must be fully implemented before these tests can pass.** CLI command bodies are currently empty stubs. Tests will fail until Stories 2.1–2.4 are complete.

## Tasks / Subtasks

- [x] Task 1: Create `tests/test_cli.py` with success-path tests (AC: 1, 2, 5)
  - [x] `test_create_account_success` — exit code 0, output contains "Account created successfully."
  - [x] `test_deposit_success` — exit code 0, output contains "Deposit successful."
  - [x] `test_withdraw_success` — exit code 0, output contains "Withdrawal successful."
  - [x] `test_show_accounts_with_data` — exit code 0, output contains Account Number/Owner/Balance headers and correct balance formatted to 2 decimal places
  - [x] `test_show_accounts_empty_state` — exit code 0, output is "No accounts found."
  - [x] Use `monkeypatch.chdir(tmp_path)` in every test for file isolation (see Dev Notes)

- [x] Task 2: Add error-path tests with content assertions (AC: 3, 4)
  - [x] `test_create_account_duplicate_error` — non-zero exit, output contains duplicate indication, NO raw traceback
  - [x] `test_create_account_non_numeric_account_number` — non-zero exit, output contains "numeric", NO "ValidationError" or traceback
  - [x] `test_withdraw_overdraft_error` — non-zero exit, output contains both the attempted amount and the current balance
  - [x] `test_deposit_account_not_found` — non-zero exit, output contains account-not-found indication
  - [x] `test_withdraw_account_not_found` — non-zero exit, output contains account-not-found indication

- [x] Task 3: Run quality gates (AC: 5, 6)
  - [x] `uv run pytest` → all tests pass; check coverage for `bank/cli.py`
  - [x] `ruff check src/` → exit code 0
  - [x] `mypy --strict src/` → exit code 0

## Dev Notes

### `test_cli.py` Does Not Exist Yet — Create It

`tests/test_cli_scaffold.py` exists from Epic 1 (tests CLI is importable and commands are registered). Do NOT touch that file. Create a new `tests/test_cli.py` for integration tests.

### Test Isolation via `monkeypatch.chdir`

The CLI composition root uses `JsonFileAccountRepository()` with the default `Path("accounts.json")` — i.e., in the current working directory. Tests must change the working directory to `tmp_path` so each test gets a fresh, isolated `accounts.json`:

```python
from pathlib import Path
import pytest
from typer.testing import CliRunner
from bank.cli import app

runner = CliRunner()


def test_create_account_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["create-account", "001", "Ali", "500.0"])
    assert result.exit_code == 0
    assert "Account created successfully." in result.output
```

`monkeypatch.chdir` is automatically reverted after each test by pytest. Do NOT use `os.chdir` directly — it would not be reverted on failure.

### CliRunner Setup

```python
from typer.testing import CliRunner
from bank.cli import app

runner = CliRunner()
```

`runner` can be a module-level constant — `CliRunner` is stateless between invocations. Pass CLI arguments as a list of strings exactly as a user would type them:

```python
runner.invoke(app, ["create-account", "001", "Ali", "500.0"])
runner.invoke(app, ["deposit", "001", "200.0"])
runner.invoke(app, ["withdraw", "001", "100.0"])
runner.invoke(app, ["show-accounts"])
```

**Default behaviour of `CliRunner.invoke`:** catches exceptions internally and stores them in `result.exception`. Use `result.exit_code` and `result.output` for assertions. To surface unhandled exceptions in test failures use `catch_exceptions=False` when debugging, but leave it at default (`True`) in committed tests.

### Success Path Assertions

```python
assert result.exit_code == 0
assert "Account created successfully." in result.output  # exact string from architecture
assert "Deposit successful." in result.output
assert "Withdrawal successful." in result.output
assert "No accounts found." in result.output
```

For `show-accounts` with data, assert on column headers and a formatted balance:

```python
def test_show_accounts_with_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["create-account", "001", "Ali", "500.0"])
    result = runner.invoke(app, ["show-accounts"])
    assert result.exit_code == 0
    assert "Account Number" in result.output
    assert "Owner" in result.output
    assert "Balance" in result.output
    assert "500.00" in result.output  # 2 decimal places
```

### Error Path Assertions — Content Over Exit Code

Always assert on `result.output` content, not just `result.exit_code`:

```python
def test_create_account_duplicate_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["create-account", "001", "Ali", "500.0"])
    result = runner.invoke(app, ["create-account", "001", "Bob", "100.0"])
    assert result.exit_code != 0
    assert "001" in result.output          # account number referenced in message
    assert "ValidationError" not in result.output  # no raw traceback
    assert "Traceback" not in result.output

def test_withdraw_overdraft_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["create-account", "001", "Ali", "300.0"])
    result = runner.invoke(app, ["withdraw", "001", "800.0"])
    assert result.exit_code != 0
    assert "800.00" in result.output   # attempted amount
    assert "300.00" in result.output   # current balance

def test_create_account_non_numeric_account_number(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["create-account", "abc", "Ali", "500.0"])
    assert result.exit_code != 0
    assert "numeric" in result.output.lower()
    assert "ValidationError" not in result.output  # reformatted, never raw
    assert "Traceback" not in result.output
```

### How the CLI Formats Errors (Required Understanding)

The CLI (`cli.py`) catches two exception categories at the boundary:

1. **Pydantic `ValidationError`** (from `Account` model constructor):
   - Extract: `e.errors()[0]["msg"]`
   - Strip prefix: remove leading `"Value error, "` if present
   - Print the cleaned message → e.g., `"Account number must be a numeric string (e.g., '001')."`

2. **`BankError` subtypes** (from `BankServiceImpl`):
   - Print: `e.message`
   - e.g., `"Insufficient balance: cannot withdraw 800.00 from account 001 (current balance: 300.00)."`

Tests must assert on the **reformatted output**, never on `"ValidationError"` or `"BankError"` appearing in `result.output`. The AC is that raw tracebacks are never shown — this is the key invariant to regression-protect.

### Exit Code Convention

CLI commands that fail should exit with a non-zero code. `typer` exits with 1 by default when `typer.echo(message); raise typer.Exit(1)` is used, or when the CLI re-raises after printing. Verify this pattern is consistent across all four error tests (`assert result.exit_code != 0`).

### Multi-Step Tests — State Carries Between `runner.invoke` Calls

Within a single test, multiple `runner.invoke` calls share the same `accounts.json` (all in `tmp_path`). This enables end-to-end sequences:

```python
# Create → deposit → show-accounts: verifies persistence and state propagation
monkeypatch.chdir(tmp_path)
runner.invoke(app, ["create-account", "001", "Ali", "500.0"])
runner.invoke(app, ["deposit", "001", "200.0"])
result = runner.invoke(app, ["show-accounts"])
assert "700.00" in result.output
```

### mypy Considerations

- `runner` as a module-level constant is typed as `CliRunner` — fine under `--strict`
- `monkeypatch: pytest.MonkeyPatch` parameter type annotation is required
- `result.output` is `str` — string operations are fully typed
- `tmp_path: Path` is the standard pytest fixture type — no annotation issues

### Files to Create / Modify

```
tests/test_cli.py        ← CREATE (does not exist)
```

No source files (`src/bank/`) are modified. Do NOT touch `tests/test_cli_scaffold.py`.

### Project Structure Notes

- Absolute imports: `from bank.cli import app`
- `runner = CliRunner()` at module level (stateless)
- No import of `conftest` fixtures needed — `tmp_path` and `monkeypatch` are built-in pytest fixtures

### References

- [Source: specs/epics.md#Story 3.3] — Acceptance criteria
- [Source: specs/architecture.md#Naming & Format Patterns] — CLI output strings: "Account created successfully.", "Deposit successful.", "Withdrawal successful.", "No accounts found."
- [Source: specs/architecture.md#Error Handling Flow] — Pydantic ValidationError vs. BankError at CLI boundary; `e.errors()[0]["msg"]` + strip "Value error, " prefix
- [Source: specs/architecture.md#Naming & Format Patterns] — Error message format: amounts to 2 decimal places; overdraft message pattern
- [Source: specs/prd.md#Journey 3] — Error recovery scenarios: overdraft, non-numeric account number, negative deposit
- [Source: src/bank/repository.py] — `DEFAULT_FILE = Path("accounts.json")` in working directory; why `monkeypatch.chdir` is needed
- [Source: specs/implementation-artifacts/3-1-test-foundation-account-model-tests.md] — conftest fixtures available (sample_account, json_file, populated_repo)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

_None — implementation proceeded without blockers._

### Completion Notes List

- Created `tests/test_cli.py` with 10 integration tests using `typer.testing.CliRunner`.
- All 5 success-path tests pass (create-account, deposit, withdraw, show-accounts with data, show-accounts empty state).
- All 5 error-path tests pass asserting on message content: duplicate account, non-numeric account number, overdraft (both amounts), deposit/withdraw account-not-found.
- No test asserts on raw `ValidationError` or `Traceback` text — all assertions target reformatted user-facing strings.
- `bank/cli.py` coverage: 100%. Full suite: 90/90 tests, 100% total coverage.
- `ruff check src/` → 0 violations. `mypy --strict src/` → 0 issues.

### File List

- `tests/test_cli.py` — CREATED: 10 CLI integration tests (success paths + error-message assertions)

## Change Log

- 2026-04-02: Story implemented by claude-sonnet-4-6 (Amelia). Created `tests/test_cli.py` with 10 integration tests covering all success and error paths. All quality gates pass (pytest 90/90, ruff, mypy --strict). Status set to "review".