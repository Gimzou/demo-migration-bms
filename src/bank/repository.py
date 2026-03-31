import json
from pathlib import Path
from typing import Protocol

from bank.model import Account

DEFAULT_FILE = Path("accounts.json")


class AccountRepository(Protocol):
    def find_all(self) -> list[Account]: ...

    def find_by_id(self, account_number: str) -> Account | None: ...

    def save(self, account: Account) -> None: ...

    def exists(self, account_number: str) -> bool: ...


class JsonFileAccountRepository:
    def __init__(self, file_path: Path = DEFAULT_FILE) -> None:
        self._file_path = file_path

    def find_all(self) -> list[Account]:
        if not self._file_path.exists():
            return []
        with self._file_path.open() as f:
            data: list[dict[str, object]] = json.load(f)
        return [Account.model_validate(item) for item in data]

    def find_by_id(self, account_number: str) -> Account | None:
        for account in self.find_all():
            if account.account_number == account_number:
                return account
        return None

    def exists(self, account_number: str) -> bool:
        return self.find_by_id(account_number) is not None

    def save(self, account: Account) -> None:
        accounts = self.find_all()
        updated = False
        for i, existing in enumerate(accounts):
            if existing.account_number == account.account_number:
                accounts[i] = account
                updated = True
                break
        if not updated:
            accounts.append(account)
        with self._file_path.open("w") as f:
            json.dump([a.model_dump() for a in accounts], f, indent=2)
