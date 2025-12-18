from fastapi import FastAPI
import pika
import json
import os
import random
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("credit-service")

app = FastAPI(title="Credit Service")

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
INPUT_QUEUE = "loan.submitted"


@app.on_event("startup")
def startup():
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=INPUT_QUEUE, durable=True)

    def handle_message(ch, method, properties, body):
        event = json.loads(body.decode())
        logger.info("Loan received for credit check: %s", event)

        approved = random.choice([True, False])

        result_event = {
            "event_type": "LoanApproved" if approved else "LoanRejected",
            "payload": {
                "loan_id": event["payload"]["loan_id"],
                "approved": approved,
                "approved_amount": event["payload"]["loan_amount"] if approved else 0,
            },
        }

        channel.basic_publish(
            exchange="",
            routing_key="loan.decision",
            body=json.dumps(result_event).encode(),
        )

        logger.info("Credit decision published: %s", result_event)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=INPUT_QUEUE, on_message_callback=handle_message)
    channel.start_consuming()


@app.get("/health")
def health_check():
    return {"status": "UP"}
