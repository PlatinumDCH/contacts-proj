from fastapi import APIRouter, Depends, HTTPException, status,Response
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository import users as repo_users
from app.config.configurate import settings
from app.db.get_session import get_connection_db
from app.services.base import service
from app.config.logger import logger

router = APIRouter(prefix='/users', tags=['users'])

@router.get('/confirmed_email/{token}')
async def confirmed_email(
    token:str, 
    db:AsyncSession=Depends(get_connection_db)):
    
    email = await service.jwt.decode_token(
        token, 
        settings.email_token
        )
    user = await repo_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Verification error, user not found'
            )
    if user.confirmed:
        return {'message':'Your email already confirmed'}
    #change filed confirmed in UserTable
    await repo_users.confirmed_email(email, db)
    await repo_users.update_token(user, None, settings.email_token, db)
    return {'message': 'Email confirmed'}


@router.get('/{username}')
async def request_email(username: str, response: Response, db: AsyncSession = Depends(get_connection_db)):
    logger.info(f'{username} open verifivation email')
    return FileResponse("app/templates/static/open_check.png", media_type="image/png", content_disposition_type="inline")
