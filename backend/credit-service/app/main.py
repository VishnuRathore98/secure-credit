from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.messages import rabbitmq_channel, handle_message, INPUT_QUEUE


@asynccontextmanager
async def lifespan(app: FastAPI):
    rabbitmq_channel.basic_consume(
        queue=INPUT_QUEUE, on_message_callback=handle_message
    )
    rabbitmq_channel.start_consuming()
    yield
    rabbitmq_channel.stop_consuming()


app = FastAPI(title="Credit Service", lifespan=lifespan)


@app.get("/health")
def health_check():
    return {"status": "UP"}
