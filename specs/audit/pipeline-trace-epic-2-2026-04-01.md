# Pipeline Trace — 2026-04-01
**Mode:** epic
**Target:** epic-2
**Stories:**
1. specs/implementation-artifacts/2-0-bankservice-protocol-bankserviceimpl-scaffold.md
2. specs/implementation-artifacts/2-1-create-account-command.md
3. specs/implementation-artifacts/2-2-deposit-command.md
4. specs/implementation-artifacts/2-3-withdrawal-command.md
5. specs/implementation-artifacts/2-4-account-listing-command.md
---

## 2-0 — Iteration 1 — Dev
- Tasks: 3/3
- Tests written: 0
- Status: review

### QA verdict: clean ✓
- Tests: 70 passed / 0 failed
- ACs: 6/6
**Story complete after 1 iteration(s).**

## 2-1 — Iteration 1 — Dev
- Tasks: 3/3
- Tests written: 4
- Status: review

### QA verdict: needs-rework
- Ruff fixes: 0
- Tests: 73 passed / 0 failed
- ACs satisfied: 3/5
- Issues:
  - AC4 FAIL: Typer parses `-100.0` as option flag `-1` before Pydantic validation fires. Fix: use `Annotated[float, typer.Argument()]`.
  - AC5 FAIL: `show-accounts` exits silently; `BankServiceImpl.get_all_accounts()` raises NotImplementedError. Needs minimal listing or AC moved to Story 2.4.

## 2-1 — Iteration 2 — Dev
- Tasks: 3/3
- Tests written: 1
- Status: review

### QA verdict: clean ✓
- Tests: 73 passed / 0 failed
- ACs: 5/5
**Story complete after 2 iteration(s).**

## 2-2 — Iteration 1 — Dev
- Tasks: 3/3
- Tests written: 5
- Status: review

### QA verdict: clean ✓
- Tests: 77 passed / 0 failed
- ACs: 4/4
**Story complete after 1 iteration(s).**

## 2-3 — Iteration 1 — Dev
- Tasks: 3/3
- Tests written: 12
- Status: review

### QA verdict: clean ✓
- Tests: 88 passed / 0 failed
- ACs: 5/5
**Story complete after 1 iteration(s).**

## 2-4 — Iteration 1 — Dev
- Tasks: 3/3
- Tests written: 0
- Status: review

### QA verdict: clean ✓
- Tests: 88 passed / 0 failed
- ACs: 4/4
**Story complete after 1 iteration(s).**

---
## Pipeline Summary
**Stories processed:** 5
**Done:** 5
**Blocked:** 0

| Story | Result | Iterations |
|-------|--------|------------|
| 2-0   | done   | 1          |
| 2-1   | done   | 2          |
| 2-2   | done   | 1          |
| 2-3   | done   | 1          |
| 2-4   | done   | 1          |
