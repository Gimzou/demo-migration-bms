from pydantic import BaseModel, Field, field_validator


class Account(BaseModel):
    account_number: str = Field(min_length=1)
    owner: str = Field(min_length=1)
    balance: float = Field(ge=0.0)

    @field_validator("account_number")
    @classmethod
    def account_number_must_be_numeric(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("Account number must be a numeric string (e.g., '001').")
        return v
