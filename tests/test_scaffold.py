"""Tests for the project scaffold — verifies all module stubs are importable
and have the expected public API defined in Story 1.1."""

import importlib
import inspect


def test_exceptions_importable() -> None:
    mod = importlib.import_module("bank.exceptions")
    assert hasattr(mod, "BankError")
    assert hasattr(mod, "AccountNotFoundError")
    assert hasattr(mod, "DuplicateAccountError")
    assert hasattr(mod, "InsufficientBalanceError")
    assert hasattr(mod, "InvalidAmountError")


def test_exceptions_hierarchy() -> None:
    from bank.exceptions import (
        AccountNotFoundError,
        BankError,
        DuplicateAccountError,
        InsufficientBalanceError,
        InvalidAmountError,
    )

    assert issubclass(AccountNotFoundError, BankError)
    assert issubclass(DuplicateAccountError, BankError)
    assert issubclass(InsufficientBalanceError, BankError)
    assert issubclass(InvalidAmountError, BankError)
    assert issubclass(BankError, Exception)


def test_model_importable() -> None:
    from bank.model import Account
    from pydantic import BaseModel

    assert issubclass(Account, BaseModel)
    fields = Account.model_fields
    assert "account_number" in fields
    assert "owner" in fields
    assert "balance" in fields


def test_repository_protocol_importable() -> None:
    mod = importlib.import_module("bank.repository")
    assert hasattr(mod, "AccountRepository")
    repo = mod.AccountRepository
    assert hasattr(repo, "find_all")
    assert hasattr(repo, "find_by_id")
    assert hasattr(repo, "save")
    assert hasattr(repo, "exists")


def test_service_protocol_importable() -> None:
    mod = importlib.import_module("bank.service")
    assert hasattr(mod, "BankService")
    svc = mod.BankService
    assert hasattr(svc, "create_account")
    assert hasattr(svc, "deposit")
    assert hasattr(svc, "withdraw")
    assert hasattr(svc, "get_all_accounts")


def test_cli_app_importable() -> None:
    """CLI module must export 'app' as a typer.Typer instance."""
    import typer

    from bank.cli import app

    assert isinstance(app, typer.Typer)


def test_cli_has_four_commands() -> None:
    """CLI must expose exactly the four commands from the architecture spec.

    Typer derives command names from callback function names (underscores → dashes)
    at invocation time, so cmd.name is None in registered_commands; we derive the
    expected CLI name ourselves via the same convention.
    """
    from bank.cli import app

    # Derive CLI names: typer converts snake_case callback names to kebab-case
    cli_names = set()
    for cmd in app.registered_commands:
        name = cmd.name
        if name is None and cmd.callback is not None:
            name = cmd.callback.__name__.replace("_", "-")
        if name is not None:
            cli_names.add(name)

    assert "create-account" in cli_names
    assert "deposit" in cli_names
    assert "withdraw" in cli_names
    assert "show-accounts" in cli_names


def test_repository_not_concrete_class() -> None:
    """AccountRepository should be a Protocol, not a concrete implementation."""
    from typing import runtime_checkable

    from bank.repository import AccountRepository

    # Protocol classes are not abstract base classes with enforcement —
    # just verify it's declared as a Protocol (has _is_protocol marker)
    assert getattr(AccountRepository, "_is_protocol", False)


def test_service_not_concrete_class() -> None:
    """BankService should be a Protocol, not a concrete implementation."""
    from bank.service import BankService

    assert getattr(BankService, "_is_protocol", False)
