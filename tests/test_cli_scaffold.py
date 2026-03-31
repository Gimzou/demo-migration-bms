"""Tests for CLI scaffold — Story 1.5.

Verifies:
- _get_service() returns a BankServiceImpl wired with JsonFileAccountRepository
- All four commands are registered with correct signatures
- Composition root wires correct concrete types
"""

import inspect


def test_get_service_function_exists() -> None:
    """cli module must expose _get_service factory function."""
    import bank.cli as cli_mod

    assert hasattr(cli_mod, "_get_service"), "_get_service not found in bank.cli"


def test_get_service_returns_bank_service_impl() -> None:
    """_get_service() must return a BankServiceImpl instance."""
    from bank.cli import _get_service
    from bank.service import BankServiceImpl

    svc = _get_service()
    assert isinstance(svc, BankServiceImpl)


def test_get_service_wires_json_file_repository() -> None:
    """_get_service() must inject a JsonFileAccountRepository."""
    from bank.cli import _get_service
    from bank.repository import JsonFileAccountRepository

    svc = _get_service()
    assert isinstance(svc._repository, JsonFileAccountRepository)


def test_cli_imports_bank_service_impl() -> None:
    """cli.py must import BankServiceImpl (composition root)."""
    import bank.cli as cli_mod

    assert hasattr(cli_mod, "BankServiceImpl")


def test_cli_imports_json_file_account_repository() -> None:
    """cli.py must import JsonFileAccountRepository (composition root)."""
    import bank.cli as cli_mod

    assert hasattr(cli_mod, "JsonFileAccountRepository")


def test_create_account_signature() -> None:
    """create_account must accept account_number, owner, initial_balance."""
    from bank.cli import create_account

    sig = inspect.signature(create_account)
    params = list(sig.parameters.keys())
    assert "account_number" in params
    assert "owner" in params
    assert "initial_balance" in params


def test_deposit_signature() -> None:
    """deposit must accept account_number and amount."""
    from bank.cli import deposit

    sig = inspect.signature(deposit)
    params = list(sig.parameters.keys())
    assert "account_number" in params
    assert "amount" in params


def test_withdraw_signature() -> None:
    """withdraw must accept account_number and amount."""
    from bank.cli import withdraw

    sig = inspect.signature(withdraw)
    params = list(sig.parameters.keys())
    assert "account_number" in params
    assert "amount" in params


def test_show_accounts_signature() -> None:
    """show_accounts must accept no arguments."""
    from bank.cli import show_accounts

    sig = inspect.signature(show_accounts)
    assert len(sig.parameters) == 0
