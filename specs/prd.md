---
stepsCompleted: [step-01-init, step-02-discovery, step-02b-vision, step-02c-executive-summary, step-03-success, step-04-journeys, step-05-domain-skipped, step-06-innovation-skipped, step-07-project-type, step-e-01-discovery, step-e-02-review, step-e-03-edit]
lastEdited: '2026-03-29'
editHistory:
  - date: '2026-03-29'
    changes: 'Coherence fixes (persistence refs, CLI model), added Functional Requirements (FR-1–6) and Non-Functional Requirements (NFR-1–6)'
classification:
  projectType: cli_tool
  domain: fintech_demo
  complexity: low
  projectContext: brownfield
inputDocuments:
  - specs/research/technical-bank-management-system-migration-research-2026-03-28.md
workflowType: 'prd'
briefCount: 0
researchCount: 1
brainstormingCount: 0
projectDocsCount: 1
---

# Product Requirements Document - demo-migration-bms

**Author:** Arnould
**Date:** 2026-03-28

## Executive Summary

The Bank Management System (BMS) is a Python rewrite of an existing Java console banking application. The rewrite replaces imperative, scattered validation with declarative, framework-enforced business rules using Pydantic v2. The end-users are operators of the CLI who invoke argument-based commands to create accounts, deposit, withdraw, and view balances.

The Java predecessor is functionally complete but architecturally weak on validation: business rules (`balance ≥ 0`, `amount ≤ balance`) are buried in constructor guards with no validation on deposit amounts, account number format, or owner name. A single catch-all exception handler obscures all error distinctions. The Python rewrite corrects these gaps, improves user-facing error feedback, and delivers a codebase that is easier to set up, run, and extend.

### What Makes This Special

Pydantic v2 is not introduced as a convenience layer — it is the architectural foundation. By defining `Account` as a `pydantic.BaseModel` with `Field` constraints and `@field_validator` rules, business rules become the schema: declared once, enforced everywhere, visible to any reader of the code, and verifiable by the test suite. This shifts the BMS from a system where correctness is the developer's responsibility to one where correctness is enforced by the framework.

The result is a user experience improvement at two levels: the application raises specific, meaningful errors (not generic exceptions), and the codebase communicates its own rules without requiring a developer to trace through imperative logic.

## Project Classification

| Attribute | Value |
|-----------|-------|
| Project Type | CLI tool — argument-based commands via `typer`, with built-in `--help` |
| Domain | Banking (fintech demo scope — no compliance or auth requirements) |
| Complexity | Low — 4 operations, JSON file persistence, ~200 LOC baseline |
| Project Context | Brownfield — migrating existing Java codebase; Java tests define baseline behaviour |

## Success Criteria

### User Success

- The CLI starts and runs with a single command: `uv run bank`
- All 4 operations work identically to the Java version: create account, deposit, withdraw, display accounts
- Invalid input produces specific, user-readable error messages (e.g., *"Balance must be 0 or greater"*, not *"Error: balance cannot be negative"*)
- Account number format is validated at creation time — malformed numbers are rejected with guidance
- Deposit and withdrawal amounts are validated (must be positive)

### Technical Success

- All Java test scenarios have passing pytest equivalents
- `ruff check src/` passes with zero PEP 8 violations
- `mypy --strict src/` passes with zero type errors
- Every business rule is expressed as a Pydantic field constraint or validator — no manual `if` guards in constructors
- Test coverage ≥ 90% (`pytest --cov`)

### Migration Success

- The Python codebase reproduces 100% of the Java application's behaviour
- Validation gaps identified in the technical research are closed: deposit amount, account number format, owner name
- Architecture improvements are implemented: Repository pattern, typed exception hierarchy, Protocol-based service interface

### Measurable Outcomes

| Metric | Target |
|--------|--------|
| Java test parity | 4/4 scenarios pass in pytest |
| New validation rules added | ≥ 3 (deposit amount, account number format, owner name) |
| PEP 8 violations | 0 |
| Type check errors | 0 |
| Test coverage | ≥ 90% |

## Product Scope

### MVP — Minimum Viable Product

- Python 3.12+ console application reproducing all Java BMS functionality
- `Account` as Pydantic `BaseModel` with declarative field validation
- `BankService` Protocol + `BankServiceImpl` with `JsonFileAccountRepository`
- `typer`-based CLI with argument commands: `create-account`, `deposit`, `withdraw`, `show-accounts`
- Typed exception hierarchy with specific error messages
- Validation of amounts (positive), account number format, and owner name (non-empty)
- Full pytest suite mirroring Java tests + new validation tests
- PEP 8 compliant, type-checked, linted codebase

## User Journeys

### Persona: Sam, the CLI Operator

Sam is a developer or technical user who runs the Bank Management System from a terminal. They expect a modern CLI with discoverable commands, type-safe arguments, and clear feedback when something goes wrong.

---

### Journey 1: First-Time Setup and Discovery

**Opening:** Sam clones the project and runs `uv sync`. Then `uv run bank --help` — the CLI prints all available commands with descriptions. No guessing, no reading source code. Setup is instant — no JDK, no classpath, no build step.

**Action:** Sam runs `uv run bank create-account 001 Ali 500.0`. The application confirms: *"Account created successfully."*

**Resolution:** Sam runs `uv run bank show-accounts` and sees the new account listed with formatted balance. They trust the system is working.

---

### Journey 2: Normal Banking Operations

**Opening:** Sam has an existing account and wants to manage funds.

**Action:** Sam runs `uv run bank deposit 001 500.0`, then `uv run bank withdraw 001 200.0`. Each command confirms with a clear success message.

**Resolution:** `uv run bank show-accounts` shows the updated balance reflecting both operations. The workflow is fast, predictable, and scriptable.

---

### Journey 3: Error Recovery — Where Pydantic Shines

**Opening:** Sam makes a series of input mistakes — this is where the Python rewrite diverges most from the Java original.

**Scenario A — Overdraft attempt:**
`uv run bank withdraw 001 800.0` — The Java version prints: `Error: Insufficient balance`. The Python version prints: *"Insufficient balance: cannot withdraw 800.00 from account 001 (current balance: 300.00)."*

**Scenario B — Invalid account number format:**
`uv run bank create-account abc Ali 500.0` — The Java version silently accepts it. The Python version rejects it: *"Account number must be a numeric string (e.g., '001')."*

**Scenario C — Negative deposit:**
`uv run bank deposit 001 -50` — The Java version adds it (the balance decreases — a bug). The Python version rejects it: *"Deposit amount must be greater than 0."*

**Resolution:** Sam never has to guess what went wrong. Each error message names the field, states the rule, and implies the fix. This is the core UX improvement over the Java version.

---

### Journey 4: Help and Discoverability

Sam forgets the command syntax. `uv run bank deposit --help` prints:
```
Usage: bank deposit [OPTIONS] ACCOUNT_NUMBER AMOUNT

  Deposit funds into an account.

Arguments:
  ACCOUNT_NUMBER  [required]
  AMOUNT          [required]
```

Every command is self-documenting — no manual needed.

---

### Journey Requirements Summary

| Journey | Capabilities revealed |
|---------|----------------------|
| 1 — Setup & Discovery | Project runs via `uv run bank`; `--help` on all commands; account creation with field validation |
| 2 — Banking ops | Deposit and withdrawal with balance updates; account listing with formatted output |
| 3 — Error recovery | Pydantic field-level error messages; account number format validation; amount positivity validation; overdraft protection with context |
| 4 — Help | Built-in `--help` on every command via `typer` |

## CLI Tool Specific Requirements

### Command Structure

The CLI uses `typer` with a flat command hierarchy — no nested subcommands. Each banking operation is a top-level command.

| Command | Arguments | Description |
|---------|-----------|-------------|
| `create-account` | `ACCOUNT_NUMBER`, `OWNER`, `INITIAL_BALANCE` | Create a new account with validated fields |
| `deposit` | `ACCOUNT_NUMBER`, `AMOUNT` | Deposit a positive amount into an existing account |
| `withdraw` | `ACCOUNT_NUMBER`, `AMOUNT` | Withdraw from an account if sufficient balance |
| `show-accounts` | *(none)* | List all accounts with formatted balances |

All arguments are positional and required (no optional flags beyond `--help`). `typer` derives argument types from Python type hints — `AMOUNT` is `float`, `ACCOUNT_NUMBER` and `OWNER` are `str`.

### Output Formats

The CLI outputs plain text to stdout. No JSON or structured output mode is planned for MVP.

- **Success messages:** Short confirmation sentences (e.g., *"Account created successfully."*)
- **Error messages:** Pydantic validation errors are caught and reformatted into user-readable sentences. The raw Pydantic `ValidationError` detail is never shown to the user.
- **Account listing:** Tabular text output with columns: account number, owner, balance (formatted to 2 decimal places)

### Persistence

Each `typer` command runs as a separate process, so state must survive between invocations. The CLI persists accounts to a local `accounts.json` file in the working directory.

- The file is created automatically on the first write (no setup step required)
- Each command reads the file at start, performs its operation, and writes back
- Pydantic's built-in serialisation (`.model_dump()` / `.model_validate()`) handles the JSON round-trip — no extra dependencies
- To reset all data, the user deletes the file manually (`rm accounts.json`)
- No account deletion or file management commands are in MVP scope

The Repository pattern abstracts this: `JsonFileAccountRepository` implements the same interface as an in-memory store would. The service layer has no knowledge of how or where data is persisted.

### Configuration

No configuration files, environment variables, or dotfiles. The JSON data file location is implicit (current working directory). This is intentional for a demo-scope CLI.

### Scripting Support

Commands are stateless and argument-driven, which makes them scriptable:

```bash
uv run bank create-account 001 Ali 500.0
uv run bank deposit 001 200.0
uv run bank show-accounts
```

Because state persists to `accounts.json`, commands compose naturally in shell scripts. Shell completion is available via `typer`'s built-in `--install-completion`.

## Functional Requirements

Each FR traces to one or more User Journeys (J1–J4) and is testable via pytest.

### FR-1: Account Creation (J1, J3)

Users can create a bank account by providing an account number, owner name, and initial balance. The system validates all three fields at creation time:

- Account number must be a non-empty numeric string (e.g., `"001"`)
- Owner name must be a non-empty string
- Initial balance must be ≥ 0

If any field is invalid, the command fails with a field-specific error message naming the rule that was violated. If the account number already exists, the command fails with a duplicate account error.

**Acceptance criteria:** Account is persisted to `accounts.json` and visible in `show-accounts`. Invalid inputs are rejected with specific messages — one per violated rule.

### FR-2: Deposit (J2, J3)

Users can deposit funds into an existing account. The deposit amount must be strictly greater than 0. The system rejects zero and negative amounts with a specific error message.

**Acceptance criteria:** Account balance increases by exactly the deposited amount. Updated balance is persisted immediately. Non-existent account numbers produce an "account not found" error.

### FR-3: Withdrawal (J2, J3)

Users can withdraw funds from an existing account. The withdrawal amount must be strictly greater than 0 and must not exceed the current balance. The system rejects overdrafts with a message that includes the current balance and the attempted amount.

**Acceptance criteria:** Account balance decreases by exactly the withdrawn amount. Updated balance is persisted immediately. Overdraft attempts are rejected without modifying the balance.

### FR-4: Account Listing (J1, J2)

Users can display all existing accounts. Each account is shown with its account number, owner name, and balance formatted to 2 decimal places. If no accounts exist, the output states that explicitly.

**Acceptance criteria:** All persisted accounts are listed. Output is human-readable tabular text.

### FR-5: Command Discoverability (J1, J4)

Every command supports `--help`, displaying its name, description, and required arguments. The root command (`uv run bank --help`) lists all available commands.

**Acceptance criteria:** `--help` output includes argument names and types for each command.

### FR-6: Data Persistence Across Commands (J1, J2)

Accounts created or modified by one command invocation are available to subsequent commands. Data is stored in `accounts.json` in the working directory. The file is created on first write and read on every command start.

**Acceptance criteria:** A `create-account` followed by a separate `show-accounts` invocation displays the created account.

### Functional Requirements Traceability

| FR | J1 Setup | J2 Banking | J3 Errors | J4 Help |
|----|----------|------------|-----------|---------|
| FR-1 Account Creation | x | | x | |
| FR-2 Deposit | | x | x | |
| FR-3 Withdrawal | | x | x | |
| FR-4 Account Listing | x | x | | |
| FR-5 Discoverability | x | | | x |
| FR-6 Persistence | x | x | | |

## Non-Functional Requirements

### NFR-1: Code Quality — PEP 8 Compliance

`ruff check src/` produces zero violations. All Python source files follow PEP 8 naming conventions (`snake_case` functions, `PascalCase` classes).

**Measurement:** `ruff check src/` exit code 0.

### NFR-2: Type Safety

`mypy --strict src/` produces zero type errors. All function signatures include type annotations. Pydantic models provide runtime type enforcement.

**Measurement:** `mypy --strict src/` exit code 0.

### NFR-3: Test Coverage

Test suite covers ≥ 90% of source lines. Every FR has at least one corresponding pytest test. All Java test scenarios have pytest equivalents.

**Measurement:** `pytest --cov` reports ≥ 90% coverage.

### NFR-4: Validation Architecture

Every business rule (balance ≥ 0, amount > 0, account number format, owner non-empty) is expressed as a Pydantic `Field` constraint or `@field_validator` — not as a manual `if` guard in application code.

**Measurement:** No `if` guards for input validation exist outside Pydantic model definitions.

### NFR-5: Error Message Quality

All user-facing error messages name the specific field, state the violated rule, and imply the corrective action. Raw Pydantic `ValidationError` tracebacks are never shown to the user.

**Measurement:** Each error scenario in the test suite asserts on the message content, not just the exception type.

### NFR-6: Zero-Setup Experience

The project runs with `uv sync` followed by `uv run bank <command>`. No manual dependency installation, virtual environment creation, or configuration steps required.

**Measurement:** A clean clone + `uv sync` + `uv run bank --help` succeeds on Python 3.12+.