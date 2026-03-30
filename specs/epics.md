---
stepsCompleted: [1, 2, 3, 4]
lastStep: 4
status: 'complete'
completedAt: '2026-03-29'
lastEdited: '2026-03-29'
workflowType: 'epics'
project_name: 'demo-migration-bms'
user_name: 'Arnould'
date: '2026-03-29'
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
**Stories:** 2.0 (service scaffold), 2.1 (create-account), 2.2 (deposit), 2.3 (withdraw), 2.4 (show-accounts)

### Epic 3: Migration Quality Assurance

After this epic, all NFR gates pass: zero linting violations, zero type errors, ≥ 90% test coverage, and every Java test scenario has a verified pytest equivalent. The migration is complete and measurably correct.
**FRs covered:** All FRs verified via test suite
**NFRs addressed:** NFR-1, NFR-2, NFR-3, NFR-4, NFR-5

## Epic 1: Runnable CLI Foundation

After this epic, any developer can clone the repo, run `uv sync`, and execute `uv run bank --help` to see all available commands. The full architectural skeleton is in place with all five modules wired together.

### Story 1.1: Project Scaffold & pyproject.toml Configuration

As a developer,
I want a correctly initialized Python package with all dependencies configured,
So that I can run `uv sync` and have the full dev environment ready without any manual steps.

**Acceptance Criteria:**

**Given** a clean directory,
**When** the scaffold is applied with `uv init --app --package bank --python ">=3.12"` and `pyproject.toml` is configured,
**Then** `uv sync` completes with no errors
**And** `uv run bank --help` exits with code 0

**Given** the `pyproject.toml` is inspected,
**When** dependencies are checked,
**Then** runtime deps include `pydantic >=2.12,<3` and `typer >=0.24,<1`
**And** dev deps include `pytest >=9,<10`, `pytest-cov`, `ruff >=0.15`, `mypy >=1.19`
**And** `[project.scripts]` declares `bank = "bank.cli:app"`
**And** `ruff check src/` and `mypy --strict src/` both exit with code 0

### Story 1.2: Exception Hierarchy

As a developer,
I want a typed exception hierarchy for all domain errors,
So that every error condition maps to a specific, catchable exception class.

**Acceptance Criteria:**

**Given** `exceptions.py` exists,
**When** any domain rule is violated,
**Then** the raised exception is a subclass of `BankError`
**And** `AccountNotFoundError`, `DuplicateAccountError`, `InsufficientBalanceError`, `InvalidAmountError` are all importable from `bank.exceptions`
**And** each exception accepts a `str` message
**And** `ruff check src/` and `mypy --strict src/` pass with this file in place

### Story 1.3: Account Model

As a developer,
I want an `Account` Pydantic `BaseModel` with enforced field constraints,
So that no invalid `Account` instance can be created anywhere in the system.

**Acceptance Criteria:**

**Given** valid inputs (numeric account number, non-empty owner, balance ≥ 0),
**When** `Account(account_number=..., owner=..., balance=...)` is called,
**Then** the model is created successfully

**Given** account number `"abc"` (non-numeric),
**When** `Account(account_number="abc", ...)` is called,
**Then** a `ValidationError` is raised with a message referencing the account number format rule

**Given** an empty owner string or balance < 0,
**When** the model is constructed with those values,
**Then** a `ValidationError` is raised for the specific violated field

**Given** a valid account,
**When** `account.model_dump()` is called,
**Then** output is `{"account_number": ..., "owner": ..., "balance": ...}` with no aliases
**And** `Account.model_validate(account.model_dump())` round-trips without data loss
**And** `ruff check src/` and `mypy --strict src/` pass

### Story 1.4: Repository Layer

As a developer,
I want an `AccountRepository` Protocol and a `JsonFileAccountRepository` implementation,
So that the service layer can read and write accounts without knowing about file persistence.

**Acceptance Criteria:**

**Given** no `accounts.json` file exists,
**When** `JsonFileAccountRepository().find_all()` is called,
**Then** it returns an empty list with no error

**Given** an account saved via `save()` in one `JsonFileAccountRepository` instance,
**When** `find_all()` is called on a new instance pointing to the same file,
**Then** the saved account is returned

**Given** a known account number,
**When** `find_by_id(account_number)` is called,
**Then** the matching `Account` is returned; for an unknown number, `None` is returned (no exception)

**Given** `accounts.json` is inspected after a `save()`,
**When** field names are checked,
**Then** they match Python attribute names exactly (`account_number`, `owner`, `balance`) — no aliases
**And** `JsonFileAccountRepository` satisfies the `AccountRepository` Protocol without inheriting from it
**And** `ruff check src/` and `mypy --strict src/` pass

### Story 1.5: CLI Scaffold & Command Discovery

As a CLI operator,
I want all commands discoverable via `--help`,
So that I can learn the available commands and their arguments without reading source code.

**Acceptance Criteria:**

**Given** the CLI is installed,
**When** I run `uv run bank --help`,
**Then** output lists all four commands: `create-account`, `deposit`, `withdraw`, `show-accounts`

**When** I run `uv run bank create-account --help`,
**Then** output shows `ACCOUNT_NUMBER`, `OWNER`, `INITIAL_BALANCE` as required arguments

**When** I run `uv run bank deposit --help` or `uv run bank withdraw --help`,
**Then** output shows `ACCOUNT_NUMBER` and `AMOUNT` as required arguments

**When** I run `uv run bank show-accounts --help`,
**Then** output confirms the command takes no arguments
**And** `cli.py` wires `BankServiceImpl(JsonFileAccountRepository())` as the composition root
**And** `ruff check src/` and `mypy --strict src/` pass

## Epic 2: Core Banking Operations

After this epic, the CLI operator can create accounts, deposit and withdraw funds, and list all accounts with formatted output. All business rules are enforced and all error messages are specific, field-named, and actionable.

### Story 2.0: BankService Protocol & BankServiceImpl Scaffold

As a developer,
I want a `BankService` Protocol and a concrete `BankServiceImpl` stub wired into the CLI,
So that Banking Operations stories (2.1–2.4) have a clearly defined place to add business logic.

**Acceptance Criteria:**

**Given** `src/bank/service.py` exists,
**When** it is inspected,
**Then** it defines a `BankService` Protocol with method signatures for `create_account`, `deposit`, `withdraw`, and `get_all_accounts`
**And** `BankServiceImpl` is a concrete class that satisfies `BankService` without inheriting from it
**And** each method raises `NotImplementedError` at this stage (to be replaced in Stories 2.1–2.4)
**And** `BankServiceImpl.__init__` accepts an `AccountRepository` parameter

**Given** `src/bank/cli.py` is inspected,
**When** the composition root is reviewed,
**Then** the `typer` app wires `BankServiceImpl(JsonFileAccountRepository())` as the service instance passed to each command
**And** `ruff check src/` and `mypy --strict src/` pass with `service.py` in place

### Story 2.1: Create Account Command

As a CLI operator,
I want to create a bank account with a validated account number, owner name, and initial balance,
So that I can start managing funds for a new customer.

**Acceptance Criteria:**

**Given** valid arguments,
**When** I run `uv run bank create-account 001 Ali 500.0`,
**Then** output is `"Account created successfully."` and the account is persisted to `accounts.json`

**Given** an account number already in use,
**When** I run `create-account 001 ...` again,
**Then** the command fails with a duplicate account error message (no raw traceback)

**Given** account number `"abc"` (non-numeric),
**When** I run `create-account abc Ali 500.0`,
**Then** the command fails with a message naming the account number format rule

**Given** initial balance `-100.0`,
**When** I run `create-account 001 Ali -100.0`,
**Then** the command fails with a message naming the balance ≥ 0 rule

**And** a subsequent `show-accounts` invocation lists the created account

### Story 2.2: Deposit Command

As a CLI operator,
I want to deposit funds into an existing account,
So that I can increase the account balance.

**Acceptance Criteria:**

**Given** account `001` with balance `500.0`,
**When** I run `uv run bank deposit 001 200.0`,
**Then** output is `"Deposit successful."` and balance is now `700.0` in `accounts.json`

**Given** an unknown account number,
**When** I run `deposit 999 100.0`,
**Then** the command fails with an account-not-found error message

**Given** amount `0.0` or `-50.0`,
**When** the deposit command is run with those values,
**Then** the command fails with a message stating the amount must be greater than 0
**And** the balance is not modified

### Story 2.3: Withdrawal Command

As a CLI operator,
I want to withdraw funds from an existing account,
So that I can process a customer disbursement.

**Acceptance Criteria:**

**Given** account `001` with balance `500.0`,
**When** I run `uv run bank withdraw 001 200.0`,
**Then** output is `"Withdrawal successful."` and balance is now `300.0` in `accounts.json`

**Given** account `001` with balance `300.0`,
**When** I run `withdraw 001 800.0`,
**Then** the command fails with a message that includes both the attempted amount (`800.00`) and the current balance (`300.00`)
**And** the balance is unchanged

**Given** an unknown account number,
**When** I run `withdraw 999 100.0`,
**Then** the command fails with an account-not-found error message

**Given** amount `0.0`,
**When** I run `withdraw 001 0.0`,
**Then** the command fails with a positivity rule message

### Story 2.4: Account Listing Command

As a CLI operator,
I want to list all accounts with their balances,
So that I can see the current state of all accounts at a glance.

**Acceptance Criteria:**

**Given** two accounts exist,
**When** I run `uv run bank show-accounts`,
**Then** output is a formatted table with columns: Account Number, Owner, Balance
**And** balance values are formatted to 2 decimal places (e.g. `500.00`)

**Given** no accounts exist,
**When** I run `show-accounts`,
**Then** output is `"No accounts found."`

**And** accounts created in prior command invocations appear in the listing (persistence verified)

## Epic 3: Migration Quality Assurance

After this epic, all NFR gates pass: zero linting violations, zero type errors, ≥ 90% test coverage, and every Java test scenario has a verified pytest equivalent. The migration is complete and measurably correct.

### Story 3.1: Test Foundation & Account Model Tests

As a developer,
I want shared test fixtures and unit tests for the `Account` model,
So that model validation behavior is provably correct and fixtures are reusable across the suite.

**Acceptance Criteria:**

**Given** `tests/conftest.py` exists,
**When** the test suite runs,
**Then** it provides: a sample valid `Account` fixture, a `tmp_path`-based JSON file fixture, and a pre-populated `JsonFileAccountRepository` fixture

**Given** `tests/test_model.py` exists,
**When** pytest runs,
**Then** it covers: valid account creation, rejection of non-numeric account numbers, rejection of empty owner, rejection of negative balance
**And** `account.model_dump()` / `Account.model_validate()` round-trip is tested
**And** `pytest --cov` reports coverage for `bank/model.py`

### Story 3.2: Service & Repository Tests

As a developer,
I want complete tests for the service and repository layers,
So that business logic and persistence behavior are independently verified.

**Acceptance Criteria:**

**Given** `tests/test_repository.py` exists,
**When** pytest runs,
**Then** it covers: `find_all()` on a missing file returns `[]`, `save()` + `find_by_id()` round-trip, `exists()` with known and unknown IDs, persistence across two `JsonFileAccountRepository` instances on the same temp file

**Given** `tests/test_service.py` exists,
**When** pytest runs,
**Then** it covers: `create_account` success, `DuplicateAccountError` on duplicate, `deposit` success and `InvalidAmountError` on zero/negative amount, `withdraw` success and `InsufficientBalanceError` on overdraft, `AccountNotFoundError` for deposit/withdraw on unknown account
**And** all four Java test scenarios (create, deposit, withdraw, overdraft rejection) have direct pytest equivalents

### Story 3.3: CLI Integration Tests & Error Message Assertions

As a developer,
I want CLI-level tests that verify command output and error message content,
So that the user-facing UX is regression-protected.

**Acceptance Criteria:**

**Given** `tests/test_cli.py` uses typer's `CliRunner`,
**When** pytest runs,
**Then** it covers success paths: `create-account` prints `"Account created successfully."`, `deposit` prints `"Deposit successful."`, `withdraw` prints `"Withdrawal successful."`, `show-accounts` prints a formatted table, empty state prints `"No accounts found."`

**And** error paths assert on message content (not just exit code): duplicate account message, overdraft message containing both amounts, non-numeric account number message, account-not-found message
**And** no test asserts on raw Pydantic `ValidationError` format — all assertions target the reformatted user-facing string

### Story 3.4: NFR Gates — Linting, Typing & Coverage

As a developer,
I want all quality gates to pass on the complete codebase,
So that the migration is measurably complete and the codebase is maintainable.

**Acceptance Criteria:**

**Given** the full codebase,
**When** `ruff check src/` is run,
**Then** exit code is 0 with zero violations (NFR-1)

**When** `mypy --strict src/` is run,
**Then** exit code is 0 with zero errors (NFR-2)

**When** `pytest --cov` is run,
**Then** reported line coverage is ≥ 90% (NFR-3)

**When** source files under `src/bank/` are reviewed,
**Then** no `if` guards for input validation exist outside Pydantic model definitions (NFR-4)

**When** a clean clone runs `uv sync` then `uv run bank --help`,
**Then** the command succeeds with no errors (NFR-6)