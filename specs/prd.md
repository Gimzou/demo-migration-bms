---
stepsCompleted: [step-01-init, step-02-discovery, step-02b-vision, step-02c-executive-summary]
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