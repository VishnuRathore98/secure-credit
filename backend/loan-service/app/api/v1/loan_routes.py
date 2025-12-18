from fastapi import APIRouter, HTTPException, Depends
from app.schemas.loan_schemas import LoanResponse, LoanCreateRequest
from app.models.loan_models import Loan
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import json
from uuid import UUID
from sqlalchemy.future import select

router = APIRouter()


@router.post("/loans", response_model=LoanResponse)
async def create_loan(request: LoanCreateRequest, db: AsyncSession = Depends(get_db)):
    loan = Loan(
        customer_id=request.customer_id,
        loan_amount=request.loan_amount,
        approved_amount=None,
        loan_tenure_months=request.loan_tenure_months,
        loan_type=request.loan_type,
        status="SUBMITTED",
    )
    db.add(loan)
    await db.commit()
    await db.refresh(loan)

    event = {
        "event_type": "LoanApplicationSubmitted",
        "payload": {
            "loan_id": str(loan.id),
            "customer_id": str(loan.customer_id),
            "loan_amount": float(loan.loan_amount),
        },
    }

    rabbitmq_channel.basic_publish(
        exchange="",
        routing_key="loan.submitted",
        body=json.dumps(event).encode(),
    )

    return LoanResponse(
        loan_id=loan.id,
        status=loan.status,
        loan_amount=float(loan.loan_amount),
        approved_amount=loan.approved_amount,
    )


@router.get("/loans/{loan_id}", response_model=LoanResponse)
async def get_loan(loan_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Loan).where(Loan.id == loan_id))
    loan = result.scalar_one_or_none()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return LoanResponse(
        loan_id=loan.id,
        status=loan.status,
        loan_amount=float(loan.loan_amount),
        approved_amount=loan.approved_amount,
    )
