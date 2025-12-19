from fastapi import FastAPI
from app.api.v1 import loan_routes
import pika

from app.core.database import Base

app = FastAPI(title="Loan Service")


@app.on_event("startup")
def startup():
    global rabbitmq_connection, rabbitmq_channel
    with engine.begin() as conn:
        conn.run_sync(Base.metadata.create_all)
    params = pika.URLParameters(RABBITMQ_URL)
    rabbitmq_connection = pika.BlockingConnection(params)
    rabbitmq_channel = rabbitmq_connection.channel()

Base.metadata.create_all()

@app.get("/health")
def health_check():
    return {"status": "UP"}

@app.include_router(loan_routes.router)
