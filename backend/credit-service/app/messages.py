import pika
import json
import random
import logging
import os


RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
INPUT_QUEUE = "loan.submitted"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("credit-service")


params = pika.URLParameters(RABBITMQ_URL)
connection = pika.BlockingConnection(params)
rabbitmq_channel = connection.channel()

rabbitmq_channel.queue_declare(queue=INPUT_QUEUE, durable=True)


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

    rabbitmq_channel.basic_publish(
        exchange="",
        routing_key="loan.decision",
        body=json.dumps(result_event).encode(),
    )

    logger.info("Credit decision published: %s", result_event)
    ch.basic_ack(delivery_tag=method.delivery_tag)
