from aio_pika import connect_robust, exceptions
from aio_pika.abc import AbstractRobustConnection
import asyncio
from contextlib import asynccontextmanager

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
        """возвращает активное соединение или создает новое
        """
        if self.connection and not self.connection.is_closed:
            logger.info('переиспользование подключения')
            return self.connection
        
        for attempt in range(self.retries):
            try:
                self.connection = await connect_robust(self.url)
                logger.info('соединение сосздано')
                return  self.connection
                
            except exceptions.AMQPConnectionError as err:
                logger.error(f'rabbitmq conn FALSE, {attempt + 1}/{self.retries} {err}')
                if attempt == self.retries -1: # if last attempt
                    raise RuntimeError('Could not connect to RabbitMQ')
                await asyncio.sleep(self.delay)
        
    async def close(self):
        """закрыть текущее соединение если оно сцществует"""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info('соединение закрыто')
    
    async def __aenter__(self)->AbstractRobustConnection:
        """контекстный менеджер для автоматического подключения"""
        logger.info('автоматическое подключение')
        return await self.connection()
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        """контекстный менеджер для автоматического закрытия соединения"""
        logger.info('автоматическое отключение')
        await self.close()

@asynccontextmanager
async def get_rabbitmq_connection():
    manager = RaabbitMQConnectionManager(url=settings.RABBITMQ_URL)
    connection = await manager.connect()
    try:
        yield connection
    finally:
        await manager.close()

