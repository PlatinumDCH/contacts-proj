from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.config.pack_roles import Role
from app.services.base import service
from app.db.get_session import get_connection_db
from functools import partial



async def role_dependency(
        allowed_roles = list[Role],
        token:str = Depends(service.auth.auth2_scheme),
        db:AsyncSession = Depends(get_connection_db)
):
    """зависимосмость для проверки ролей
    Args:
        list[Role] - передаваемый список допустимых ролей
        token: зависимось которая проверет access токен
        db: зависимось которая предоставляет выдачу асинхронной сессия бд

    role_dependency:
        token
        db
        allowed roles: розрещшенный пользователи

        Description:
            получает обьект пользователя с базы данных
            если роль пользователя есть в переданном списке
            возвращает пользователя
    Reautrns:
        usres
    """
    return await service.auth.check_roles(token, db, allowed_roles)

role_dependency_admin = partial(role_dependency, allowed_roles=[Role.ADMIN,])
role_dependency_all = partial(role_dependency, allowed_roles = [
    Role.ADMIN, Role.MODERATOR, Role.USER
])
