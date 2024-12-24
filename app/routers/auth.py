from fastapi import APIRouter, status, Request, Depends, HTTPException
from fastapi import Security
from app.shemas.user import UserResponse, UserSchema
from app.shemas.token import TokenSchema
from fastapi.security import HTTPBearer
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.get_session import get_connection_db
from app.repository import users as repo_users
from app.config.logger import logger
from app.services.base import service
from app.config.configurate import settings
from app.shemas.password import ResetPasswordSchema

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()


@router.post('/signup', response_model=UserResponse,
             status_code=status.HTTP_201_CREATED)
async def signup(
    body: UserSchema,
    request:Request,
    db:AsyncSession = Depends(get_connection_db)
):
    """
    регистрация пользователя на сайте

    Args:

        body = {
            username
            email
            password
        }
        type:UserSchema

        request = ...
        type: Request

        db = ассинхроннай коннект к базе данных
        type:AsseyncSession
        descriptions: автоматический вызов get_connection_db

    Return:
        dict

    Description:
        проверка на наличине пользователя(email) в базе данных
        перевод вводимого пароля в хешированый
        создание нового пользователя в базе данных repo_users
        создание токена email_token для подвтерждения почты
        создатие словаря не необходимой информацией для отправки письма подтв.
        добавить емеил токен в базу данных
        отрпавить токен и словарь с данными для отправки в сервис rabbitmq
    
    """
    exist_user = await repo_users.get_user_by_email(body.email, db)
    if exist_user:
        logger.warning('user already exists in database')
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='account already exists'
        )
    body.password = service.password.get_password_hash(body.password)
    new_user = await repo_users.create_user(body, db)

    await service.email.pocess_email_confirmation(
        new_user,
        request,
        db
    )
    return {
        'id':new_user.id,
        'username':new_user.username,
        'email':new_user.email
    }
    


@router.post('/login')
async def login(
    body: OAuth2PasswordRequestForm=Depends(),
    db:AsyncSession=Depends(get_connection_db)
)->dict:
    """
    Aутентификация пользователя и выдача токенов доступа и обновления

    Args:
        body:
        type:OAuth2PasswordRequestForm (application/x-www-form-urlencoded)
        descriptions: принимает body в виде form_data, требуются обезательные 
        поля username - password. Автоматически извлекает данные из тела запроса.

        db: асинхронная сессия базы данных
        type: AsyncSession

    Raises:
        HTTPException: Invalid email
        HTTPException: Invalid password

    Returns:
        dict: dict{access_token:X, refresh_token:X, token_type:X}

    Descriprion:
        *username == email, в данному случае
        получить пользователя запросом к базе данных (email)
        если ответ None, такого пользователя нету
        если поле confirmed(подтв почта) = False. не пускать
        если пароли не совпадают (введенный и созраненный в бд), не пускать
        если все ок, создаем новую пару токенов
        обновляем в бд рефреш-токен пользователя
        возвращаем jwt-token (combo access|refersg|token_type)
    """
    user = await repo_users.get_user_by_email(
        body.username,
        db
    )
    if user is None:
        logger.info('Не нашел email в дазе данных')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='envalid email'
        )
    if not user.confirmed:
        logger.info('емеил не подтвержден в базе данных')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Account not confirmed, check email'
        )
    if not service.password.verify_password(
        body.password,
        user.password):
        logger.infog('пароли не совпадают')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid pass'
        )
    encoded_assess_token = await service.jwt.create_access_token(
        data={'sub':user.email}
    )
    logger.info('создал токен assess')
    encoded_refresh_token = await service.jwt.create_refresh_token(
        data={'sub':user.email}
    )
    logger.info('создал refresh токен')
    await repo_users.update_token(user, encoded_refresh_token, settings.refresh_token, db)
    logger.info('обновил refresh токен в базе данных')
    return {
        'access_token':encoded_assess_token,
        'refresh_token':encoded_refresh_token,
        'token_type':'bearer'
    }

@router.post('/reset_password_request')
async def forgot_password(
    body:ResetPasswordSchema,
    request:Request,
    db:AsyncSession=Depends(get_connection_db)
):
    """
    получить пользователя body.email
    проверить есть ли такой пользователь в базе данных
    тозадть токен сброса пароля
    создать задачу на отравку письма сброса пароля
    отправить письмо через rabbitmq
        """
    curent_user = await repo_users.get_user_by_email(body.email, db)
    if not curent_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    logger.info('пользователь получен', curent_user.username)
    await service.email.process_email_change_pass(
        curent_user,
        request,
        db
    )
    return {
        'message':'Check you email for reset password'
    }

