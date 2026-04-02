"""Real service tests for BankServiceImpl — Story 3.2.

All tests inject a real JsonFileAccountRepository backed by the `json_file` fixture
from conftest.py, providing authentic Pydantic round-trip + persistence coverage
without mocking.
"""

from pathlib import Path

import pytest
from pydantic import ValidationError

from bank.exceptions import (
    AccountNotFoundError,
    DuplicateAccountError,
    InsufficientBalanceError,
    InvalidAmountError,
)
from bank.model import Account
from bank.repository import JsonFileAccountRepository
from bank.service import BankServiceImpl


@pytest.fixture
def svc(json_file: Path) -> BankServiceImpl:
    return BankServiceImpl(JsonFileAccountRepository(json_file))


# ---------------------------------------------------------------------------
# create_account
# ---------------------------------------------------------------------------


def test_create_account_success(svc: BankServiceImpl, sample_account: Account) -> None:
    """create_account returns Account and persists it.

    # Java scenario equivalent
    """
    result = svc.create_account(
        sample_account.account_number, sample_account.owner, sample_account.balance
    )
    assert isinstance(result, Account)
    assert result.account_number == "001"
    assert result.owner == "Ali"
    assert result.balance == 500.0
    # verify persistence
    accounts = svc.get_all_accounts()
    assert len(accounts) == 1
    assert accounts[0] == result


def test_create_account_duplicate_raises(svc: BankServiceImpl, sample_account: Account) -> None:
    """create_account raises DuplicateAccountError when account already exists."""
    svc.create_account(sample_account.account_number, sample_account.owner, sample_account.balance)
    with pytest.raises(DuplicateAccountError) as exc_info:
        svc.create_account(sample_account.account_number, sample_account.owner, sample_account.balance)
    assert "001" in exc_info.value.message


def test_create_account_invalid_account_number(svc: BankServiceImpl) -> None:
    """Non-numeric account_number propagates Pydantic ValidationError (not BankError)."""
    with pytest.raises(ValidationError):
        svc.create_account("abc", "Ali", 500.0)


# ---------------------------------------------------------------------------
# deposit
# ---------------------------------------------------------------------------


def test_deposit_success(svc: BankServiceImpl, sample_account: Account) -> None:
    """deposit increases balance and returns updated Account.

    # Java scenario equivalent
    """
    svc.create_account(sample_account.account_number, sample_account.owner, sample_account.balance)
    result = svc.deposit("001", 200.0)
    assert isinstance(result, Account)
    assert result.balance == 700.0  # 500 + 200
    # verify persistence
    accounts = svc.get_all_accounts()
    assert accounts[0].balance == 700.0


def test_deposit_invalid_amount_zero(svc: BankServiceImpl, sample_account: Account) -> None:
    """deposit raises InvalidAmountError for zero amount."""
    svc.create_account(sample_account.account_number, sample_account.owner, sample_account.balance)
    with pytest.raises(InvalidAmountError) as exc_info:
        svc.deposit("001", 0.0)
    assert "0.00" in exc_info.value.message
    # balance unchanged
    accounts = svc.get_all_accounts()
    assert accounts[0].balance == 500.0


def test_deposit_invalid_amount_negative(svc: BankServiceImpl, sample_account: Account) -> None:
    """deposit raises InvalidAmountError for negative amount."""
    svc.create_account(sample_account.account_number, sample_account.owner, sample_account.balance)
    with pytest.raises(InvalidAmountError) as exc_info:
        svc.deposit("001", -50.0)
    assert "-50.00" in exc_info.value.message
    # balance unchanged
    accounts = svc.get_all_accounts()
    assert accounts[0].balance == 500.0


def test_deposit_account_not_found(svc: BankServiceImpl) -> None:
    """deposit raises AccountNotFoundError for an unknown account."""
    with pytest.raises(AccountNotFoundError) as exc_info:
        svc.deposit("999", 100.0)
    assert "999" in exc_info.value.message


# ---------------------------------------------------------------------------
# withdraw
# ---------------------------------------------------------------------------


def test_withdraw_success(svc: BankServiceImpl, sample_account: Account) -> None:
    """withdraw decreases balance and returns updated Account.

    # Java scenario equivalent
    """
    svc.create_account(sample_account.account_number, sample_account.owner, sample_account.balance)
    result = svc.withdraw("001", 200.0)
    assert isinstance(result, Account)
    assert result.balance == 300.0  # 500 - 200
    # verify persistence
    accounts = svc.get_all_accounts()
    assert accounts[0].balance == 300.0


def test_withdraw_overdraft_raises(svc: BankServiceImpl, sample_account: Account) -> None:
    """withdraw raises InsufficientBalanceError with both amounts in message.

    # Java scenario equivalent
    """
    svc.create_account(sample_account.account_number, sample_account.owner, sample_account.balance)
    with pytest.raises(InsufficientBalanceError) as exc_info:
        svc.withdraw("001", 800.0)
    assert "800.00" in exc_info.value.message
    assert "500.00" in exc_info.value.message  # current balance
    # balance must be unchanged
    accounts = svc.get_all_accounts()
    assert accounts[0].balance == 500.0


def test_withdraw_invalid_amount_zero(svc: BankServiceImpl, sample_account: Account) -> None:
    """withdraw raises InvalidAmountError for zero amount."""
    svc.create_account(sample_account.account_number, sample_account.owner, sample_account.balance)
    with pytest.raises(InvalidAmountError) as exc_info:
        svc.withdraw("001", 0.0)
    assert "0.00" in exc_info.value.message
    # balance unchanged
    accounts = svc.get_all_accounts()
    assert accounts[0].balance == 500.0


def test_withdraw_invalid_amount_negative(svc: BankServiceImpl, sample_account: Account) -> None:
    """withdraw raises InvalidAmountError for negative amount."""
    svc.create_account(sample_account.account_number, sample_account.owner, sample_account.balance)
    with pytest.raises(InvalidAmountError):
        svc.withdraw("001", -50.0)
    # balance unchanged
    accounts = svc.get_all_accounts()
    assert accounts[0].balance == 500.0


def test_withdraw_account_not_found(svc: BankServiceImpl) -> None:
    """withdraw raises AccountNotFoundError for an unknown account."""
    with pytest.raises(AccountNotFoundError) as exc_info:
        svc.withdraw("999", 100.0)
    assert "999" in exc_info.value.message
