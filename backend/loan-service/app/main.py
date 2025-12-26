from fastapi import FastAPI
from app.api.v1 import loan_routes
from app.core.database import Base, engine
from contextlib import asynccontextmanager
from app.core.messages import start_credit_decision_consumer
import threading
import logging

decision_logger = logging.get_logger("loan-decision-consumer")

@asynccontextmanager
async def lifespan(app: FastAPI):
    threading.Thread(
        target=start_credit_decision_consumer,
        daemon=True,
    ).start()
    
    yield

    # put in closing thread logic


app = FastAPI(title="Loan Service", lifespan=lifespan)


Base.metadata.create_all(bind=engine)



@app.get("/health")
def health_check():
    return {"status": "UP"}


app.include_router(loan_routes.router)
