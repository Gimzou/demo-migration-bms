from typing import Protocol

from bank.exceptions import (  # noqa: F401
    AccountNotFoundError,
    DuplicateAccountError,
    InsufficientBalanceError,
    InvalidAmountError,
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
        raise NotImplementedError

    def deposit(self, account_number: str, amount: float) -> Account:
        raise NotImplementedError

    def withdraw(self, account_number: str, amount: float) -> Account:
        raise NotImplementedError

    def get_all_accounts(self) -> list[Account]:
        raise NotImplementedError
