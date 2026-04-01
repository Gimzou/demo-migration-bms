from typing import Protocol

from bank.exceptions import (
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
        if amount <= 0:
            raise InvalidAmountError(
                "Invalid amount: deposit amount must be greater than 0,"
                f" got {amount:.2f}."
            )
        account = self._repository.find_by_id(account_number)
        if account is None:
            raise AccountNotFoundError(
                f"Account not found: no account with number {account_number}."
            )
        updated = account.model_copy(update={"balance": account.balance + amount})
        self._repository.save(updated)
        return updated

    def withdraw(self, account_number: str, amount: float) -> Account:
        if amount <= 0:
            raise InvalidAmountError(
                "Invalid amount: withdrawal amount must be greater than 0,"
                f" got {amount:.2f}."
            )
        account = self._repository.find_by_id(account_number)
        if account is None:
            raise AccountNotFoundError(
                f"Account not found: no account with number {account_number}."
            )
        if amount > account.balance:
            raise InsufficientBalanceError(
                f"Insufficient balance: cannot withdraw {amount:.2f} from account "
                f"{account_number} (current balance: {account.balance:.2f})."
            )
        updated = account.model_copy(update={"balance": account.balance - amount})
        self._repository.save(updated)
        return updated

    def get_all_accounts(self) -> list[Account]:
        return self._repository.find_all()
