from typing import Annotated

import typer
from pydantic import ValidationError

from bank.exceptions import BankError
from bank.repository import JsonFileAccountRepository
from bank.service import BankServiceImpl

app = typer.Typer()


def _get_service() -> BankServiceImpl:
    return BankServiceImpl(JsonFileAccountRepository())


@app.command(context_settings={"allow_interspersed_args": False})
def create_account(
    account_number: str,
    owner: str,
    initial_balance: Annotated[float, typer.Argument()],
) -> None:
    """Create a new bank account."""
    try:
        _get_service().create_account(account_number, owner, initial_balance)
        typer.echo("Account created successfully.")
    except ValidationError as exc:
        msg = exc.errors()[0]["msg"].removeprefix("Value error, ")
        typer.echo(msg)
        raise typer.Exit(1)
    except BankError as exc:
        typer.echo(str(exc))
        raise typer.Exit(1)


@app.command()
def deposit(account_number: str, amount: float) -> None:
    """Deposit funds into an account."""
    try:
        _get_service().deposit(account_number, amount)
        typer.echo("Deposit successful.")
    except BankError as exc:
        typer.echo(str(exc))
        raise typer.Exit(1)


@app.command()
def withdraw(account_number: str, amount: float) -> None:
    """Withdraw funds from an account."""
    try:
        _get_service().withdraw(account_number, amount)
        typer.echo("Withdrawal successful.")
    except BankError as exc:
        typer.echo(str(exc))
        raise typer.Exit(1)


@app.command()
def show_accounts() -> None:
    """Display all accounts."""
    accounts = _get_service().get_all_accounts()
    if not accounts:
        typer.echo("No accounts found.")
        return

    headers = ("Account Number", "Owner", "Balance")
    rows = [
        (a.account_number, a.owner, f"{a.balance:.2f}")
        for a in accounts
    ]

    col_widths = [
        max(len(headers[i]), max(len(row[i]) for row in rows))
        for i in range(3)
    ]

    def fmt_row(cols: tuple[str, str, str]) -> str:
        return (
            f"{cols[0]:<{col_widths[0]}}  "
            f"{cols[1]:<{col_widths[1]}}  "
            f"{cols[2]:>{col_widths[2]}}"
        )

    typer.echo(fmt_row(headers))
    for row in rows:
        typer.echo(fmt_row(row))
