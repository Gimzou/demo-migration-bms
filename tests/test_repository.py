"""Tests for JsonFileAccountRepository — Story 3.2 (updated to use conftest fixtures)."""

import json
from pathlib import Path

from bank.model import Account
from bank.repository import JsonFileAccountRepository


def test_find_all_returns_empty_when_file_missing(json_file: Path) -> None:
    repo = JsonFileAccountRepository(json_file)
    assert repo.find_all() == []


def test_save_and_find_by_id_roundtrip(json_file: Path, sample_account: Account) -> None:
    repo = JsonFileAccountRepository(json_file)
    repo.save(sample_account)
    result = repo.find_by_id(sample_account.account_number)
    assert result == sample_account


def test_find_by_id_returns_none_for_unknown(json_file: Path) -> None:
    repo = JsonFileAccountRepository(json_file)
    assert repo.find_by_id("999") is None


def test_exists_returns_true_for_known_id(json_file: Path, sample_account: Account) -> None:
    repo = JsonFileAccountRepository(json_file)
    repo.save(sample_account)
    assert repo.exists(sample_account.account_number) is True


def test_exists_returns_false_for_unknown_id(json_file: Path) -> None:
    repo = JsonFileAccountRepository(json_file)
    assert repo.exists("999") is False


def test_persistence_across_instances(json_file: Path, sample_account: Account) -> None:
    repo1 = JsonFileAccountRepository(json_file)
    repo1.save(sample_account)
    repo2 = JsonFileAccountRepository(json_file)
    assert repo2.find_by_id(sample_account.account_number) is not None


def test_json_field_names_match_python_attributes(json_file: Path, sample_account: Account) -> None:
    repo = JsonFileAccountRepository(json_file)
    repo.save(sample_account)
    raw = json.loads(json_file.read_text())
    assert list(raw[0].keys()) == ["account_number", "owner", "balance"]


def test_save_updates_existing_account(json_file: Path, sample_account: Account) -> None:
    repo = JsonFileAccountRepository(json_file)
    repo.save(sample_account)
    updated = sample_account.model_copy(update={"balance": 750.0})
    repo.save(updated)
    accounts = repo.find_all()
    assert len(accounts) == 1
    assert accounts[0].balance == 750.0
