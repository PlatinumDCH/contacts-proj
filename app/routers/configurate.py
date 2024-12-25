from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.get_session import get_connection_db
from app.config.logger import logger
from sqlalchemy import text
from app.depend.roles_dependies import role_dependency_admin

router = APIRouter(prefix="/config", tags=["configurate"])


@router.get("/healthchecker", dependencies=[Depends(role_dependency_admin)])
async def healthchecker(db: AsyncSession = Depends(get_connection_db)
                        ):
    """вроверка подклюяения к базе данных
    
    Depends:
        role_dependency_admin - зависимось которая проверяет что у пользователя
        роль админ
    Args:
        звисимось подключения к базе данных
    Returns:
        if connection data pase corect, return messages
        else HTTPExeption
    """
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, 
                detail="Database is not configured correctly"
                )
        return {
            "message": "Data base normaly work"
            }
    except Exception as err:    
        logger.critical(f'Database connection error, {err}')
        raise HTTPException(
            status_code=500, 
            detail="Error connecting to the database"
            )
