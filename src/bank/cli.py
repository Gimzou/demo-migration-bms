import typer
from pydantic import ValidationError  # noqa: F401

from bank.exceptions import BankError  # noqa: F401
from bank.repository import JsonFileAccountRepository
from bank.service import BankServiceImpl

app = typer.Typer()


def _get_service() -> BankServiceImpl:
    return BankServiceImpl(JsonFileAccountRepository())


@app.command()
def create_account(account_number: str, owner: str, initial_balance: float) -> None:
    """Create a new bank account."""


@app.command()
def deposit(account_number: str, amount: float) -> None:
    """Deposit funds into an account."""


@app.command()
def withdraw(account_number: str, amount: float) -> None:
    """Withdraw funds from an account."""


@app.command()
def show_accounts() -> None:
    """Display all accounts."""
