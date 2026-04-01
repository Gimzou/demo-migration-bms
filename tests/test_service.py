"""Tests for BankServiceImpl stub — Story 1.5."""

import pytest


def test_bank_service_impl_importable() -> None:
    """BankServiceImpl must be importable from bank.service."""
    from bank.service import BankServiceImpl  # noqa: F401


def test_bank_service_impl_accepts_repository() -> None:
    """BankServiceImpl must accept an AccountRepository in its constructor."""
    from unittest.mock import MagicMock

    from bank.service import BankServiceImpl

    mock_repo = MagicMock()
    svc = BankServiceImpl(mock_repo)
    assert svc is not None


def test_bank_service_impl_create_account_persists() -> None:
    """create_account saves a valid Account via the repository and returns it."""
    from unittest.mock import MagicMock

    from bank.model import Account
    from bank.service import BankServiceImpl

    mock_repo = MagicMock()
    mock_repo.exists.return_value = False
    svc = BankServiceImpl(mock_repo)
    account = svc.create_account("001", "Alice", 500.0)

    mock_repo.exists.assert_called_once_with("001")
    mock_repo.save.assert_called_once_with(account)
    assert isinstance(account, Account)
    assert account.account_number == "001"
    assert account.owner == "Alice"
    assert account.balance == 500.0


def test_bank_service_impl_create_account_duplicate_raises() -> None:
    """create_account raises DuplicateAccountError when account already exists."""
    from unittest.mock import MagicMock

    from bank.exceptions import DuplicateAccountError
    from bank.service import BankServiceImpl

    mock_repo = MagicMock()
    mock_repo.exists.return_value = True
    svc = BankServiceImpl(mock_repo)
    with pytest.raises(DuplicateAccountError):
        svc.create_account("001", "Alice", 100.0)


def test_bank_service_impl_create_account_invalid_number() -> None:
    """create_account raises ValidationError for non-numeric account_number."""
    from unittest.mock import MagicMock

    from pydantic import ValidationError

    from bank.service import BankServiceImpl

    mock_repo = MagicMock()
    mock_repo.exists.return_value = False
    svc = BankServiceImpl(mock_repo)
    with pytest.raises(ValidationError):
        svc.create_account("abc", "Alice", 100.0)


def test_bank_service_impl_create_account_negative_balance() -> None:
    """create_account raises ValidationError for negative initial_balance."""
    from unittest.mock import MagicMock

    from pydantic import ValidationError

    from bank.service import BankServiceImpl

    mock_repo = MagicMock()
    mock_repo.exists.return_value = False
    svc = BankServiceImpl(mock_repo)
    with pytest.raises(ValidationError):
        svc.create_account("001", "Alice", -100.0)


def test_bank_service_impl_deposit_success() -> None:
    """deposit updates balance and persists updated account."""
    from unittest.mock import MagicMock

    from bank.model import Account
    from bank.service import BankServiceImpl

    mock_repo = MagicMock()
    existing = Account(account_number="001", owner="Alice", balance=500.0)
    mock_repo.find_by_id.return_value = existing
    svc = BankServiceImpl(mock_repo)
    result = svc.deposit("001", 200.0)

    mock_repo.find_by_id.assert_called_once_with("001")
    mock_repo.save.assert_called_once()
    assert result.balance == 700.0
    assert result.account_number == "001"


def test_bank_service_impl_deposit_account_not_found() -> None:
    """deposit raises AccountNotFoundError when account does not exist."""
    from unittest.mock import MagicMock

    from bank.exceptions import AccountNotFoundError
    from bank.service import BankServiceImpl

    mock_repo = MagicMock()
    mock_repo.find_by_id.return_value = None
    svc = BankServiceImpl(mock_repo)
    with pytest.raises(AccountNotFoundError):
        svc.deposit("999", 100.0)


def test_bank_service_impl_deposit_zero_amount() -> None:
    """deposit raises InvalidAmountError for zero amount."""
    from unittest.mock import MagicMock

    from bank.exceptions import InvalidAmountError
    from bank.service import BankServiceImpl

    svc = BankServiceImpl(MagicMock())
    with pytest.raises(InvalidAmountError):
        svc.deposit("001", 0.0)


def test_bank_service_impl_deposit_negative_amount() -> None:
    """deposit raises InvalidAmountError for negative amount."""
    from unittest.mock import MagicMock

    from bank.exceptions import InvalidAmountError
    from bank.service import BankServiceImpl

    svc = BankServiceImpl(MagicMock())
    with pytest.raises(InvalidAmountError):
        svc.deposit("001", -50.0)


def test_bank_service_impl_deposit_balance_not_modified_on_invalid_amount() -> None:
    """deposit does not call save when amount is invalid."""
    from unittest.mock import MagicMock

    from bank.exceptions import InvalidAmountError
    from bank.service import BankServiceImpl

    mock_repo = MagicMock()
    svc = BankServiceImpl(mock_repo)
    with pytest.raises(InvalidAmountError):
        svc.deposit("001", 0.0)
    mock_repo.save.assert_not_called()


def test_bank_service_impl_withdraw_success() -> None:
    """withdraw deducts amount from balance, saves updated account, and returns it."""
    from unittest.mock import MagicMock

    from bank.model import Account
    from bank.service import BankServiceImpl

    mock_repo = MagicMock()
    existing = Account(account_number="001", owner="Alice", balance=500.0)
    mock_repo.find_by_id.return_value = existing
    svc = BankServiceImpl(mock_repo)
    result = svc.withdraw("001", 200.0)

    mock_repo.find_by_id.assert_called_once_with("001")
    mock_repo.save.assert_called_once()
    assert result.balance == 300.0
    assert result.account_number == "001"


def test_bank_service_impl_withdraw_zero_amount_raises() -> None:
    """withdraw raises InvalidAmountError for zero amount without touching repo."""
    from unittest.mock import MagicMock

    from bank.exceptions import InvalidAmountError
    from bank.service import BankServiceImpl

    mock_repo = MagicMock()
    svc = BankServiceImpl(mock_repo)
    with pytest.raises(InvalidAmountError) as exc_info:
        svc.withdraw("001", 0.0)
    assert "0.00" in str(exc_info.value)
    mock_repo.find_by_id.assert_not_called()
    mock_repo.save.assert_not_called()


def test_bank_service_impl_withdraw_negative_amount_raises() -> None:
    """withdraw raises InvalidAmountError for negative amount without touching repo."""
    from unittest.mock import MagicMock

    from bank.exceptions import InvalidAmountError
    from bank.service import BankServiceImpl

    mock_repo = MagicMock()
    svc = BankServiceImpl(mock_repo)
    with pytest.raises(InvalidAmountError):
        svc.withdraw("001", -50.0)
    mock_repo.save.assert_not_called()


def test_bank_service_impl_withdraw_account_not_found_raises() -> None:
    """withdraw raises AccountNotFoundError when account does not exist."""
    from unittest.mock import MagicMock

    from bank.exceptions import AccountNotFoundError
    from bank.service import BankServiceImpl

    mock_repo = MagicMock()
    mock_repo.find_by_id.return_value = None
    svc = BankServiceImpl(mock_repo)
    with pytest.raises(AccountNotFoundError) as exc_info:
        svc.withdraw("999", 100.0)
    assert "999" in str(exc_info.value)
    mock_repo.save.assert_not_called()


def test_bank_service_impl_withdraw_insufficient_balance_raises() -> None:
    """withdraw raises InsufficientBalanceError with both amounts in message."""
    from unittest.mock import MagicMock

    from bank.exceptions import InsufficientBalanceError
    from bank.model import Account
    from bank.service import BankServiceImpl

    mock_repo = MagicMock()
    existing = Account(account_number="001", owner="Alice", balance=300.0)
    mock_repo.find_by_id.return_value = existing
    svc = BankServiceImpl(mock_repo)
    with pytest.raises(InsufficientBalanceError) as exc_info:
        svc.withdraw("001", 800.0)
    error_msg = str(exc_info.value)
    assert "800.00" in error_msg
    assert "300.00" in error_msg
    mock_repo.save.assert_not_called()


def test_bank_service_impl_withdraw_does_not_mutate_on_overdraft() -> None:
    """withdraw does not call save when overdraft guard fires."""
    from unittest.mock import MagicMock

    from bank.model import Account
    from bank.service import BankServiceImpl

    mock_repo = MagicMock()
    existing = Account(account_number="001", owner="Alice", balance=300.0)
    mock_repo.find_by_id.return_value = existing
    svc = BankServiceImpl(mock_repo)
    try:
        svc.withdraw("001", 800.0)
    except Exception:
        pass
    mock_repo.save.assert_not_called()


def test_bank_service_impl_withdraw_exact_balance_succeeds() -> None:
    """withdraw with amount equal to balance succeeds (balance reaches 0)."""
    from unittest.mock import MagicMock

    from bank.model import Account
    from bank.service import BankServiceImpl

    mock_repo = MagicMock()
    existing = Account(account_number="001", owner="Alice", balance=300.0)
    mock_repo.find_by_id.return_value = existing
    svc = BankServiceImpl(mock_repo)
    result = svc.withdraw("001", 300.0)

    assert result.balance == 0.0
    mock_repo.save.assert_called_once()


def test_bank_service_impl_get_all_accounts_delegates_to_repository() -> None:
    """get_all_accounts delegates directly to repository.find_all()."""
    from unittest.mock import MagicMock

    from bank.model import Account
    from bank.service import BankServiceImpl

    mock_repo = MagicMock()
    expected = [
        Account(account_number="001", owner="Alice", balance=500.0),
        Account(account_number="002", owner="Bob", balance=1000.0),
    ]
    mock_repo.find_all.return_value = expected
    svc = BankServiceImpl(mock_repo)
    result = svc.get_all_accounts()

    mock_repo.find_all.assert_called_once_with()
    assert result == expected


def test_bank_service_impl_stores_repository() -> None:
    """BankServiceImpl stores the injected repository as _repository."""
    from unittest.mock import MagicMock

    from bank.service import BankServiceImpl

    mock_repo = MagicMock()
    svc = BankServiceImpl(mock_repo)
    assert svc._repository is mock_repo
