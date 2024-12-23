import aio_pika
import json
from aio_pika import ExchangeType

from app.db.get_rab_con import get_rabbitmq_connection
from app.config import logger, settings

async def send_to_rabbit(message: dict):
    '''Публикация сообщения в RabbitMQ
    
    :parm message: Словарь с данными для публикации в RabbitMQ
    :parm message_type: Тип сообщения (password_reset, email_verification)
    '''
    logger.info("Подготовка к отправке уведовления к RabbitMQ")
    try:
        async with get_rabbitmq_connection() as connection:
            channel = await connection.channel()
            #обьявляем обменник
            exchange = await channel.declare_exchange(
                name="sending_mail",
                type=ExchangeType.DIRECT,
                durable=True
            )
            #бубликуем сообщение
            await exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=message['queue_name']
            )
            logger.info(f"Сообщение отправлено в RabbitMQ с ключом '{message['queue_name']}'")
    except Exception as err:
        logger.err(f'Failed to publisher message: {err}')