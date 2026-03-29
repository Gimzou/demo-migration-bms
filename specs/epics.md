---
stepsCompleted: [1, 2]
inputDocuments:
  - specs/prd.md
  - specs/architecture.md
---

# demo-migration-bms - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for demo-migration-bms, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR-1: Users can create a bank account by providing an account number, owner name, and initial balance. All three fields are validated at creation time (account number is a non-empty numeric string, owner is non-empty, initial balance ≥ 0). Duplicate account numbers are rejected. Invalid inputs produce field-specific error messages.

FR-2: Users can deposit funds into an existing account. The deposit amount must be strictly greater than 0. Non-existent accounts and non-positive amounts produce specific error messages. The updated balance is persisted immediately.

FR-3: Users can withdraw funds from an existing account. The withdrawal amount must be strictly greater than 0 and must not exceed the current balance. Overdraft attempts are rejected with a message including the current balance and the attempted amount. The updated balance is persisted immediately without modification on failure.

FR-4: Users can display all existing accounts. Each account shows its account number, owner name, and balance formatted to 2 decimal places. If no accounts exist, the output states that explicitly. Output is human-readable tabular text.

FR-5: Every command supports `--help`, displaying its name, description, and required arguments with types. The root command (`uv run bank --help`) lists all available commands.

FR-6: Accounts created or modified by one command invocation are available to subsequent commands. Data is persisted to `accounts.json` in the working directory automatically — no setup step required.

### NonFunctional Requirements

NFR-1: `ruff check src/` produces zero violations. All Python source files follow PEP 8 naming conventions.

NFR-2: `mypy --strict src/` produces zero type errors. All function signatures include type annotations. Pydantic models provide runtime type enforcement.

NFR-3: Test suite covers ≥ 90% of source lines. Every FR has at least one corresponding pytest test. All Java test scenarios have pytest equivalents.

NFR-4: Every business rule (balance ≥ 0, amount > 0, account number format, owner non-empty) is expressed as a Pydantic `Field` constraint or `@field_validator` — not as a manual `if` guard in application code.

NFR-5: All user-facing error messages name the specific field, state the violated rule, and imply the corrective action. Raw Pydantic `ValidationError` tracebacks are never shown to the user. Each error scenario in the test suite asserts on the message content, not just the exception type.

NFR-6: The project runs with `uv sync` followed by `uv run bank <command>`. No manual setup, virtual environment creation, or configuration steps required.

### Additional Requirements

- **Project scaffold**: Architecture specifies `uv init --app --package bank --python ">=3.12"` as the starter template — this must be Epic 1 Story 1
- **Entry point**: `pyproject.toml` must declare `bank = "bank.cli:app"` under `[project.scripts]` to enable `uv run bank`
- **Runtime dependencies**: `pydantic >=2.12,<3` and `typer >=0.24,<1` must be added post-init
- **Dev tooling**: `pytest >=9,<10`, `pytest-cov`, `ruff >=0.15`, `mypy >=1.19` must be added as dev dependencies with tool configuration in `pyproject.toml`
- **Module structure**: Flat layout in `src/bank/` — one file per concern: `cli.py`, `model.py`, `service.py`, `repository.py`, `exceptions.py`
- **Protocol-based interfaces**: `AccountRepository` and `BankService` must be defined as `Protocol` classes; concrete implementations do not inherit from them
- **Two-tier validation**: Pydantic `Field`/`@field_validator` for structural invariants on `Account`; service layer for operational guards (duplicate detection, overdraft, amount > 0)
- **Exception hierarchy**: `BankError` base with four subtypes: `AccountNotFoundError`, `DuplicateAccountError`, `InsufficientBalanceError`, `InvalidAmountError`
- **Test structure**: One test file per source module in `tests/`; shared fixtures in `conftest.py`
- **Import style**: Absolute imports only (`from bank.model import Account`) — no relative imports

### UX Design Requirements

*N/A — This is a CLI tool with no graphical UI. Output formatting requirements are captured in FR-4 and NFR-5.*

### FR Coverage Map

FR-1: Epic 2 — Account creation with field validation and duplicate detection
FR-2: Epic 2 — Deposit with amount > 0 validation and balance persistence
FR-3: Epic 2 — Withdrawal with overdraft protection and balance persistence
FR-4: Epic 2 — Account listing with tabular output and empty-state message
FR-5: Epic 1 — Command discoverability via typer `--help` on all commands
FR-6: Epic 1 — Cross-invocation persistence via `JsonFileAccountRepository`

## Epic List

### Epic 1: Runnable CLI Foundation

After this epic, any developer can clone the repo, run `uv sync`, and execute `uv run bank --help` to see all available commands. The full architectural skeleton is in place with all five modules wired together.
**FRs covered:** FR-5, FR-6
**NFRs addressed:** NFR-6 (zero-setup), NFR-1 and NFR-2 enforced from day one

### Epic 2: Core Banking Operations

After this epic, the CLI operator can create accounts, deposit and withdraw funds, and list all accounts with formatted output. All business rules are enforced and all error messages are specific, field-named, and actionable.
**FRs covered:** FR-1, FR-2, FR-3, FR-4
**NFRs addressed:** NFR-4 (Pydantic validation architecture), NFR-5 (error message quality)

### Epic 3: Migration Quality Assurance

After this epic, all NFR gates pass: zero linting violations, zero type errors, ≥ 90% test coverage, and every Java test scenario has a verified pytest equivalent. The migration is complete and measurably correct.
**FRs covered:** All FRs verified via test suite
**NFRs addressed:** NFR-1, NFR-2, NFR-3, NFR-4, NFR-5