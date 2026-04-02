# Story 3.4: NFR Gates — Linting, Typing & Coverage

Status: done

## Story

As a developer,
I want all quality gates to pass on the complete codebase,
so that the migration is measurably complete and the codebase is maintainable.

## Acceptance Criteria

1. `ruff check src/` exits with code 0 and zero violations (NFR-1).
2. `mypy --strict src/` exits with code 0 and zero errors (NFR-2).
3. `pytest --cov` reports line coverage ≥ 90% (NFR-3).
4. No `if` guards for model-level input validation exist outside Pydantic model definitions in `src/bank/` (NFR-4) — see Dev Notes for exact scope.
5. A clean clone running `uv sync` then `uv run bank --help` succeeds with exit code 0 (NFR-6).
6. All four commands (`create-account`, `deposit`, `withdraw`, `show-accounts`) and their `--help` variants exit with code 0.

## Prerequisite

**All of Epic 2 (Stories 2.0–2.4) and Epic 3 Stories 3.1–3.3 must be complete before this story can succeed.** This story does not implement new features — it verifies and fixes quality gate failures across the complete, implemented codebase.

## Tasks / Subtasks

- [x] Task 1: Run ruff and fix all violations (AC: 1)
  - [x] `uv run ruff check src/` — collect all violations
  - [x] `uv run ruff check src/ --fix` — auto-fix what ruff can (import order, whitespace, etc.)
  - [x] Manually fix remaining violations (F-string issues, unused imports, etc.)
  - [x] Re-run until exit code 0

- [x] Task 2: Run mypy and fix all type errors (AC: 2)
  - [x] `uv run mypy --strict src/` — collect all errors
  - [x] Fix missing return type annotations
  - [x] Fix `Any` type usage (add explicit types)
  - [x] Fix Protocol structural typing issues if any
  - [x] Re-run until exit code 0

- [x] Task 3: Run pytest and verify ≥ 90% coverage (AC: 3)
  - [x] `uv run pytest` — check coverage report in terminal (auto-generated via `addopts`)
  - [x] Identify modules below 90% (`bank/cli.py`, `bank/service.py`, `bank/repository.py`, `bank/model.py`, `bank/exceptions.py`)
  - [x] Add targeted tests in the appropriate Epic 3 test files if any module is under-covered
  - [x] Re-run until overall line coverage ≥ 90%

- [x] Task 4: Verify NFR-4 — no manual validation guards in application code (AC: 4)
  - [x] Grep `src/bank/service.py` for `if` statements — confirm they are operational guards (`amount <= 0`, duplicate detection, overdraft), NOT structural validators for `Account` fields
  - [x] Grep `src/bank/cli.py` — confirm no validation logic; only error catching and message formatting
  - [x] Confirm `src/bank/model.py` uses `Field` constraints and `@field_validator` for all structural invariants

- [x] Task 5: Verify NFR-6 — zero-setup experience (AC: 5, 6)
  - [x] `uv sync` → exit code 0
  - [x] `uv run bank --help` → exit code 0, lists all four commands
  - [x] `uv run bank create-account --help` → exit code 0
  - [x] `uv run bank deposit --help` → exit code 0
  - [x] `uv run bank withdraw --help` → exit code 0
  - [x] `uv run bank show-accounts --help` → exit code 0

## Dev Notes

### This Story Is a Verification + Fix Story

No new source files or features. Work through gates in order: ruff → mypy → pytest → NFR-4 check → NFR-6 smoke test. Each gate may expose issues requiring small fixes in `src/bank/` or `tests/`.

### Ruff Configuration

`pyproject.toml` configures ruff with:
```toml
[tool.ruff.lint]
select = ["E", "F", "W", "I"]
```
- `E` — pycodestyle errors (line length, indentation, whitespace)
- `F` — pyflakes (unused imports `F401`, undefined names `F821`, etc.)
- `W` — pycodestyle warnings
- `I` — isort (import ordering)

**Common violations to expect:**
- `F401` unused import — e.g., `from bank.exceptions import ...  # noqa: F401` already exists in `cli.py` for forward-reference imports; verify these are still needed
- `I001` import order — `ruff --fix` handles automatically
- `E501` line too long — reformat long lines

Run `uv run ruff check src/ --fix` first to auto-fix mechanical issues, then address remaining manually.

### mypy Configuration

```toml
[tool.mypy]
strict = true
```

`--strict` enables: `--disallow-untyped-defs`, `--disallow-incomplete-defs`, `--check-untyped-defs`, `--disallow-any-generics`, `--warn-return-any`, `--no-implicit-reexport`, and more.

**Common strict-mode issues to expect:**

1. **Missing return type on functions**: Every function must have a return type annotation including `-> None`.

2. **Protocol structural compatibility**: `JsonFileAccountRepository` satisfies `AccountRepository` Protocol without inheriting. mypy validates this structurally — if a method signature doesn't match exactly (e.g., wrong parameter type), it fails. The Protocol is:
   ```python
   class AccountRepository(Protocol):
       def find_all(self) -> list[Account]: ...
       def find_by_id(self, account_number: str) -> Account | None: ...
       def save(self, account: Account) -> None: ...
       def exists(self, account_number: str) -> bool: ...
   ```
   `JsonFileAccountRepository` must match each signature exactly.

3. **`typer` parameter types**: typer infers CLI argument types from Python type annotations. Under `--strict`, ensure all typer command functions have full annotations (`account_number: str`, `amount: float`, `-> None`).

4. **`json.load()` return type**: Returns `Any`. Annotate explicitly: `data: list[dict[str, object]] = json.load(f)` (already done in `repository.py` — verify it's still there).

5. **`e.errors()[0]`**: Pydantic's `.errors()` returns `list[ErrorDetails]`. Accessing `["msg"]` is fine as `ErrorDetails` is a `TypedDict`.

### pytest Coverage — Auto-Reported

`pyproject.toml` already sets:
```toml
[tool.pytest.ini_options]
addopts = "--cov=bank --cov-report=term-missing"
```

Running `uv run pytest` automatically produces a per-module coverage report. Look for the `TOTAL` line: must be ≥ 90%.

**Modules most likely to be under-covered:**
- `bank/exceptions.py` — only 5 exception classes; covered by any test that imports them
- `bank/cli.py` — needs CLI integration tests (Story 3.3) to reach coverage
- `bank/service.py` — needs service tests (Story 3.2)

If a specific module is below 90%, check `--cov-report=term-missing` output for which lines are uncovered, then add targeted tests in the relevant `test_*.py` file.

### NFR-4 Scope — Operational Guards Are Acceptable

NFR-4 states: "every business rule expressed as Pydantic `Field` constraint or `@field_validator`." The architecture made one explicit correction: **`amount > 0` is an operational guard in the service layer, not a Pydantic model field constraint** — because `amount` is an operation parameter, not an `Account` field.

**What NFR-4 requires (must be in `model.py`):**
- `balance ≥ 0` → `Field(ge=0.0)` on `Account.balance` ✓
- Account number must be numeric → `@field_validator("account_number")` ✓
- Owner must be non-empty → `Field(min_length=1)` on `Account.owner` ✓

**What is acceptable in `service.py` (operational guards):**
- `if amount <= 0: raise InvalidAmountError(...)` — correct service-layer pattern
- `if self._repository.exists(account_number): raise DuplicateAccountError(...)` — correct
- `if account.balance < amount: raise InsufficientBalanceError(...)` — correct

**NFR-4 violation to look for and fix:**
- Any `if balance < 0:` or `if not owner:` guard in `service.py` or `cli.py` — these duplicate Pydantic and must be removed

### NFR-6 Smoke Test — No Accounts.json Side Effects

Run `uv run bank --help` from the project root, not from a temp directory. It must exit 0. If `accounts.json` gets created by `--help`, that is a bug in the CLI composition root — `_get_service()` should not instantiate the repository on `--help` (typer handles `--help` before calling the command body).

### Coverage Gap — `bank/exceptions.py`

`exceptions.py` has 5 classes, each just `pass` or `__init__`. It will likely show 100% coverage since any test that raises a `BankError` subtype covers those lines. No action needed unless coverage report shows otherwise.

### Files That May Need Small Fixes

```
src/bank/cli.py         ← likely mypy annotation fixes; verify noqa comments still valid
src/bank/service.py     ← verify method return types; amount guard pattern
src/bank/repository.py  ← json.load annotation; open mode strings
src/bank/model.py       ← unlikely to need changes (already typed)
src/bank/exceptions.py  ← unlikely to need changes
tests/                  ← may need additional tests if coverage < 90%
```

Do NOT add features or refactor logic. Only fix gate failures (type errors, lint violations, missing test coverage).

### Expected Final State

```
$ uv run ruff check src/
(no output)
$ echo $?
0

$ uv run mypy --strict src/
Success: no issues found in 5 source files
$ echo $?
0

$ uv run pytest
...
TOTAL    ...   ≥ 90%
... passed

$ uv run bank --help
Usage: bank [OPTIONS] COMMAND [ARGS]...
...
  create-account  ...
  deposit         ...
  withdraw        ...
  show-accounts   ...
$ echo $?
0
```

### References

- [Source: specs/prd.md#NFR-1 through NFR-6] — Gate definitions and measurement criteria
- [Source: specs/architecture.md#Gap Analysis Results] — "amount > 0 moved to service layer" — NFR-4 scope clarification
- [Source: specs/architecture.md#Enforcement Guidelines] — "All AI Agents MUST: Run ruff check src/ and mypy --strict src/ before considering a story complete"
- [Source: specs/architecture.md#Implementation Patterns] — Anti-patterns: relative imports, alias serialization, repository raising exceptions
- [Source: pyproject.toml] — ruff selects E/F/W/I; mypy strict; pytest addopts with --cov
- [Source: src/bank/repository.py] — `data: list[dict[str, object]] = json.load(f)` annotation pattern

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None — all gates passed without issues on first run.

### Completion Notes List

- Task 1 (ruff): `uv run ruff check src/` reported zero violations immediately. No fixes were required. Exit code 0.
- Task 2 (mypy): `uv run mypy --strict src/` reported "Success: no issues found in 6 source files". No annotation fixes needed. Exit code 0.
- Task 3 (pytest + coverage): 90 tests passed, 100% line coverage across all 6 source modules (cli.py, exceptions.py, model.py, repository.py, service.py, __init__.py). No additional tests needed.
- Task 4 (NFR-4): Verified that `service.py` contains only operational guards (amount <= 0, exists check, overdraft check) — no structural validators duplicating Pydantic. `cli.py` contains only error-catching and formatting, no validation logic. `model.py` uses `Field(ge=0.0)`, `Field(min_length=1)`, and `@field_validator("account_number")` for all structural invariants.
- Task 5 (NFR-6): `uv sync` exits 0. `uv run bank --help` exits 0 and lists all four commands (create-account, deposit, withdraw, show-accounts). All four `--help` subcommands exit 0.

### File List

No source files were modified. All quality gates passed on the pre-existing implementation without requiring any code changes.

- specs/implementation-artifacts/sprint-status.yaml (modified: status updated to in-progress, then to review)
- specs/implementation-artifacts/3-4-nfr-gates-linting-typing-coverage.md (modified: task checkboxes, Dev Agent Record, File List, Change Log, Status)

## Change Log

- 2026-04-02: All NFR gates verified and passed. ruff: 0 violations. mypy --strict: 0 errors. pytest: 90 passed, 100% coverage. NFR-4: no duplicate validation guards found. NFR-6: all CLI commands and --help variants exit 0. Story set to "review".