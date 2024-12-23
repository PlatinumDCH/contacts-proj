import aio_pika
import json
from aio_pika import ExchangeType

from app.db.get_rab_con import get_rabbit_connection
from app.config import logger, settings

async def send_to_rabbit(message: dict):
    '''Публикация сообщения в RabbitMQ
    
    :parm message: Словарь с данными для публикации в RabbitMQ
    :parm message_type: Тип сообщения (password_reset, email_verification)
    '''
    logger.info("Preparing to send message to RabbitMQ")
    async for connection in get_rabbit_connection():
        async with connection:
            channel = await connection.channel()

            exchange = await channel.declare_exchange(
                name="sending_mail",
                type=ExchangeType.DIRECT,
                durable=True
            )
            
            await exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=message['queue_name']
            )
            logger.info(f"Message published to RabbitMQ with routing_key '{message['queue_name']}")
            break 