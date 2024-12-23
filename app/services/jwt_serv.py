from fastapi import HTTPException, status
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
import pytz

from app.config import settings

class JWTService:
    SECRET_KEY = settings.SECRET_KEY_JWT
    ALGORITHM = settings.ALGORITHM

    async def create_access_token(
            self, 
            data: dict, 
            expires_delta:Optional[float]=None)->str:
        to_encode = data.copy()
        unc_now = datetime.now(pytz.UTC)
        if expires_delta:
            expire = unc_now + timedelta(minutes=expires_delta)
        else:
            expire = unc_now + timedelta(minutes=45)
        to_encode.update(
            {'iat': datetime.now(pytz.UTC),  # time created token
             'exp': expire,  # finishing time token
             'scope': 'access_token'}  # token type
        )
        encoded_assess_token = jwt.encode(
            to_encode, 
            self.SECRET_KEY, 
            algorithm=self.ALGORITHM
            )
        return encoded_assess_token
        
    async def create_refresh_token(
            self, data: dict,
            expires_delta: Optional[float] = None) -> str:
        to_encode = data.copy()
        utc_now = datetime.now(pytz.UTC)
        if expires_delta:
            expire = utc_now + timedelta(seconds=expires_delta)
        else:
            expire = utc_now + timedelta(days=7)
        to_encode.update({
            'iat': datetime.now(pytz.UTC),  # time creates token
            'exp': expire,  # finisfing time token
            'scope': 'refresh_token'  # type token
        })
        encoded_refresh_token = jwt.encode(
            to_encode, 
            self.SECRET_KEY, 
            algorithm=self.ALGORITHM)
        return encoded_refresh_token
    
    async def decode_token(self, token: str, token_type: str) -> str:
        """возврат емейла, проверка вермини действия токена"""
        try:
            payload = jwt.decode(
            token, 
            self.SECRET_KEY, 
            algorithms=[self.ALGORITHM]
            )
            # проверка на наличие времени истечения действия токена
            exp = payload.get('exp')
            if exp is None:
                raise JWTError('Token has no exporation time')
            
            #проверка на истечение времени действия токена
            utc_now = datetime.now(pytz.UTC)
            if utc_now > datetime.fromtimestamp(payload['exp'], tz=pytz.UTC):
                raise JWTError('Token has expired')

            #проверка на тип токена
            if payload['scope'] != token_type:
                raise JWTError('Invalid token type')
            
            return payload.get('sub')
            
        except JWTError as err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail=str(err)
                )
        except Exception as err:
            HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail='Invalid token'
                )
        