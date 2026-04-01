"""Tests for the withdraw CLI command and BankServiceImpl.withdraw() — Story 2.3."""

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from bank.cli import app
from bank.exceptions import (
    AccountNotFoundError,
    InsufficientBalanceError,
    InvalidAmountError,
)
from bank.model import Account

runner = CliRunner()


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------


def test_withdraw_success_prints_message() -> None:
    """withdraw prints 'Withdrawal successful.' on success (AC 1)."""
    updated = Account(account_number="001", owner="Alice", balance=300.0)
    with patch("bank.cli._get_service") as mock_svc_factory:
        mock_svc = MagicMock()
        mock_svc.withdraw.return_value = updated
        mock_svc_factory.return_value = mock_svc

        result = runner.invoke(app, ["withdraw", "001", "200.0"])

    assert result.exit_code == 0
    assert "Withdrawal successful." in result.output


def test_withdraw_success_calls_service_with_correct_args() -> None:
    """withdraw passes account_number and amount to service (AC 1)."""
    updated = Account(account_number="001", owner="Alice", balance=300.0)
    with patch("bank.cli._get_service") as mock_svc_factory:
        mock_svc = MagicMock()
        mock_svc.withdraw.return_value = updated
        mock_svc_factory.return_value = mock_svc

        runner.invoke(app, ["withdraw", "001", "200.0"])

        mock_svc.withdraw.assert_called_once_with("001", 200.0)


def test_withdraw_insufficient_balance_shows_error_and_exits_1() -> None:
    """withdraw shows InsufficientBalanceError message and exits with code 1 (AC 2)."""
    error_msg = (
        "Insufficient balance: cannot withdraw 800.00 from account 001 "
        "(current balance: 300.00)."
    )
    with patch("bank.cli._get_service") as mock_svc_factory:
        mock_svc = MagicMock()
        mock_svc.withdraw.side_effect = InsufficientBalanceError(error_msg)
        mock_svc_factory.return_value = mock_svc

        result = runner.invoke(app, ["withdraw", "001", "800.0"])

    assert result.exit_code == 1
    assert "800.00" in result.output
    assert "300.00" in result.output


def test_withdraw_account_not_found_shows_error_and_exits_1() -> None:
    """withdraw shows AccountNotFoundError message and exits with code 1 (AC 3)."""
    error_msg = "Account not found: no account with number 999."
    with patch("bank.cli._get_service") as mock_svc_factory:
        mock_svc = MagicMock()
        mock_svc.withdraw.side_effect = AccountNotFoundError(error_msg)
        mock_svc_factory.return_value = mock_svc

        result = runner.invoke(app, ["withdraw", "999", "100.0"])

    assert result.exit_code == 1
    assert "999" in result.output


def test_withdraw_zero_amount_shows_error_and_exits_1() -> None:
    """withdraw shows InvalidAmountError message and exits with code 1 (AC 4)."""
    error_msg = "Invalid amount: withdrawal amount must be greater than 0, got 0.00."
    with patch("bank.cli._get_service") as mock_svc_factory:
        mock_svc = MagicMock()
        mock_svc.withdraw.side_effect = InvalidAmountError(error_msg)
        mock_svc_factory.return_value = mock_svc

        result = runner.invoke(app, ["withdraw", "001", "0.0"])

    assert result.exit_code == 1
    assert "0.00" in result.output
