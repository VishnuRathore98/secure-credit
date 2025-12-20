from fastapi import FastAPI
from app.api.v1 import loan_routes
from app.core.database import Base, engine

app = FastAPI(title="Loan Service")


Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "UP"}


app.include_router(loan_routes.router)
