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


def test_bank_service_impl_deposit_raises() -> None:
    """deposit raises NotImplementedError (stub until Epic 2)."""
    from unittest.mock import MagicMock

    from bank.service import BankServiceImpl

    svc = BankServiceImpl(MagicMock())
    with pytest.raises(NotImplementedError):
        svc.deposit("ACC001", 50.0)


def test_bank_service_impl_withdraw_raises() -> None:
    """withdraw raises NotImplementedError (stub until Epic 2)."""
    from unittest.mock import MagicMock

    from bank.service import BankServiceImpl

    svc = BankServiceImpl(MagicMock())
    with pytest.raises(NotImplementedError):
        svc.withdraw("ACC001", 25.0)


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
