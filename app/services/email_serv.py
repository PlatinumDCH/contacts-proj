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
from app.services.jwt_serv import JWTService

class EmailService(JWTService):
    
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

    async def process_email_change_pass(
            self,
            user:UserSchema,
            request:Request,
            db:AsyncSession
    ):
        """создание задачи и отправка писька для смены пароля"""
        re_pass_token = await self.create_re_pass_token(
            {'sub':user.email},
            settings.reset_password_token
        )
        logger.info('создать токен сброса пароля, успешно')
        await repo_users.update_token(
            user,
            re_pass_token,
            settings.reset_password_token,
            db
        )
        logger.info('записать рефреш токен в дазу данных,успешно')
        email_task = {
            'email':user.email,
            'username':user.username,
            'host': str(request.base_url),
            'queue_name':'reset_password',
            'token':re_pass_token
        }
        await self.send_email(email_task)
        logger.info('отрпавить запрос к серверу rabbitmq, успешно')

   
        
email_service = EmailService()