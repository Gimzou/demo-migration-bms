# Story 1.4: Repository Layer

Status: ready-for-dev

## Story

As a developer,
I want an `AccountRepository` Protocol and a `JsonFileAccountRepository` implementation,
so that the service layer can read and write accounts without knowing about file persistence.

## Acceptance Criteria

1. `JsonFileAccountRepository().find_all()` returns an empty list when no `accounts.json` file exists — no error raised.
2. An account saved via `save()` in one `JsonFileAccountRepository` instance is returned by `find_all()` on a new instance pointing to the same file.
3. `find_by_id(account_number)` returns the matching `Account` for a known number; returns `None` for an unknown number (no exception).
4. `accounts.json` field names after a `save()` match Python attribute names exactly (`account_number`, `owner`, `balance`) — no aliases.
5. `JsonFileAccountRepository` satisfies the `AccountRepository` Protocol without inheriting from it.
6. `ruff check src/` exits with code 0.
7. `mypy --strict src/` exits with code 0.

## Tasks / Subtasks

- [ ] Task 1: Implement `repository.py` (AC: 1–5)
  - [ ] Replace Story 1.1 stub with full `AccountRepository` Protocol
  - [ ] Implement `JsonFileAccountRepository` with `accounts.json` persistence
  - [ ] `find_all()`: return `[]` if file absent; load and deserialize otherwise
  - [ ] `find_by_id()`: return matching `Account` or `None`
  - [ ] `exists()`: return `True` if account_number present
  - [ ] `save()`: read-modify-write — replace existing or append new account
  - [ ] Accept optional `file_path: Path` in constructor (enables test isolation)

- [ ] Task 2: Write unit tests in `tests/test_repository.py` (AC: 1–5)
  - [ ] Test: `find_all()` on missing file returns `[]`
  - [ ] Test: `save()` + `find_by_id()` round-trip
  - [ ] Test: `exists()` returns `True` for known ID, `False` for unknown
  - [ ] Test: persistence across two `JsonFileAccountRepository` instances on the same temp file
  - [ ] Test: `accounts.json` field names match Python attributes (inspect raw JSON)

- [ ] Task 3: Verify quality gates (AC: 6, 7)
  - [ ] `ruff check src/` → exit code 0
  - [ ] `mypy --strict src/` → exit code 0

## Dev Notes

### Implementation

`src/bank/repository.py` — full file:

```python
import json
from pathlib import Path
from typing import Protocol

from bank.model import Account

DEFAULT_FILE = Path("accounts.json")


class AccountRepository(Protocol):
    def find_all(self) -> list[Account]: ...
    def find_by_id(self, account_number: str) -> Account | None: ...
    def save(self, account: Account) -> None: ...
    def exists(self, account_number: str) -> bool: ...


class JsonFileAccountRepository:
    def __init__(self, file_path: Path = DEFAULT_FILE) -> None:
        self._file_path = file_path

    def find_all(self) -> list[Account]:
        if not self._file_path.exists():
            return []
        with self._file_path.open() as f:
            data: list[dict[str, object]] = json.load(f)
        return [Account.model_validate(item) for item in data]

    def find_by_id(self, account_number: str) -> Account | None:
        for account in self.find_all():
            if account.account_number == account_number:
                return account
        return None

    def exists(self, account_number: str) -> bool:
        return self.find_by_id(account_number) is not None

    def save(self, account: Account) -> None:
        accounts = self.find_all()
        updated = False
        for i, existing in enumerate(accounts):
            if existing.account_number == account.account_number:
                accounts[i] = account
                updated = True
                break
        if not updated:
            accounts.append(account)
        with self._file_path.open("w") as f:
            json.dump([a.model_dump() for a in accounts], f, indent=2)
```

### Design Decisions

**`file_path` constructor parameter with default:**
Enables test isolation via `tmp_path` fixture (pytest built-in) without changing production code. Default `Path("accounts.json")` resolves relative to the current working directory at call time — matching the CLI invocation pattern.

**Read-modify-write in `save()`:**
Each `save()` call reads the full file, updates the matching entry or appends, and writes back. For a demo-scope CLI with <1000 accounts this is fine. The service layer never calls `save()` on a partially-modified state.

**Repository returns `None`, never raises:**
`find_by_id()` returns `None` for unknown accounts — no exception. It is the service layer's responsibility to decide whether `None` means "raise `AccountNotFoundError`" or "proceed normally" (e.g., checking for duplicates).

**No `AccountNotFoundError` in this file:**
`exceptions.py` is NOT imported here. Repository is purely a data access layer.

### Protocol Structural Typing

`JsonFileAccountRepository` satisfies `AccountRepository` without inheriting:

```python
# This is valid — structural typing, not nominal
def use_repo(repo: AccountRepository) -> None: ...

use_repo(JsonFileAccountRepository())  # ✅ mypy accepts this
```

mypy --strict verifies structural compatibility automatically. No `# type: ignore` needed.

### Test Pattern — Use `tmp_path` Fixture

```python
# tests/test_repository.py
from pathlib import Path
import pytest
from bank.model import Account
from bank.repository import JsonFileAccountRepository

def test_find_all_returns_empty_when_file_missing(tmp_path: Path) -> None:
    repo = JsonFileAccountRepository(tmp_path / "accounts.json")
    assert repo.find_all() == []

def test_save_and_find_by_id_roundtrip(tmp_path: Path) -> None:
    repo = JsonFileAccountRepository(tmp_path / "accounts.json")
    account = Account(account_number="001", owner="Ali", balance=500.0)
    repo.save(account)
    result = repo.find_by_id("001")
    assert result == account

def test_persistence_across_instances(tmp_path: Path) -> None:
    file = tmp_path / "accounts.json"
    repo1 = JsonFileAccountRepository(file)
    repo1.save(Account(account_number="001", owner="Ali", balance=500.0))
    repo2 = JsonFileAccountRepository(file)
    assert repo2.find_by_id("001") is not None

def test_find_by_id_returns_none_for_unknown(tmp_path: Path) -> None:
    repo = JsonFileAccountRepository(tmp_path / "accounts.json")
    assert repo.find_by_id("999") is None

def test_json_field_names_match_python_attributes(tmp_path: Path) -> None:
    import json
    file = tmp_path / "accounts.json"
    repo = JsonFileAccountRepository(file)
    repo.save(Account(account_number="001", owner="Ali", balance=500.0))
    raw = json.loads(file.read_text())
    assert list(raw[0].keys()) == ["account_number", "owner", "balance"]
```

### mypy --strict Notes

- `data: list[dict[str, object]]` annotation on the `json.load()` result is required — without it mypy infers `Any`
- `DEFAULT_FILE = Path("accounts.json")` at module level is fine — mypy infers `Path` type
- All method signatures must include return types (`-> None`, `-> list[Account]`, etc.)
- `Protocol` must be imported from `typing` (Python 3.12 still uses `typing.Protocol`)

### Architecture Constraints

- `accounts.json` is created in the **current working directory** (where `uv run bank` is invoked), not relative to the source file
- **No relative imports** — `from bank.model import Account` only
- **No aliases** — `model_dump()` with no arguments; JSON keys will be `account_number`, `owner`, `balance`
- The `AccountRepository` Protocol is the only interface the service layer sees — it must not import `JsonFileAccountRepository` directly

### Project Structure

Files touched in this story:
```
src/bank/repository.py     ← replace stub with full implementation
tests/test_repository.py   ← new test file
```

### Dependencies on Previous Stories

- Story 1.1: `uv sync` complete
- Story 1.3: `Account` model with validators — `model_validate()` enforces constraints on load

### References

- [Source: specs/architecture.md#Data Architecture] — Protocol-based repository, no service knowledge of persistence
- [Source: specs/architecture.md#Interface Patterns] — exact `AccountRepository` Protocol method signatures
- [Source: specs/architecture.md#Naming & Format Patterns] — JSON field names = Python attribute names, no `by_alias`
- [Source: specs/architecture.md#Anti-Patterns] — `raise AccountNotFoundError` inside repository is explicitly forbidden
- [Source: specs/epics.md#Story 1.4] — acceptance criteria

## Dev Agent Record

### Agent Model Used

_to be filled by dev agent_

### Debug Log References

### Completion Notes List

### File List
