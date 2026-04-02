"""Shared pytest fixtures for the bank test suite (Story 3.1)."""

import pytest
from pathlib import Path

from bank.model import Account
from bank.repository import JsonFileAccountRepository


@pytest.fixture
def sample_account() -> Account:
    return Account(account_number="001", owner="Ali", balance=500.0)


@pytest.fixture
def json_file(tmp_path: Path) -> Path:
    return tmp_path / "accounts.json"


@pytest.fixture
def populated_repo(json_file: Path, sample_account: Account) -> JsonFileAccountRepository:
    repo = JsonFileAccountRepository(json_file)
    repo.save(sample_account)
    return repo
