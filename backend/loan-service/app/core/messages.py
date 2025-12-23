import pika
import json
from datetime import datetime
from app.core.config import settings
import logging
from app.models.loan_models import Loan
from sqlalchemy.ext.asyncio import AsyncSessionLocal


decision_logger = logging.getLogger("loan-decision-consumer")


params = pika.URLParameters(settings.RABBITMQ_URL)
rabbitmq_connection = pika.BlockingConnection(params)
rabbitmq_channel = rabbitmq_connection.channel()


# setting up loan decision consumer
DECISION_QUEUE = "loan.decision"


def start_credit_decision_consumer():
    params = pika.URLParameters(settings.RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=DECISION_QUEUE, durable=True)

    def handle_decision(ch, method, properties, body):
        event = json.loads(body.decode())
        decision_logger.info("Credit decision received: %s", event)

        loan_id = event["payload"]["loan_id"]
        approved = event["payload"]["approved"]
        approved_amount = event["payload"]["approved_amount"]

        from sqlalchemy.future import select

        async def update_loan():
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(Loan).where(Loan.id == loan_id))
                loan = result.scalar_one_or_none()

                if not loan:
                    decision_logger.warning("Loan not found: %s", loan_id)
                    return

                loan.status = "APPROVED" if approved else "REJECTED"
                loan.approved_amount = approved_amount
                loan.updated_at = datetime.utcnow()

                await session.commit()
                decision_logger.info("Loan %s updated to %s", loan_id, loan.status)

        import asyncio

        asyncio.run(update_loan())

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=DECISION_QUEUE,
        on_message_callback=handle_decision,
    )

    decision_logger.info("Started credit decision consumer")
    channel.start_consuming()
