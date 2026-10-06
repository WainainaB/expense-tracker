from datetime import date as date_type
from pydantic import BaseModel, Field, field_validator

class ExpenseBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0, description="Must be greater than 0")
    category: str = Field(..., min_length=1, max_length=50)
    date: date_type
    paid_by: str = Field(..., min_length=1, max_length=100)

    @field_validator("description", "category", "paid_by")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be blank")
        return v.strip()

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    description: str | None = Field(None, min_length=1, max_length=200)
    amount: float | None = Field(None, gt=0)
    category: str | None = Field(None, min_length=1, max_length=50)
    date: date_type | None = None
    paid_by: str | None = Field(None, min_length=1, max_length=100)

class Expense(ExpenseBase):
    id: int