"""Unit tests for the bank exception hierarchy — Story 1.2."""

import pytest

from bank.exceptions import (
    AccountNotFoundError,
    BankError,
    DuplicateAccountError,
    InsufficientBalanceError,
    InvalidAmountError,
)

_ALL_SUBTYPES = [
    AccountNotFoundError,
    DuplicateAccountError,
    InsufficientBalanceError,
    InvalidAmountError,
]


class TestBankErrorBase:
    def test_bank_error_is_exception_subclass(self) -> None:
        assert issubclass(BankError, Exception)

    def test_bank_error_accepts_message(self) -> None:
        exc = BankError("something went wrong")
        assert str(exc) == "something went wrong"

    def test_bank_error_message_attribute(self) -> None:
        exc = BankError("base error")
        assert exc.message == "base error"


class TestSubtypeInheritance:
    @pytest.mark.parametrize("exc_class", _ALL_SUBTYPES)
    def test_is_subclass_of_bank_error(self, exc_class: type[BankError]) -> None:
        assert issubclass(exc_class, BankError)

    @pytest.mark.parametrize("exc_class", _ALL_SUBTYPES)
    def test_isinstance_of_bank_error(self, exc_class: type[BankError]) -> None:
        exc = exc_class("test message")
        assert isinstance(exc, BankError)

    @pytest.mark.parametrize("exc_class", _ALL_SUBTYPES)
    def test_str_returns_message(self, exc_class: type[BankError]) -> None:
        msg = f"error from {exc_class.__name__}"
        exc = exc_class(msg)
        assert str(exc) == msg

    @pytest.mark.parametrize("exc_class", _ALL_SUBTYPES)
    def test_message_attribute(self, exc_class: type[BankError]) -> None:
        msg = f"attribute test for {exc_class.__name__}"
        exc = exc_class(msg)
        assert exc.message == msg


class TestSpecificExceptions:
    def test_account_not_found_error(self) -> None:
        exc = AccountNotFoundError("Account ACC-001 not found.")
        assert isinstance(exc, BankError)
        assert str(exc) == "Account ACC-001 not found."

    def test_duplicate_account_error(self) -> None:
        exc = DuplicateAccountError("Account ACC-001 already exists.")
        assert isinstance(exc, BankError)
        assert str(exc) == "Account ACC-001 already exists."

    def test_insufficient_balance_error(self) -> None:
        exc = InsufficientBalanceError(
            "Insufficient balance: cannot withdraw 100.00 from account ACC-001 "
            "(current balance: 50.00)."
        )
        assert isinstance(exc, BankError)
        assert "Insufficient balance" in str(exc)

    def test_invalid_amount_error(self) -> None:
        exc = InvalidAmountError("Amount must be greater than 0.")
        assert isinstance(exc, BankError)
        assert str(exc) == "Amount must be greater than 0."
