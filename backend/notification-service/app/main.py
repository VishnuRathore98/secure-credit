from fastapi import FastAPI
import pika
import json
import os

app = FastAPI(title="Notification Service")

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE_NAME = "loan.submitted"


@app.on_event("startup")
def startup():
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    def handle_message(ch, method, properties, body):
        event = json.loads(body.decode())
        print("Notification received:", event)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=handle_message)

    channel.start_consuming()


@app.get("/health")
def health_check():
    return {"status": "UP"}
