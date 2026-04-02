"""CLI integration tests for bank commands — success paths and error-message assertions."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from bank.cli import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# Task 1 — Success-path tests
# ---------------------------------------------------------------------------


def test_create_account_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["create-account", "001", "Ali", "500.0"])
    assert result.exit_code == 0
    assert "Account created successfully." in result.output


def test_deposit_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["create-account", "001", "Ali", "500.0"])
    result = runner.invoke(app, ["deposit", "001", "200.0"])
    assert result.exit_code == 0
    assert "Deposit successful." in result.output


def test_withdraw_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["create-account", "001", "Ali", "500.0"])
    result = runner.invoke(app, ["withdraw", "001", "100.0"])
    assert result.exit_code == 0
    assert "Withdrawal successful." in result.output


def test_show_accounts_with_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["create-account", "001", "Ali", "500.0"])
    result = runner.invoke(app, ["show-accounts"])
    assert result.exit_code == 0
    assert "Account Number" in result.output
    assert "Owner" in result.output
    assert "Balance" in result.output
    assert "500.00" in result.output  # 2 decimal places


def test_show_accounts_empty_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["show-accounts"])
    assert result.exit_code == 0
    assert "No accounts found." in result.output


# ---------------------------------------------------------------------------
# Task 2 — Error-path tests with content assertions
# ---------------------------------------------------------------------------


def test_create_account_duplicate_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["create-account", "001", "Ali", "500.0"])
    result = runner.invoke(app, ["create-account", "001", "Bob", "100.0"])
    assert result.exit_code != 0
    assert "001" in result.output  # account number referenced in message
    assert "ValidationError" not in result.output  # no raw traceback
    assert "Traceback" not in result.output


def test_create_account_non_numeric_account_number(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["create-account", "abc", "Ali", "500.0"])
    assert result.exit_code != 0
    assert "numeric" in result.output.lower()
    assert "ValidationError" not in result.output  # reformatted, never raw
    assert "Traceback" not in result.output


def test_withdraw_overdraft_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["create-account", "001", "Ali", "300.0"])
    result = runner.invoke(app, ["withdraw", "001", "800.0"])
    assert result.exit_code != 0
    assert "800.00" in result.output  # attempted amount
    assert "300.00" in result.output  # current balance


def test_deposit_account_not_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["deposit", "999", "100.0"])
    assert result.exit_code != 0
    assert "999" in result.output  # account number referenced in not-found message


def test_withdraw_account_not_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["withdraw", "999", "100.0"])
    assert result.exit_code != 0
    assert "999" in result.output  # account number referenced in not-found message
