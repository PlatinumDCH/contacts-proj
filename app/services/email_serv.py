from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
import pytz
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from app.services.rabbit_send.produse import send_to_rabbit
from app.config import settings, logger
from app.shemas.user import UserSchema
from app.repository import users as repo_users

class EmailService:
    SECRET_KEY = settings.SECRET_KEY_JWT
    ALGORITHM = settings.ALGORITHM

    async def create_email_token(
            self, 
            data:dict, 
            token_type:str,
            expires_delta:Optional[float]=None
            ):
        to_encode = data.copy()
        unc_now = datetime.now(pytz.UTC)
        if expires_delta:
            expire = unc_now + timedelta(hours=expires_delta)
        else:
            expire = unc_now + timedelta(hours=12)
        to_encode.update({
            'exp':expire,
            'iat':datetime.now(pytz.UTC),
            'scope': token_type
        })
        encoded_email_token = jwt.encode(
            to_encode, 
            self.SECRET_KEY, 
            algorithm=self.ALGORITHM
            )
        logger.info(f'token type {to_encode["scope"]}')
        return encoded_email_token
    
    
    async def send_email(self, email_task:dict):
        """
        отравка email задачи в rabbitmq
        email_task = {
            'email':new_user.email,
            'username':new_user.username,
            'host': str(request.base_url),
            'queue_name':'confirm_email',
            'token': < email_token >
            }
        """
        try:
            logger.info(f'Отравка словаря с информацией к RabbitMQ: {email_task} ')
            await send_to_rabbit(email_task)
        except Exception as err:
            logger.error(f'Ошибка отпраки  email задачи к RabbitMQ: {err}')
            raise


    async def pocess_email_confirmation(
            self,
            user: UserSchema,
            request: Request,
            db: AsyncSession
    ):
        """создание email задачи и отправка подтверждения"""
        email_token = await self.create_email_token(
            {'sub':user.email},
            settings.email_token
        )
        logger.info('Cоздать email_toke, успешно')
        await repo_users.update_token(
            user,
            email_token,
            settings.email_token,
            db
        )
        logger.info('обновить email токен в базе данных, успешно')
        email_task = {
            'email':user.email,
            'username':user.username,
            'host': str(request.base_url),
            'queue_name':'confirm_email',
            'token':email_token
        }
        await self.send_email(email_task)
        logger.info('отравить запрос к серверу rabbitmq успешно')

email_service = EmailService()