from typing import Protocol

from bank.exceptions import (
    AccountNotFoundError,  # noqa: F401  (used in Stories 2.2–2.3)
    DuplicateAccountError,
    InsufficientBalanceError,  # noqa: F401  (used in Story 2.3)
    InvalidAmountError,  # noqa: F401  (used in Stories 2.2–2.3)
)
from bank.model import Account
from bank.repository import AccountRepository


class BankService(Protocol):
    def create_account(
        self, account_number: str, owner: str, initial_balance: float
    ) -> Account: ...

    def deposit(self, account_number: str, amount: float) -> Account: ...

    def withdraw(self, account_number: str, amount: float) -> Account: ...

    def get_all_accounts(self) -> list[Account]: ...


class BankServiceImpl:
    def __init__(self, repository: AccountRepository) -> None:
        self._repository = repository

    def create_account(
        self, account_number: str, owner: str, initial_balance: float
    ) -> Account:
        if self._repository.exists(account_number):
            raise DuplicateAccountError(
                f"Duplicate account: account number {account_number} already exists."
            )
        account = Account(
            account_number=account_number,
            owner=owner,
            balance=initial_balance,
        )
        self._repository.save(account)
        return account

    def deposit(self, account_number: str, amount: float) -> Account:
        raise NotImplementedError

    def withdraw(self, account_number: str, amount: float) -> Account:
        raise NotImplementedError

    def get_all_accounts(self) -> list[Account]:
        raise NotImplementedError
