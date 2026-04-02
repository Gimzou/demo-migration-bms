# Story 3.1: Test Foundation & Account Model Tests

Status: done

## Story

As a developer,
I want shared test fixtures and unit tests for the `Account` model,
so that model validation behavior is provably correct and fixtures are reusable across the suite.

## Acceptance Criteria

1. `tests/conftest.py` provides: a sample valid `Account` fixture, a `tmp_path`-based JSON file path fixture, and a pre-populated `JsonFileAccountRepository` fixture.
2. `tests/test_model.py` covers: valid account creation, rejection of non-numeric account numbers, rejection of empty owner, rejection of negative balance.
3. `account.model_dump()` / `Account.model_validate()` round-trip is tested in `test_model.py`.
4. `pytest --cov` reports coverage for `bank/model.py`.
5. `ruff check src/` and `mypy --strict src/` pass.

## Tasks / Subtasks

- [x] Task 1: Implement shared fixtures in `tests/conftest.py` (AC: 1, 4)
  - [x] Add `sample_account` fixture: returns `Account(account_number="001", owner="Ali", balance=500.0)`
  - [x] Add `json_file` fixture: accepts `tmp_path: Path`, returns `tmp_path / "accounts.json"`
  - [x] Add `populated_repo` fixture: accepts `json_file` + `sample_account`, saves account, returns `JsonFileAccountRepository`

- [x] Task 2: Review `tests/test_model.py` — verify AC coverage (AC: 2, 3)
  - [x] Confirm existing tests cover all AC scenarios (they do — see Dev Notes)
  - [x] Optionally update tests to use the `sample_account` fixture where it avoids duplication
  - [x] Do NOT rewrite from scratch — the file already satisfies all AC requirements

- [x] Task 3: Run quality gates (AC: 4, 5)
  - [x] `uv run pytest` → all tests pass (coverage report is auto-generated via `addopts`)
  - [x] `ruff check src/` → exit code 0
  - [x] `mypy --strict src/` → exit code 0

## Dev Notes

### Critical Context: What Already Exists

**`tests/conftest.py`** — currently a placeholder with only a comment:
```python
# Fixtures will be added in Epic 3
```
This is the primary deliverable for Story 3.1. Write fixtures here.

**`tests/test_model.py`** — already fully written in Story 1.3. It covers every AC scenario for this story:
- `TestAccountValidCreation` — valid creation, zero balance, int→float coercion
- `TestAccountNumberValidation` — non-numeric ("abc"), alphanumeric ("12a"), empty string
- `TestOwnerValidation` — empty owner string
- `TestBalanceValidation` — negative balance (-1.0, -999.99)
- `TestModelDump` — correct keys, correct values, no extra keys
- `TestModelRoundTrip` — round-trip preserves data, equality check

**Do NOT rewrite `test_model.py` from scratch.** Review it and optionally add `sample_account` fixture usage where it reduces duplication (e.g., `TestModelDump` and `TestModelRoundTrip` test classes create the same `Account(account_number="001", owner="Ali", balance=500.0)` inline).

**`tests/test_repository.py`** — also already written. Do NOT touch it in this story.

**`tests/test_service.py`** — contains NotImplementedError stub tests from Story 1.5. Do NOT touch it in this story; it will be completely replaced in Story 3.2.

### Conftest Fixtures to Write

```python
import pytest
from pathlib import Path

from bank.model import Account
from bank.repository import JsonFileAccountRepository


@pytest.fixture
def sample_account() -> Account:
    return Account(account_number="001", owner="Ali", balance=500.0)


@pytest.fixture
def json_file(tmp_path: Path) -> Path:
    return tmp_path / "accounts.json"


@pytest.fixture
def populated_repo(json_file: Path, sample_account: Account) -> JsonFileAccountRepository:
    repo = JsonFileAccountRepository(json_file)
    repo.save(sample_account)
    return repo
```

These fixtures will be consumed by Stories 3.2 (`test_service.py`, `test_repository.py`) and 3.3 (`test_cli.py`). Keep them general.

### Repository Constructor Signature

`JsonFileAccountRepository` accepts an optional `file_path: Path` parameter:
```python
class JsonFileAccountRepository:
    def __init__(self, file_path: Path = DEFAULT_FILE) -> None: ...
```
The `DEFAULT_FILE = Path("accounts.json")` in working directory — tests MUST use `tmp_path`-based paths to avoid writing real files.

### pytest Coverage Configuration

`pyproject.toml` already configures auto-coverage:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=bank --cov-report=term-missing"
```
Running `uv run pytest` automatically generates a coverage report for all `bank/` modules. No extra flags needed.

### mypy Type Annotations for conftest

All fixture functions must have return type annotations. Under `mypy --strict`, untyped fixtures fail the type check gate. Example:
```python
@pytest.fixture
def sample_account() -> Account:   # ← return type required
    ...
```

The `tmp_path: Path` parameter in `json_file` is provided by pytest and typed correctly — no issue with `--strict`.

For `populated_repo`, the return type `JsonFileAccountRepository` is the concrete class (not the Protocol), which is correct — test code interacts with the concrete class.

### Files to Modify

```
tests/conftest.py   ← replace placeholder comment with fixture implementations
tests/test_model.py ← optional: add sample_account fixture usage; verify AC coverage
```

No source files (`src/bank/`) are modified in this story. This is a test-only story.

### Existing Tests Health Check

Before completing, verify these files pass without modification:
- `tests/test_repository.py` — 8 tests, all using `tmp_path` inline
- `tests/test_service.py` — 6 stub tests, all asserting `NotImplementedError` (still valid since Epic 2 not yet implemented)
- `tests/test_scaffold.py`, `tests/test_exceptions.py`, `tests/test_cli_scaffold.py` — scaffold/structural tests from Epic 1

### Project Structure Notes

- Fixtures in `tests/conftest.py` are auto-discovered by pytest — no import needed in test files
- Absolute imports only: `from bank.model import Account`, `from bank.repository import JsonFileAccountRepository`
- `tests/__init__.py` already exists — do not remove it

### References

- [Source: specs/epics.md#Story 3.1] — Acceptance criteria
- [Source: specs/architecture.md#Structure Patterns] — Test organization: `conftest.py` for shared fixtures
- [Source: specs/architecture.md#Interface Patterns] — `AccountRepository` Protocol and `JsonFileAccountRepository`
- [Source: specs/implementation-artifacts/2-4-account-listing-command.md#Dev Notes] — "No test files in this story (tests are Epic 3)"
- [Source: src/bank/repository.py] — `JsonFileAccountRepository.__init__` signature with `file_path: Path` parameter

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None — implementation completed without blockers.

### Completion Notes List

- Task 1: Replaced the placeholder comment in `tests/conftest.py` with three fully-typed pytest fixtures (`sample_account`, `json_file`, `populated_repo`) as specified in Dev Notes. All fixtures follow `mypy --strict` annotation requirements.
- Task 2: Reviewed `tests/test_model.py` — all six AC scenarios already covered by Story 1.3 tests. Updated `TestModelDump` and `TestModelRoundTrip` test methods to consume the `sample_account` fixture, eliminating inline `Account(...)` duplication. `test_round_trip_equality` retains its own `Account` since it uses a different test value.
- Task 3: `uv run pytest` → 88 passed, `bank/model.py` 100% coverage; `ruff check src/` → clean; `mypy --strict src/` → clean.

### File List

- `tests/conftest.py` — replaced placeholder comment with `sample_account`, `json_file`, and `populated_repo` fixtures
- `tests/test_model.py` — updated `TestModelDump` and `TestModelRoundTrip` to use `sample_account` fixture

## Change Log

- 2026-04-02: Story 3.1 implemented (claude-sonnet-4-6). Added shared fixtures to `tests/conftest.py`; refactored `test_model.py` to use `sample_account` fixture. All 88 tests pass; `bank/model.py` 100% covered; ruff and mypy clean.