class BankError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class AccountNotFoundError(BankError):
    pass


class DuplicateAccountError(BankError):
    pass


class InsufficientBalanceError(BankError):
    pass


class InvalidAmountError(BankError):
    pass
