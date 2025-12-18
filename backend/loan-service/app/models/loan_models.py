from sqlalchemy import Column, DateTime, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.core.database import Base
from datetime import datetime, timezone
from uuid import uuid4


class Loan(Base):
    __tablename__ = "loans"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_id = Column(PGUUID(as_uuid=True), nullable=False)
    loan_amount = Column(Numeric, nullable=False)
    approved_amount = Column(Numeric, nullable=True)
    loan_tenure_months = Column(Integer, nullable=False)
    loan_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
