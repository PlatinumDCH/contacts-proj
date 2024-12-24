from fastapi import APIRouter, Depends, HTTPException, status,Response, Request
from fastapi import Body
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository import users as repo_users
from app.config.configurate import settings
from app.db.get_session import get_connection_db
from app.services.base import service
from app.config.logger import logger
from app.repository import users as repo_users
from app.services.base import service
from fastapi_limiter.depends import RateLimiter
from app.models.base_model import Users
from fastapi.templating import Jinja2Templates

from app.shemas.user import ReauestEmail, UserResponse
from app.shemas.password import ConfirmPassword

router = APIRouter(prefix='/users', tags=['users'])
templates = Jinja2Templates(directory='app/templates/pasw')
home_templates = Jinja2Templates(directory='app/templates')

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

@router.get('/me', response_model=UserResponse, 
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_current_user(user:Users=Depends(service.auth.get_current_user)):
    """
    postman
    get http://127.0.0.1:8000/api/users/me
    autorization : type bearer token
    вставить токен access
    ограничение запросов 1 на 20с.
    """
    try:
        logger.info('возврат собтвенного ендпоинта')
        return user
    except Exception as err:
        logger.error('Ошибка при проучения текущего пользователя',err)
        raise HTTPException(
            status_code = status.HTTP_429_TOO_MANY_REQUESTS,
            detail='To mane request'
        )

@router.get('/{username}')
async def request_email(username: str, response: Response, 
                        db: AsyncSession = Depends(get_connection_db)):
    """роут для отслеживания, открыл ли получатель письмо
    в пистме есть статический прозрачный пиксель за которым браузер делает
    запрос на сервер"""
    logger.info(f'{username} open verifivation email')
    return FileResponse("app/templates/static/open_check.png", media_type="image/png", content_disposition_type="inline")

@router.post('/request_email')
async def request_email(body:ReauestEmail,request:Request,
                        db:AsyncSession=Depends(get_connection_db)):
    """повторная отправка email для подтверждения"""
    user = await repo_users.get_user_by_email(body.email, db)
    if user.confirmed:
        return {
            'message':'You email is already confirmed'
        }
    await service.email.pocess_email_confirmation(user,request,db)
    return {
        'message':'Email send, checck you post for confirmation'
    }

@router.get('/reset_password_form/{token}')
async def reset_password_form(request: Request, token:str ):
    try:
        email = await service.jwt.decode_token(
            token,
            settings.reset_password_token
        )
    except HTTPException as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid or expired token'
        )
    
    return templates.TemplateResponse(
        'form_input_password.html',
        {
            'request':request,
            'token':token,
        }
    )

@router.post('/reset_password',status_code=status.HTTP_200_OK)
async def change_password(
    request:Request,
    body: ConfirmPassword = Body(...),
    db:AsyncSession=Depends(get_connection_db),
    ):
    logger.info('start change password')
    try:
        email = await service.jwt.decode_token(
            body.token, 
            settings.reset_password_token
            )
    except HTTPException as err:
        raise err
    logger.info('get user')
    user = await repo_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Verification error, user not found'
            )
    logger.info('old_password == ? new_password ')
    identic_password = service.password.verify_password(
        body.new_password, 
        user.password
        )
    if identic_password:
        logger.warning(f'new password == old password, {user.username}, {body.new_password}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='New password is the same as old password'
            )
    hashed_password = service.password.get_password_hash(body.new_password)
    await repo_users.update_user_password(user, hashed_password, db)
    logger.info(f'{user.username} reset password')
    await repo_users.update_token(
        user, 
        None, 
        settings.reset_password_token, 
        db
        )
    logger.info(f'{user.username} del reset_password_token')

    return {
        'message':'password successfully updated'
        }
    