---
stepsCompleted: [step-01-init, step-02-discovery, step-02b-vision, step-02c-executive-summary, step-03-success]
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

The Bank Management System (BMS) is a Python rewrite of an existing Java console banking application. The rewrite replaces imperative, scattered validation with declarative, framework-enforced business rules using Pydantic v2. The end-users are operators of the CLI who interact with a numbered-menu interface to create accounts, deposit, withdraw, and view balances.

The Java predecessor is functionally complete but architecturally weak on validation: business rules (`balance ≥ 0`, `amount ≤ balance`) are buried in constructor guards with no validation on deposit amounts, account number format, or owner name. A single catch-all exception handler obscures all error distinctions. The Python rewrite corrects these gaps, improves user-facing error feedback, and delivers a codebase that is easier to set up, run, and extend.

### What Makes This Special

Pydantic v2 is not introduced as a convenience layer — it is the architectural foundation. By defining `Account` as a `pydantic.BaseModel` with `Field` constraints and `@field_validator` rules, business rules become the schema: declared once, enforced everywhere, visible to any reader of the code, and verifiable by the test suite. This shifts the BMS from a system where correctness is the developer's responsibility to one where correctness is enforced by the framework.

The result is a user experience improvement at two levels: the application raises specific, meaningful errors (not generic exceptions), and the codebase communicates its own rules without requiring a developer to trace through imperative logic.

## Project Classification

| Attribute | Value |
|-----------|-------|
| Project Type | CLI tool — interactive console, numbered menu, `input()` / `match/case` |
| Domain | Banking (fintech demo scope — no compliance, auth, or persistence requirements) |
| Complexity | Low — 4 operations, in-memory storage, ~200 LOC baseline |
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
- `BankService` Protocol + `BankServiceImpl` with `InMemoryAccountRepository`
- `BankingConsole` with `input()` + `match/case` menu loop
- Typed exception hierarchy with specific error messages
- Validation of amounts (positive), account number format, and owner name (non-empty)
- Full pytest suite mirroring Java tests + new validation tests
- PEP 8 compliant, type-checked, linted codebase