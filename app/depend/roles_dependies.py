from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.config.pack_roles import Role
from app.services.base import service
from app.db.get_session import get_connection_db
from app.models.base_model import Users

class RoleDepandency:
    def __init__(self, allowed_roles: list[Role]):
        """
        зависимость для проверки ролей
        Args:
            list[Role] - передаваемый список допустимых ролей
        """
        self.allowed_roles = allowed_roles
    
    async def __call__(
            self,
            token:str = Depends(service.auth.auth2_scheme),
            db: AsyncSession = Depends(get_connection_db)
    )->Users:
        """
        проверка  роли пользователя
        
        Args:
            token(str): токен авторизации
            db: (AsyncSession): ассинхронная сессия базы данных
        
        Resturns:
            Users: обьект пользователя
        
        Raises:
            HTTPExceptions: если пользовател не имеет разрещенной роли
        """
        user = await service.auth.check_roles(token, db, self.allowed_roles)
        return user



role_dependency_admin = RoleDepandency(allowed_roles=[Role.ADMIN])

role_dependency_all = RoleDepandency(allowed_roles = [
    Role.ADMIN, 
    Role.MODERATOR, 
    Role.USER
    ])
