# Story 1.3: Account Model

Status: done

## Story

As a developer,
I want an `Account` Pydantic `BaseModel` with enforced field constraints,
so that no invalid `Account` instance can be created anywhere in the system.

## Acceptance Criteria

1. Valid inputs (numeric account number, non-empty owner, balance ≥ 0) produce a successful `Account` instance.
2. Non-numeric account number (e.g., `"abc"`) raises `ValidationError` with a message referencing the account number format rule.
3. Empty owner string raises `ValidationError` for the owner field.
4. Balance < 0 raises `ValidationError` for the balance field.
5. `account.model_dump()` returns `{"account_number": ..., "owner": ..., "balance": ...}` — no aliases, no extra keys.
6. `Account.model_validate(account.model_dump())` round-trips without data loss.
7. `ruff check src/` exits with code 0.
8. `mypy --strict src/` exits with code 0.

## Tasks / Subtasks

- [x] Task 1: Implement `Account` model in `src/bank/model.py` (AC: 1–6)
  - [x] Replace the Story 1.1 stub with full Pydantic model
  - [x] Add `Field` constraints for `owner` (non-empty) and `balance` (≥ 0)
  - [x] Add `@field_validator` for `account_number` (numeric string check)
  - [x] Confirm no aliases set (`by_alias` never used)

- [x] Task 2: Write unit tests in `tests/test_model.py` (AC: 1–6)
  - [x] Test: valid account created successfully
  - [x] Test: non-numeric account number raises `ValidationError`
  - [x] Test: empty owner raises `ValidationError`
  - [x] Test: negative balance raises `ValidationError`
  - [x] Test: `model_dump()` output shape (keys, no aliases)
  - [x] Test: `model_validate(model_dump())` round-trip

- [x] Task 3: Verify quality gates (AC: 7, 8)
  - [x] `ruff check src/` → exit code 0
  - [x] `mypy --strict src/` → exit code 0

## Dev Notes

### Implementation

`src/bank/model.py` — full file:

```python
from pydantic import BaseModel, Field, field_validator


class Account(BaseModel):
    account_number: str = Field(min_length=1)
    owner: str = Field(min_length=1)
    balance: float = Field(ge=0.0)

    @field_validator("account_number")
    @classmethod
    def account_number_must_be_numeric(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("Account number must be a numeric string (e.g., '001').")
        return v
```

**Key design decisions:**

| Field | Constraint mechanism | Rule |
|---|---|---|
| `account_number` | `Field(min_length=1)` + `@field_validator` | non-empty AND all digits |
| `owner` | `Field(min_length=1)` | non-empty string |
| `balance` | `Field(ge=0.0)` | ≥ 0 at construction time |

**Why `Field(min_length=1)` on `account_number` too?** The `@field_validator` runs after field-level validation. An empty string would fail `isdigit()` but the error message would be wrong. `min_length=1` catches the empty case with a clear Pydantic message before the validator runs.

### Pydantic v2 Validator Syntax

Use `@field_validator` (Pydantic v2), NOT the deprecated v1 `@validator`:

```python
# ✅ Pydantic v2 — correct
@field_validator("account_number")
@classmethod
def account_number_must_be_numeric(cls, v: str) -> str: ...

# ❌ Pydantic v1 — do not use
@validator("account_number")
def account_number_must_be_numeric(cls, v): ...
```

`@classmethod` decorator is **required** in Pydantic v2 on all `@field_validator` methods. mypy --strict will error without it.

### Serialization Contract

```python
account = Account(account_number="001", owner="Ali", balance=500.0)

account.model_dump()
# → {"account_number": "001", "owner": "Ali", "balance": 500.0}

Account.model_validate({"account_number": "001", "owner": "Ali", "balance": 500.0})
# → Account(account_number='001', owner='Ali', balance=500.0)
```

**Never use:**
- `model_dump(by_alias=True)` — there are no aliases; this would break repository JSON format
- `model_dump(mode="json")` — not needed; default Python dict is what the repository uses

### CLI Error Message Handling

When `ValidationError` is raised, the CLI layer (Story 1.5) will reformat it. The validator's `ValueError` message becomes the user-facing text after Pydantic strips the `"Value error, "` prefix:

```
Pydantic raises: "Value error, Account number must be a numeric string (e.g., '001')."
CLI strips prefix → shows user: "Account number must be a numeric string (e.g., '001')."
```

Write validator messages accordingly — they will be shown verbatim to users.

### mypy --strict Notes

- `@field_validator` with `@classmethod` satisfies mypy strict
- `Field(ge=0.0)` — use `0.0` not `0` to match `float` type annotation
- `balance: float` — Pydantic will coerce `int` inputs at runtime, but type annotation stays `float`

### Architecture Constraints

- **No manual `if` guards** — all validation via Pydantic Field/validator (NFR-4 hard gate)
- **No aliases** — JSON keys must match Python attribute names exactly
- **Absolute imports** in test file: `from bank.model import Account`
- **No `__init__.py` changes** needed — `Account` is imported directly from `bank.model`

### Project Structure

Files touched in this story:
```
src/bank/model.py       ← replace stub with full implementation
tests/test_model.py     ← new test file
```

### Dependencies on Previous Stories

- Story 1.1: `uv sync` complete, pydantic available
- Story 1.2: `exceptions.py` exists (not imported by model, but part of overall structure)
- This story introduces no dependency on `exceptions.py` — `Account` raises `ValidationError`, not `BankError`

### References

- [Source: specs/architecture.md#Data Architecture] — two-tier validation, Pydantic for structural invariants
- [Source: specs/architecture.md#Naming & Format Patterns] — no aliases, field names match Python attributes
- [Source: specs/architecture.md#Interface Patterns] — model_dump/model_validate as serialization boundary
- [Source: specs/architecture.md#Anti-Patterns] — `model_dump(by_alias=True)` is explicitly forbidden
- [Source: specs/epics.md#Story 1.3] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

No blockers encountered. Implementation was straightforward following the story Dev Notes exactly.

### Completion Notes List

- Task 1: Replaced stub `Account` model with full Pydantic v2 implementation using `Field` constraints and `@field_validator` for numeric account number validation. All constraints enforced via Pydantic — no manual `if` guards.
- Task 2: Created `tests/test_model.py` with 14 unit tests organized in 6 test classes covering all 6 ACs. Tests written first (RED), then implementation made them pass (GREEN). 46/46 tests pass with no regressions.
- Task 3: `ruff check src/` → exit code 0 (clean). `mypy --strict src/` → exit code 0 (no issues in 6 source files).

### File List

- `src/bank/model.py` — modified: replaced stub with full `Account` Pydantic model
- `tests/test_model.py` — created: 14 unit tests for all ACs

## Change Log

- 2026-03-30: Story 1.3 implemented — Account Pydantic model with field constraints and validator; 14 unit tests added; all quality gates pass (ruff, mypy --strict). Status: ready-for-dev → review.
