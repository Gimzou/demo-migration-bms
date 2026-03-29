---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments:
  - specs/prd.md
  - docs/BankManagementSystem/README.md
workflowType: 'architecture'
project_name: 'demo-migration-bms'
user_name: 'Arnould'
date: '2026-03-29'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
6 FRs covering account CRUD (create, list), banking transactions (deposit, withdraw), CLI discoverability (--help), and cross-invocation data persistence. All operations are synchronous, single-user, and argument-driven. The account model is the only domain entity.

**Non-Functional Requirements:**
6 NFRs that function as hard gates, not guidelines:
- Code quality: `ruff check src/` = 0 violations
- Type safety: `mypy --strict src/` = 0 errors
- Test coverage: `pytest --cov` ≥ 90%
- Validation architecture: all business rules in Pydantic, none in application code
- Error messages: field-specific, rule-stating, action-implying — no raw tracebacks
- Zero-setup: `uv sync` + `uv run bank` on a clean clone

**Scale & Complexity:**

- Primary domain: CLI tool (fintech demo scope)
- Complexity level: Low
- Estimated architectural components: 5 (model, service protocol + impl, repository, exception hierarchy, CLI entry point)

### Technical Constraints & Dependencies

- Python 3.12+ (required for modern type syntax: `type` aliases, `TypeVar` defaults, `override`)
- Pydantic v2 for model validation and JSON serialization
- `typer` for CLI argument parsing and `--help` generation
- `uv` as the sole package/environment manager
- JSON file persistence in working directory (no database)
- No configuration files, environment variables, or dotfiles
- Entry-point configuration in `pyproject.toml` (`[project.scripts]`) is required for the `uv run bank` zero-setup experience (NFR-6)

### Cross-Cutting Concerns Identified

1. **Field-level validation (Pydantic):** Account number format, owner non-empty, balance ≥ 0, amount > 0. These are declared on the `Account` model and enforced at construction time. No other layer duplicates these checks.
2. **Entity-level business rules (Service):** Duplicate account detection and overdraft protection require repository state and cannot be expressed as Pydantic validators. The service layer owns these rules and raises typed exceptions when they're violated.
3. **CLI as error-translation boundary:** The CLI layer contains zero business logic. Its sole role beyond argument parsing is catching `ValidationError` (from Pydantic) and domain exceptions (from the service layer) and formatting them into user-readable sentences. This is the only place where error message text is authored.
4. **Repository encapsulates persistence lifecycle:** The read-modify-write cycle is internal to `JsonFileAccountRepository`, not a cross-cutting concern. The service layer interacts through a clean interface (`find_all`, `find_by_id`, `save`) without knowing about the JSON file.
5. **Serialization round-trip:** `Account.model_dump()` → JSON file → `Account.model_validate()`. Every field must survive this cycle without data loss or type coercion surprises.

## Starter Template Evaluation

### Primary Technology Domain

Python CLI tool, based on project requirements analysis. No web, mobile, or API surface.

### Starter Options Considered

| Option | Approach | Verdict |
|--------|----------|---------|
| `uv init --app --package` | Minimal uv scaffold with src/ layout and entry point | **Selected** — right-sized for a low-complexity CLI |
| Cookiecutter/Copier templates | Pre-configured CI, docs, Docker, linting | Rejected — too much scaffolding to strip for ~200 LOC |
| Manual pyproject.toml | Write everything from scratch | Viable but `uv init` does the same thing faster |

### Selected Starter: `uv init --app --package`

**Rationale:** The project is a low-complexity CLI with 5 architectural components. A minimal scaffold that provides the `src/` layout and `[project.scripts]` entry point is the right foundation — anything heavier creates removal work rather than saving effort.

**Initialization Command:**

```bash
uv init --app --package bank --python ">=3.12"
```

**Architectural Decisions Provided by Starter:**

**Language & Runtime:**
- Python 3.12+ with `src/` package layout
- `uv_build` as build backend

**Dependencies (added post-init):**
- `pydantic >=2.12,<3` — model validation and JSON serialization
- `typer >=0.24,<1` — CLI argument parsing and --help generation

**Dev Tooling (added post-init):**
- `pytest >=9,<10` + `pytest-cov` — test runner with coverage
- `ruff >=0.15` — linting and formatting (PEP 8 gate)
- `mypy >=1.19` — strict type checking gate

**Code Organization:**
- `src/bank/` — application package
- `tests/` — test suite
- Entry point: `bank = "bank.cli:app"`

**Note:** Project initialization using this command should be the first implementation story.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
All 4 decisions below are critical — an implementing agent cannot write consistent code without them.

**Deferred Decisions (Post-MVP):**
- Authentication & security: out of scope
- Infrastructure & deployment: local CLI, no deployment target
- Frontend architecture: N/A
- API design: N/A

### Data Architecture

**Persistence:** JSON file in working directory (`accounts.json`). Created on first write, no setup step. Pydantic's `model_dump()` / `model_validate()` handle serialization — no extra libraries.

**Repository Interface:** `Protocol`-based. `JsonFileAccountRepository` implements the protocol without inheriting from it. The service layer depends on the protocol, not the concrete class.

**Validation Strategy:** Two-tier.
- Tier 1 (field-level): Pydantic `Field` constraints and `@field_validator` on `Account`. Enforced at model construction time.
- Tier 2 (entity-level): Business rules requiring repository state (duplicate detection, overdraft) and operation-level validation (amount > 0) live in `BankServiceImpl`. Raised as typed domain exceptions.

### Exception Hierarchy

Flat, one level deep. Each exception maps 1:1 to a business rule violation:

```
BankError (base)
├── AccountNotFoundError
├── DuplicateAccountError
├── InsufficientBalanceError
└── InvalidAmountError
```

All inherit from a common `BankError` base so the CLI can catch the entire domain in one handler if needed.

### Module Structure

Flat, one module per concern inside `src/bank/`:

```
src/bank/
├── __init__.py
├── cli.py          # typer app + error formatting
├── model.py        # Account BaseModel
├── service.py      # BankService Protocol + BankServiceImpl
├── repository.py   # AccountRepository Protocol + JsonFileAccountRepository
└── exceptions.py   # BankError hierarchy
```

No sub-packages. Each file has a single, obvious responsibility.

### Error Handling Flow

`ValidationError` from Pydantic is caught at the CLI boundary (`cli.py`), not wrapped in domain exceptions. The CLI extracts the first error message from `e.errors()[0]["msg"]` and prints it as a user-readable sentence.

Domain exceptions (`BankError` subtypes) raised by the service layer are also caught at the CLI boundary and formatted into user-readable messages.

The CLI is the only place where error message text is authored. No other layer formats output.

### Decision Impact Analysis

**Implementation Sequence:**
1. `exceptions.py` — no dependencies
2. `model.py` — depends on nothing (Pydantic self-contained)
3. `repository.py` — depends on `model`
4. `service.py` — depends on `model`, `repository` (protocol), `exceptions`
5. `cli.py` — depends on `service`, `exceptions`, catches `ValidationError`

**Cross-Component Dependencies:**
- `model.py` is imported by `repository.py`, `service.py`
- `exceptions.py` is imported by `service.py`, `cli.py`
- `repository.py` protocol is imported by `service.py`
- `cli.py` imports everything — it is the composition root

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:**
6 areas where AI agents could make incompatible choices.

### Naming & Format Patterns

**Python Naming:**
- PEP 8 throughout: `snake_case` for functions, methods, variables, modules; `PascalCase` for classes and type aliases
- Enforced by `ruff check` — no separate convention needed

**JSON Persistence Format:**
- Field names match Python attribute names exactly (Pydantic default)
- No aliases, no `by_alias=True`, no `serialization_alias`
- Example: `{"account_number": "001", "owner": "Ali", "balance": 500.0}`

**Error Message Format:**
- Domain exceptions: `"{What failed}: {context with values}."`
  - Example: `"Insufficient balance: cannot withdraw 800.00 from account 001 (current balance: 300.00)."`
- No `"Error:"` prefix in exception messages — the CLI layer decides presentation
- Amounts formatted to 2 decimal places
- Pydantic validation messages: use built-in wording; CLI strips `"Value error, "` prefix when displaying

**CLI Output Format:**
- `show-accounts`: plain-text table with aligned columns (Account Number, Owner, Balance)
- Empty state: `"No accounts found."`
- Mutation success: single sentence — `"Account created successfully."`, `"Deposit successful."`, `"Withdrawal successful."`

### Structure Patterns

**Test Organization:**
```
tests/
├── __init__.py
├── test_model.py
├── test_service.py
├── test_repository.py
├── test_cli.py
└── conftest.py
```
- One test file per source module, prefixed with `test_`
- Shared fixtures (sample accounts, temp JSON files) in `conftest.py`

**Import Style:**
- Always absolute imports from package root: `from bank.model import Account`
- No relative imports

### Interface Patterns

**Repository Protocol:**
```python
class AccountRepository(Protocol):
    def find_all(self) -> list[Account]: ...
    def find_by_id(self, account_number: str) -> Account | None: ...
    def save(self, account: Account) -> None: ...
    def exists(self, account_number: str) -> bool: ...
```
- `find_by_id` returns `None` if not found (no exception at repository level)
- Service layer raises `AccountNotFoundError` when needed

**BankService Protocol:**
```python
class BankService(Protocol):
    def create_account(self, account_number: str, owner: str, initial_balance: float) -> Account: ...
    def deposit(self, account_number: str, amount: float) -> Account: ...
    def withdraw(self, account_number: str, amount: float) -> Account: ...
    def get_all_accounts(self) -> list[Account]: ...
```
- All mutation methods return the updated `Account`
- Validation and business rule exceptions raised before any state change

### Enforcement Guidelines

**All AI Agents MUST:**
- Run `ruff check src/` and `mypy --strict src/` before considering a story complete
- Follow the Protocol signatures exactly — no renaming, no reordering parameters
- Use the error message format defined above — no ad-hoc wording
- Place tests in the corresponding `test_*.py` file

**Anti-Patterns:**
- ❌ `from .model import Account` (relative import)
- ❌ `model_dump(by_alias=True)` (alias serialization)
- ❌ `raise AccountNotFoundError(...)` inside repository (repository returns None)
- ❌ `print("Error: ...")` in service layer (only CLI formats output)

## Project Structure & Boundaries

### Complete Project Directory Structure

```
bank/
├── .gitignore
├── .python-version
├── README.md
├── pyproject.toml
├── src/
│   └── bank/
│       ├── __init__.py
│       ├── cli.py
│       ├── model.py
│       ├── service.py
│       ├── repository.py
│       └── exceptions.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_model.py
    ├── test_service.py
    ├── test_repository.py
    └── test_cli.py
```

13 files total. No additional directories, CI configs, or tooling beyond what `uv init --app --package` and `pyproject.toml` provide.

### Requirements to Structure Mapping

| FR | Primary Module | Supporting Modules |
|----|----------------|-------------------|
| FR-1 Account Creation | `service.py` | `model.py`, `repository.py`, `cli.py` |
| FR-2 Deposit | `service.py` | `model.py`, `repository.py`, `cli.py` |
| FR-3 Withdrawal | `service.py` | `model.py`, `repository.py`, `exceptions.py`, `cli.py` |
| FR-4 Account Listing | `service.py` | `repository.py`, `cli.py` |
| FR-5 Discoverability | `cli.py` | typer built-in |
| FR-6 Persistence | `repository.py` | `model.py` |

### Architectural Boundaries

**Boundary 1 — CLI → Service (composition root):**
`cli.py` instantiates `BankServiceImpl` with `JsonFileAccountRepository` and calls service methods. The only place where concrete implementations are wired together. Direction is one-way: CLI calls service; service never calls CLI.

**Boundary 2 — Service → Repository (Protocol interface):**
`service.py` depends on the `AccountRepository` Protocol. Repository returns data or `None`; service decides whether to raise domain exceptions.

**Boundary 3 — Model ↔ JSON (serialization boundary):**
`repository.py` uses `Account.model_dump()` / `Account.model_validate()` for JSON round-trip. The file structure is determined entirely by the Pydantic model.

### Data Flow

Every CLI command follows the same pattern:

```
User input → typer parses args → cli.py calls service method
  → service calls repository (read) → repository reads accounts.json
  → Account.model_validate() per entry → service applies business logic
  → service calls repository (write) → Account.model_dump() per entry
  → repository writes accounts.json → service returns Account
  → cli.py prints success message
```

Error flow:
- Pydantic `ValidationError` → caught by `cli.py` → user message
- `BankError` subtypes → caught by `cli.py` → user message
- typer `BadParameter` → handled by typer → usage error