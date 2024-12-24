from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.get_session import get_connection_db
from app.config.logger import logger
from sqlalchemy import text
from app.services.auth_serv import RoleAccess
from app.models.base_model import Users
from app.services.base import service
from app.config.pack_roles import Role

router = APIRouter(prefix="/config", tags=["configurate"])
access_to_rolle_all = RoleAccess(
    [Role.ADMIN, Role.MODERATOR]
)

@router.get("/healthchecker",dependencies=[Depends(access_to_rolle_all)])
async def healthchecker(db: AsyncSession = Depends(get_connection_db),
                        user:Users = Depends(service.auth.get_current_user)):
    """вроверка подклюяения к базе данных"""
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
