from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
import pytz


from app.services.rabbit_send.produse import send_to_rabbit
from app.config import settings, logger

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
    
    
    async def send_email(self, email_task:dict,email_token:str=None):
        try:
            logger.info(f'Sending email task to RabbitMQ: {email_task} ')
            await send_to_rabbit(email_task)
        except Exception as err:
            logger.error(f'Failed to send email task to RabbitMQ: {err}')
            raise




email_service = EmailService()