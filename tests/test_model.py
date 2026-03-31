"""Unit tests for the Account Pydantic model (Story 1.3)."""

import pytest
from pydantic import ValidationError

from bank.model import Account


class TestAccountValidCreation:
    """AC 1: Valid inputs produce a successful Account instance."""

    def test_valid_account_created_successfully(self) -> None:
        account = Account(account_number="001", owner="Ali", balance=500.0)
        assert account.account_number == "001"
        assert account.owner == "Ali"
        assert account.balance == 500.0

    def test_valid_account_with_zero_balance(self) -> None:
        account = Account(account_number="123", owner="Bob", balance=0.0)
        assert account.balance == 0.0

    def test_valid_account_balance_int_coerced_to_float(self) -> None:
        account = Account(account_number="999", owner="Carol", balance=100)
        assert account.balance == 100.0
        assert isinstance(account.balance, float)


class TestAccountNumberValidation:
    """AC 2: Non-numeric account number raises ValidationError."""

    def test_non_numeric_account_number_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Account(account_number="abc", owner="Ali", balance=0.0)
        errors = exc_info.value.errors()
        messages = [str(e["msg"]) for e in errors]
        assert any("numeric" in msg.lower() for msg in messages)

    def test_alphanumeric_account_number_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError):
            Account(account_number="12a", owner="Ali", balance=0.0)

    def test_empty_account_number_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError):
            Account(account_number="", owner="Ali", balance=0.0)


class TestOwnerValidation:
    """AC 3: Empty owner string raises ValidationError for the owner field."""

    def test_empty_owner_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Account(account_number="001", owner="", balance=0.0)
        errors = exc_info.value.errors()
        field_names = [e["loc"][0] for e in errors]
        assert "owner" in field_names


class TestBalanceValidation:
    """AC 4: Balance < 0 raises ValidationError for the balance field."""

    def test_negative_balance_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Account(account_number="001", owner="Ali", balance=-1.0)
        errors = exc_info.value.errors()
        field_names = [e["loc"][0] for e in errors]
        assert "balance" in field_names

    def test_large_negative_balance_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError):
            Account(account_number="001", owner="Ali", balance=-999.99)


class TestModelDump:
    """AC 5: model_dump() returns exact expected shape with no aliases."""

    def test_model_dump_returns_correct_keys(self) -> None:
        account = Account(account_number="001", owner="Ali", balance=500.0)
        dumped = account.model_dump()
        assert set(dumped.keys()) == {"account_number", "owner", "balance"}

    def test_model_dump_returns_correct_values(self) -> None:
        account = Account(account_number="001", owner="Ali", balance=500.0)
        dumped = account.model_dump()
        assert dumped == {"account_number": "001", "owner": "Ali", "balance": 500.0}

    def test_model_dump_no_extra_keys(self) -> None:
        account = Account(account_number="001", owner="Ali", balance=500.0)
        dumped = account.model_dump()
        assert len(dumped) == 3


class TestModelRoundTrip:
    """AC 6: model_validate(model_dump()) round-trips without data loss."""

    def test_round_trip_preserves_data(self) -> None:
        original = Account(account_number="001", owner="Ali", balance=500.0)
        restored = Account.model_validate(original.model_dump())
        assert restored.account_number == original.account_number
        assert restored.owner == original.owner
        assert restored.balance == original.balance

    def test_round_trip_equality(self) -> None:
        original = Account(account_number="042", owner="Beatrice", balance=1234.56)
        restored = Account.model_validate(original.model_dump())
        assert restored == original
