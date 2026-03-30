# Story 1.2: Exception Hierarchy

Status: ready-for-dev

## Story

As a developer,
I want a typed exception hierarchy for all domain errors,
so that every error condition maps to a specific, catchable exception class.

## Acceptance Criteria

1. `exceptions.py` defines `BankError` as the base exception class.
2. Four subtypes are importable from `bank.exceptions`: `AccountNotFoundError`, `DuplicateAccountError`, `InsufficientBalanceError`, `InvalidAmountError`.
3. Each exception accepts a `str` message via its constructor.
4. `ruff check src/` exits with code 0.
5. `mypy --strict src/` exits with code 0.

## Tasks / Subtasks

- [ ] Task 1: Implement exception hierarchy in `src/bank/exceptions.py` (AC: 1, 2, 3)
  - [ ] Replace the Story 1.1 stub with full implementation
  - [ ] Define `BankError(Exception)` with `message: str` constructor
  - [ ] Define all four subtypes inheriting from `BankError`
  - [ ] Ensure each subtype passes its message up to `super().__init__(message)`

- [ ] Task 2: Write unit tests in `tests/test_exceptions.py` (AC: 2, 3)
  - [ ] Test that each exception is a subclass of `BankError`
  - [ ] Test that `isinstance(exc, BankError)` is `True` for all subtypes
  - [ ] Test that `str(exc)` returns the message passed at construction

- [ ] Task 3: Verify quality gates (AC: 4, 5)
  - [ ] `ruff check src/` → exit code 0
  - [ ] `mypy --strict src/` → exit code 0

## Dev Notes

### Implementation

`src/bank/exceptions.py` — full file:

```python
class BankError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class AccountNotFoundError(BankError):
    pass


class DuplicateAccountError(BankError):
    pass


class InsufficientBalanceError(BankError):
    pass


class InvalidAmountError(BankError):
    pass
```

**Why `self.message`?** The CLI layer reads the exception message via `str(exc)` or `exc.message` to format user output. Storing it as an attribute makes it accessible without `exc.args[0]`.

### mypy --strict Compliance

- `__init__` must be annotated with `-> None`
- `message: str` parameter must be typed
- Subtypes with `pass` bodies are valid — they inherit `__init__` from `BankError`

### Usage Contract (for dev agent context)

The service layer raises these exceptions; the CLI layer catches them:

```python
# service.py — raises
raise AccountNotFoundError(f"Account {account_number} not found.")
raise DuplicateAccountError(f"Account {account_number} already exists.")
raise InsufficientBalanceError(
    f"Insufficient balance: cannot withdraw {amount:.2f} from account "
    f"{account_number} (current balance: {balance:.2f})."
)
raise InvalidAmountError("Amount must be greater than 0.")

# cli.py — catches
except BankError as exc:
    typer.echo(str(exc))
    raise typer.Exit(1)
```

The exact message wording is defined in the architecture and enforced by CLI integration tests in Epic 3.

### Architecture Constraints

- This file has **no imports** from other `bank` modules — it is the lowest-level dependency.
- Import style for consumers: `from bank.exceptions import AccountNotFoundError` (absolute, never relative).
- **Do not** add `__all__` — it is not required and adds noise.
- Error message format from architecture: `"{What failed}: {context with values}."` — no `"Error:"` prefix; the CLI decides presentation.

### Project Structure

Only file touched in this story:
```
src/bank/exceptions.py    ← replace stub with full implementation
tests/test_exceptions.py  ← new test file
```

All other stubs from Story 1.1 remain unchanged.

### Dependency on Story 1.1

This story assumes Story 1.1 is complete:
- `uv sync` has been run and all deps are available
- `src/bank/` directory structure exists with stubs
- `ruff` and `mypy` are available via `uv run ruff` / `uv run mypy`

If Story 1.1 is not done, complete it first.

### References

- [Source: specs/architecture.md#Exception Hierarchy] — flat hierarchy, 4 subtypes, 1:1 with business rules
- [Source: specs/architecture.md#Error Handling Flow] — CLI is the only place that formats exception messages
- [Source: specs/architecture.md#Enforcement Guidelines] — run quality gates before marking done
- [Source: specs/epics.md#Story 1.2] — acceptance criteria

## Dev Agent Record

### Agent Model Used

_to be filled by dev agent_

### Debug Log References

### Completion Notes List

### File List