from contextlib import asynccontextmanager
from fastapi import FastAPI
import pika
import json
import os


RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE_NAME = "loan.submitted"


@asynccontextmanager
async def lifespan(app: FastAPI):
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    def handle_message(ch, method, properties, body):
        event = json.loads(body.decode())
        print("Notification received:", event)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=handle_message)

    print("rabbitmq: loan:submitted started consuming.")

    channel.start_consuming()

    yield

    print("rabbitmq: loan:submitted stoped consuming.")

    channel.stop_consuming()


app = FastAPI(title="Notification Service", lifespan=lifespan)


@app.get("/health")
def health_check():
    return {"status": "UP"}
