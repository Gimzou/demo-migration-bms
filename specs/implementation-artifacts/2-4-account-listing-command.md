# Story 2.4: Account Listing Command

Status: ready-for-dev

## Story

As a CLI operator,
I want to list all accounts with their balances,
so that I can see the current state of all accounts at a glance.

## Acceptance Criteria

1. When two or more accounts exist, `uv run bank show-accounts` prints a formatted table with columns: Account Number, Owner, Balance — with balance values formatted to 2 decimal places (e.g. `500.00`).
2. When no accounts exist, `show-accounts` prints `"No accounts found."`.
3. Accounts created in prior command invocations appear in the listing (end-to-end persistence verified).
4. `ruff check src/` and `mypy --strict src/` pass.

## Tasks / Subtasks

- [ ] Task 1: Implement `BankServiceImpl.get_all_accounts()` in `src/bank/service.py` (AC: 1, 2, 3)
  - [ ] Delegate directly to `self._repository.find_all()` and return the result

- [ ] Task 2: Implement `show_accounts` command body in `src/bank/cli.py` (AC: 1, 2)
  - [ ] Call `_get_service().get_all_accounts()`
  - [ ] If empty list: `typer.echo("No accounts found.")`
  - [ ] If accounts exist: print header row, then one row per account with aligned columns
  - [ ] Format balance as `f"{account.balance:.2f}"`
  - [ ] No try/except needed (method raises no domain exceptions)

- [ ] Task 3: Run quality gates (AC: 4)
  - [ ] `ruff check src/` → exit code 0
  - [ ] `mypy --strict src/` → exit code 0

## Dev Notes

### Implementation — `src/bank/service.py`

Replace the `get_all_accounts` stub with:

```python
def get_all_accounts(self) -> list[Account]:
    return self._repository.find_all()
```

No guards, no exceptions — this method is a pure read delegated to the repository. `find_all()` returns `[]` when `accounts.json` does not exist (handled by `JsonFileAccountRepository`).

### Implementation — `src/bank/cli.py`

Replace the `show_accounts` command body:

```python
@app.command()
def show_accounts() -> None:
    """Display all accounts."""
    accounts = _get_service().get_all_accounts()
    if not accounts:
        typer.echo("No accounts found.")
        return

    headers = ("Account Number", "Owner", "Balance")
    rows = [
        (a.account_number, a.owner, f"{a.balance:.2f}")
        for a in accounts
    ]

    col_widths = [
        max(len(headers[i]), *(len(row[i]) for row in rows))
        for i in range(3)
    ]

    def fmt_row(cols: tuple[str, str, str]) -> str:
        return (
            f"{cols[0]:<{col_widths[0]}}  "
            f"{cols[1]:<{col_widths[1]}}  "
            f"{cols[2]:>{col_widths[2]}}"
        )

    typer.echo(fmt_row(headers))
    for row in rows:
        typer.echo(fmt_row(row))
```

**Why no try/except:** `get_all_accounts()` delegates to `find_all()`, which returns `[]` on a missing file and never raises `BankError` or `ValidationError`. The CLI error-handling pattern only applies to commands with business-rule failure paths.

**Column alignment:**
- Account Number and Owner: left-aligned (`:<width`)
- Balance: right-aligned (`:>width`) — conventional for numeric columns

**Dynamic widths:** column widths are computed from the actual data so the table stays readable regardless of account number length or owner name length.

### mypy Considerations

The `fmt_row` helper has a `tuple[str, str, str]` parameter — mypy strict mode will accept this. The list comprehension for `col_widths` produces `list[int]`, and the f-string width specifiers (`col_widths[0]` etc.) are `int` — all clean under `--strict`.

If mypy flags the unpacking in `max(len(headers[i]), *(len(row[i]) for row in rows))`, rewrite as:
```python
col_widths = [
    max(len(headers[i]), max(len(row[i]) for row in rows))
    for i in range(3)
]
```

### Expected Output Examples

**Two accounts:**
```
Account Number  Owner  Balance
001             Ali     500.00
002             Bob    1000.00
```

**No accounts:**
```
No accounts found.
```

### No Extra Libraries

Runtime dependencies are `pydantic` and `typer` only. Do **not** add `tabulate`, `rich`, or any other formatting library. The plain f-string approach above satisfies the AC.

### Files to Modify

```
src/bank/service.py    ← implement get_all_accounts()
src/bank/cli.py        ← implement show_accounts() body
```

No new source files. No test files in this story (tests are Epic 3).

### Existing Tests to Keep Green

- `tests/test_service.py` — any test asserting `NotImplementedError` for `get_all_accounts` must be updated or removed.
- All Story 2.1, 2.2, and 2.3 tests must still pass.

After this story, all four `BankServiceImpl` methods are fully implemented. Epic 2 is functionally complete.

### References

- [Source: specs/architecture.md#Naming & Format Patterns] — CLI output format: `"show-accounts: plain-text table with aligned columns"`, `"No accounts found."`, balance to 2 decimal places
- [Source: specs/architecture.md#Technical Constraints] — runtime deps are pydantic and typer only; no additional formatting libraries
- [Source: specs/epics.md#Story 2.4] — Acceptance criteria
- [Source: specs/implementation-artifacts/1-5-cli-scaffold-command-discovery.md] — `show_accounts` Python function maps to `show-accounts` CLI command (typer auto-converts underscores)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List