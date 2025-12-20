import pika
from app.core.config import settings


params = pika.URLParameters(settings.RABBITMQ_URL)
rabbitmq_connection = pika.BlockingConnection(params)
rabbitmq_channel = rabbitmq_connection.channel()
