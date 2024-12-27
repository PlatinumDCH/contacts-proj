from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
import pickle
import redis

from app.repository import users as repository_users
from app.models.base_model import Users
from app.config.pack_roles import Role
from app.services.jwt_serv import JWTService
from app.db.get_session import get_connection_db
from app.config import settings, logger


class AuthService:
    auth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
    cashe = redis.Redis(
        host=settings.REDIS_DOMAIN,
        port=settings.REDIS_PORT,
        db=0,
        password=settings.REDIS_PASSWORD,
    )

    async def get_current_user(
        self,
        token: str = Depends(auth2_scheme),
        db: AsyncSession = Depends(get_connection_db),
    ):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            logger.info("начало получение токена")
            email = await JWTService().decode_token(token, settings.access_token)
            logger.info(f"получил вот такой емеил {email}")
            if email is None:
                raise credentials_exception
        except JWTError as err:
            raise credentials_exception

        user_hesh = str(email)
        user = self.cashe.get(user_hesh)
        if user is None:
            logger.info(f"User {email} from database")
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            logger.info(f"Checking cache for user {user_hesh}")
            self.cashe.set(user_hesh, pickle.dumps(user))
            self.cashe.expire(user_hesh, 500)
        else:
            logger.info("user {email} from cashe")
            user = pickle.loads(user)

        return user

    async def check_roles(
        self, token: str, db: AsyncSession, allowed_roles: list[Role]
    ) -> Users:
        """проверить если ли у пользователя допустимая роль"""
        user = await self.get_current_user(token, db)
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {user.role} is not allowed",
            )
        return user
