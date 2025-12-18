from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class LoanCreateRequest(BaseModel):
    customer_id: UUID
    loan_amount: float
    loan_tenure_months: int
    loan_type: str


class LoanResponse(BaseModel):
    loan_id: UUID
    status: str
    loan_amount: float
    approved_amount: Optional[float] = None
