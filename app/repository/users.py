from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.get_session import get_connection_db
from app.models.base_model import Users
from sqlalchemy import select, update
from app.models.base_model import UserTokensTable
from app.shemas.user import NewUserSchema
from app.shemas.token import TokenUpdateRequest
from libgravatar import Gravatar
from app.config.logger import logger

async def get_user_by_email(email:str,db: AsyncSession = 
    Depends(get_connection_db))->Users|None:    
    """
    Получить пользователя пол его адресу електронной почты из дазы данных.

    Args:
        email (str): Адрес електронной посчты пользователя, которого нужно получить.
                
        db (AsyncSession, optional): Зависимось сессии базы данных.По уиолчанию используется асинхронная сесия из
        get_connection_db

    Returns:
        Users | None: The user object if found, otherwise None.
    """
    
    query = select(Users).filter_by(email=email)
    user = await db.execute(query)
    user = user.scalar_one_or_none()
    return user

async def create_user(
        body: NewUserSchema, 
        db: AsyncSession = Depends(get_user_by_email))->Users:
    """
    создать пользователя в базе данных.

    Args:
        body (NewUserSchema): схема содержащая данные нового пользователя.
        db (AsyncSession, optional): ависимось сессии базы данных.
                по уиолчанию используется асинхронная сесия из get_connection_db

    Returns:
        Users: обьект только что созданного пользователя.

    Raises:
        Exception: Возникает ошибка при получении аватара пользователя.
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar:str = g.get_image() # url
    except Exception as err:
        logger.error('User not have image in serice Gravatar')
    new_user = Users(
        **body.model_dump(),
        avatar=avatar
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

"""
Descriptions:
        Что делает функция:
        1. Находит токены пользователя в базе данных:
            user_tokens = UserTokensTable(
                user_id=1,
                refresh_token="old_token",
                email_token="email_token"
            )
        2. Если `user_tokens` не None, обновляем значение токена.
        3. Если `user_tokens` is None, создаёт новый объект `UserTokensTable` с user_id и значением токена.
        4. Сохраняет изменения в базе данных.
        5. Обрабатывает ошибки, открывая транзакцию.
"""
async def update_token(
        user: Users,
        token: TokenUpdateRequest,
        token_type:str,
        db: AsyncSession)->None:
    """
    обновить токен пользователя в базе данных

    Args:
        user (UsetsTable): объект пользователя с идентификатором пользователя.
        token (str): новое значение токена для сохранения.
        token_type (str): тип токена (e.g., "refresh_token").
        db (AsyncSession): сессия базы данных для выполнения запросов.

    Returns:
        None
    """
    try:
        user_query = select(UserTokensTable).filter_by(user_id=user.id)
        result = await db.execute(user_query)
        user_tokens = result.scalar_one_or_none()
        
        if user_tokens:
            setattr(user_tokens, token_type, token)
            update_query = (
                update(UserTokensTable)
                .where(UserTokensTable.user_id == user.id)
                .values(**{token_type: token})
            )
            await db.execute(update_query)

        else:
            new_token = UserTokensTable(user_id=user.id, **{token_type: token})
            db.add(new_token)
            user_tokens = new_token

        await db.commit()
        await db.refresh(user_tokens)

    except Exception as err:
        await db.rollback()
        logger.error(f"Failed to update user's token: {err}/{token_type}")
        raise err

async def get_token(user: Users, token_type: str, db: AsyncSession) -> str | None:
    """
    получить значение токена для использования из базы данных

    Args:
        user (UsersTable): обьект пользователя из базы данных
        token_type (str): тип токена
        db (AsyncSession): ассинхронная сессия для выполнения запроса

    Returns:
        str|None: закодированый токен в виде строки или None
    """
    try:
        user_query = select(UserTokensTable).filter_by(user_id=user.id)
        result = await db.execute(user_query)
        user_token = result.scalar_one_or_none()

        if user_token:
            return getattr(user_token, token_type, None)
        else:
            return None
    except Exception as err:
        logger.error(f"Failed to get user token: {err}/{token_type}")
        raise err
    
async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    обновить стату подтверждения пользователя на True на основе его 
    електронной почты.

    Args:
        email (str): адрес посты пользователя стату подтверждения которого нужно 
        обновить.
        db (AsyncSession): сессия базы данных, используемая для операции.

    Returns:
        None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()
    await db.refresh(user)

async def update_user_password(user: Users, password: str, db: AsyncSession):
    """
    обновить пароь для указанного пользователя.

    Args:
        user (Users): обькт пользователя чей пароль нужно обновить.
        password (str): новый пароль для установки пользрвателю.
        db (AsyncSession): сессия базы данных используемая для операции.

    Returns:
        Users: обновленный обьект пользователя с новым паролем.
    """
    user = await get_user_by_email(email=user.email, db=db)
    user.password = password
    await db.commit()
    await db.refresh(user)
    return user

async def update_avatar_url(email:str,url:str|None, db:AsyncSession):
    """обновить url аватара пользоваталея"""
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user