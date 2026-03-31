import json
from pathlib import Path

import pytest

from bank.model import Account
from bank.repository import JsonFileAccountRepository


def test_find_all_returns_empty_when_file_missing(tmp_path: Path) -> None:
    repo = JsonFileAccountRepository(tmp_path / "accounts.json")
    assert repo.find_all() == []


def test_save_and_find_by_id_roundtrip(tmp_path: Path) -> None:
    repo = JsonFileAccountRepository(tmp_path / "accounts.json")
    account = Account(account_number="001", owner="Ali", balance=500.0)
    repo.save(account)
    result = repo.find_by_id("001")
    assert result == account


def test_find_by_id_returns_none_for_unknown(tmp_path: Path) -> None:
    repo = JsonFileAccountRepository(tmp_path / "accounts.json")
    assert repo.find_by_id("999") is None


def test_exists_returns_true_for_known_id(tmp_path: Path) -> None:
    repo = JsonFileAccountRepository(tmp_path / "accounts.json")
    repo.save(Account(account_number="001", owner="Ali", balance=500.0))
    assert repo.exists("001") is True


def test_exists_returns_false_for_unknown_id(tmp_path: Path) -> None:
    repo = JsonFileAccountRepository(tmp_path / "accounts.json")
    assert repo.exists("999") is False


def test_persistence_across_instances(tmp_path: Path) -> None:
    file = tmp_path / "accounts.json"
    repo1 = JsonFileAccountRepository(file)
    repo1.save(Account(account_number="001", owner="Ali", balance=500.0))
    repo2 = JsonFileAccountRepository(file)
    assert repo2.find_by_id("001") is not None


def test_json_field_names_match_python_attributes(tmp_path: Path) -> None:
    file = tmp_path / "accounts.json"
    repo = JsonFileAccountRepository(file)
    repo.save(Account(account_number="001", owner="Ali", balance=500.0))
    raw = json.loads(file.read_text())
    assert list(raw[0].keys()) == ["account_number", "owner", "balance"]


def test_save_updates_existing_account(tmp_path: Path) -> None:
    file = tmp_path / "accounts.json"
    repo = JsonFileAccountRepository(file)
    repo.save(Account(account_number="001", owner="Ali", balance=500.0))
    repo.save(Account(account_number="001", owner="Ali", balance=750.0))
    accounts = repo.find_all()
    assert len(accounts) == 1
    assert accounts[0].balance == 750.0
