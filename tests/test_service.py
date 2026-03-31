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


def test_bank_service_impl_create_account_raises() -> None:
    """create_account raises NotImplementedError (stub until Epic 2)."""
    from unittest.mock import MagicMock

    from bank.service import BankServiceImpl

    svc = BankServiceImpl(MagicMock())
    with pytest.raises(NotImplementedError):
        svc.create_account("ACC001", "Alice", 100.0)


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


def test_bank_service_impl_get_all_accounts_raises() -> None:
    """get_all_accounts raises NotImplementedError (stub until Epic 2)."""
    from unittest.mock import MagicMock

    from bank.service import BankServiceImpl

    svc = BankServiceImpl(MagicMock())
    with pytest.raises(NotImplementedError):
        svc.get_all_accounts()


def test_bank_service_impl_stores_repository() -> None:
    """BankServiceImpl stores the injected repository as _repository."""
    from unittest.mock import MagicMock

    from bank.service import BankServiceImpl

    mock_repo = MagicMock()
    svc = BankServiceImpl(mock_repo)
    assert svc._repository is mock_repo
