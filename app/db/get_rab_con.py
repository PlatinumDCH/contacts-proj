from aio_pika import connect_robust, exceptions
from aio_pika.abc import AbstractRobustConnection
import asyncio

from app.config.configurate import settings
from app.config.logger import logger



class RaabbitMQConnectionManager:
    def __init__(self, url:str, retries:int=5, delay:int=1):
        """Инициализация менеджера соединения с rabbitmq

        Args:
            url (str): url для подключения
            retries (int, optional): Количество повторных попыток подключения. Defaults to 5.
            delay (int, optional): Задержка мужду попытками подключения. Defaults to 1.
        """
        self.url = url
        self.retries = retries
        self.delay = delay
        self.connection:AbstractRobustConnection|None = None
    
    async def connect(self)->AbstractRobustConnection:
        """устанавливаем соединение с rabbotmq с повторными попытками

        Returns:
            AbstractRobustConnection: объект соединения
        """
        for attempt in range(self.retries):
            try:
                self.connection = await connect_robust(self.url)
                logger.info('rabbitmq conn TRUE')
                return  self.connection
                
            except exceptions.AMQPConnectionError as err:
                logger.error(f'rabbitmq conn FALSE, {attempt + 1}/{self.retries} {err}')
                if attempt == self.retries -1: # if last attempt
                    raise RuntimeError('Could not connect to RabbitMQ')
                await asyncio.sleep(self.delay)
        
    async def close(self):
        """Закрываем соединение с rabbitmq"""
        if self.connection:
            await self.connection.close()
            logger.info('rabbotmq connection closed')
    
    async def __aenter__(self)->AbstractRobustConnection:
        """контекстный менеджер для автоматического подключения"""
        await self.connect()
        return self.connection
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        """контекстный менеджер для автоматического закрытия соединения"""
        await self.close()

async def get_rabbit_connection():
    url = settings.RABBITMQ_URL
    retries = 5
    delay = 1
    async with RaabbitMQConnectionManager(url, retries, delay) as connection:
        logger.info("Using RabbitMQ connection")
        yield connection