from aio_pika import IncomingMessage, ExchangeType
import asyncio
import json
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pathlib import Path

from app.config.configurate import settings
from app.config.logger import  logger
from app.db.get_rab_con import get_rabbitmq_connection


BASE_DIR = Path(__file__).resolve().parent.parent.parent / 'templates'

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_USERNAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME='Contact server',
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER= BASE_DIR
)


async def process_message(message:IncomingMessage):
    """Обработка входящего сообщения из очереди"""
    try:
        async with message.process():
            try:
                task_data = json.loads(message.body)
                email = task_data['email']
                username = task_data['username']
                host = task_data['host']
                message_type = task_data['queue_name']
                token = task_data['token']

                logger.info(f"Message data parsed: {task_data}")
            except KeyError as err:
                logger.error(f'Missing required field in message: {err}')
                return

            if message_type == 'reset_password':
                logger.info("Processing reset password message")
                message_schema = MessageSchema(
                    subject="Changer server-pas",
                    recipients=[email],
                    template_body={"host": host, "username": username,"token": token},    
                    subtype=MessageType.html,
                )
                template_name = 'pasw/psw_reset.html'

            elif message_type == 'confirm_email':
                logger.info("Processing confirm email message")
                message_schema = MessageSchema(
                    subject='Changer server-email',
                    recipients=[email],
                    template_body={'host':host, 'username':username,'token':token},
                    subtype=MessageType.html,
                )
                template_name='email/email_confirm.html'
            else:
                logger.warning(f"Unknown message type: {message_type}")
                return
            fm = FastMail(conf)
            logger.info(f"Sending email to: {email}")
            logger.info(f"Using template: {template_name}")
            await fm.send_message(message_schema, template_name=template_name)
            logger.info(f'Message precessed successfully : {email}. Type: {message_type}')
    except Exception as err:
        logger.error(f'Failed to process message: {err}')
        raise

async def main():
    logger.info("Starting worker...")
    """Основной воркер для обработки сообщений из RabbitMQ"""
    max_retires = 5 # максимальное количество повторных попыток
    retry_count = 0 # Счетчик попыток
    while retry_count < max_retires:
        try:
            async with get_rabbitmq_connection() as connection:
            
                # Объявление обменника
                async with connection:
                    channel = await connection.channel()
                    exchange = await channel.declare_exchange(
                                name="sending_mail",
                                type=ExchangeType.DIRECT,
                                durable=True
                            )

                        # Объявляем очередь и связываем с routing_key
                    queue = await channel.declare_queue('email_queue', durable=True)
                    await queue.bind(exchange, routing_key="reset_password")
                    await queue.bind(exchange, routing_key="confirm_email")

                        # Запускаем обработку сообщений
                    await queue.consume(process_message)
                    logger.info("Worker is consuming messages...")

                    # Ожидание новых сообщений
                    while True:
                        await asyncio.sleep(1)

        except Exception as err:
            retry_count += 1
            logger.error(f'An error occurred in the main loop: {err}')
            if retry_count < max_retires:
                logger.info(f'Retrying in 5 seconds... Attempt {retry_count}/{max_retires}')
                await asyncio.sleep(5)
            else:
                logger.critical('Max retry attempts reached.Exiting')
        finally:
            logger.info("Worker finished.")
                
if __name__ == '__main__':
    print('Воркер работат')
    asyncio.run(main())
  