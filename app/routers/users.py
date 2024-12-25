import cloudinary.uploader
from fastapi import APIRouter, Depends, HTTPException, status,Response, Request
from fastapi import Body, UploadFile, File
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
import cloudinary
import pickle
from fastapi.templating import Jinja2Templates

from app.shemas.user import ReauestEmail, UserResponse
from app.shemas.password import ConfirmPassword

router = APIRouter(prefix='/users', tags=['users'])
templates = Jinja2Templates(directory='app/templates/pasw')
home_templates = Jinja2Templates(directory='app/templates')



@router.patch('/avatar', response_model=UserResponse,
             dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_current_user(
    file:UploadFile = File(),
    user:Users = Depends(service.auth.get_current_user),
    db:AsyncSession = Depends(get_connection_db)):
    """
    обработка загрузки аватара для текущего пользователя.

    этот ендпоит позволяет аутентифицированому пользователю загрузить
    изображение аватара.
    Изображение загружается в Cloudinary и URL аватара пользрвателя обновляется
    в базе данных
    Обновленная информаци о пользователе кешируется для быстрого доступа

    Args:
        file (UploadFile): файл изображения аватара для загрузки.
        user (Users): текущий аутентифицированный пользователь, полученный
        через зависимось
        db (AsyncSession): сессия базы данных полученнач через зависимость

    Returns:
        UserResponse: обновленну информацию о пользоватле с новым URL автара.
    """
    public_id = f'uid43/{user.email}'
    resurs = cloudinary.uploader.upload(
        file.file,
        public_id=public_id,
        owerride=True
    )
    resurl_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250,
        height=250,
        crop='fill',
        version=resurs.get('version')
    )
    user = await repo_users.update_avatar_url(
        user.email,
        resurl_url,
        db
    )
    service.auth.cashe.set(user.email, pickle.dumps(user))
    service.auth.cashe.expire(user.email, 500)
    return user

@router.get('/confirmed_email/{token}')
async def confirmed_email(
    token:str, 
    db:AsyncSession=Depends(get_connection_db)):
    """
    Обработка подтверждения электронной почты с использованием токена.

    Этот эндпоинт проверяет токен подтверждения электронной почты, обновляет
    статус подтверждения пользователя и аннулирует использованный токен

    Args:
        token (str): Токен подтверждения электронной почты.
        db (AsyncSession, optional): Зависимость сессии базы данных.

    Returns:
        dict: Сообщение, указывающее результат процесса подтверждения.

    Raises:
        HTTPException:Если пользователь не найден или произошла ошибка проверки.
    """
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
    Получение информации о текущем аутентифицированном пользователе.

    Этот эндпоинт позволяет аутентифицированному пользователю получить
    собственную информацию. Запрос должен включать действительный токен доступа
    в заголовке Authorization. Применяется ограничение частоты запросов: 1 запрос
    каждые 20 секунд
    Args:
        user (Users): Текущий аутентифицированный пользователь, полученный через
        зависимость.
    
    Returns:
        Users: Информация о текущем аутентифицированном пользователе.

    Raises:
        HTTPException: Если происходит ошибка при получении информации о
    пользователе или превышено количество запросов
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
    """
    Маршрут для отслеживания открытия письма получателем.

    Этот эндпоинт используется для проверки, открыл ли получатель письмо.
    В письме содержится статический прозрачный пиксель, который вызывает
    запрос на сервер при открытии письма в браузере.

    Args:
        username (str): Имя пользователя, связанное с запросом.
         response (Response): Объект ответа, используемый для настройки HTTP-ответа.
         db (AsyncSession): Асинхронная сессия базы данных, полученная через зависимость.

    Returns:
        FileResponse: Изображение прозрачного пикселя, используемое для отслеживания.
    """
    logger.info(f'{username} open verifivation email')
    return FileResponse(
        "app/templates/static/open_check.png", 
        media_type="image/png", 
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"
        },
        content_disposition_type="inline")

@router.post('/request_email')
async def request_email(body:ReauestEmail,request:Request,
                        db:AsyncSession=Depends(get_connection_db)):
    """
    Повторная отправка email для подтверждения.

    Этот эндпоинт позволяет повторно отправить письмо для подтверждения
    электронной почты, если пользователь еще не подтвердил свой email.

    Args:
        body (ReauestEmail): Данные запроса, содержащие email пользователя.
        request (Request): Объект запроса, содержащий информацию о запросе.
        db (AsyncSession): Асинхронная сессия базы данных, полученная через зависимость.

    Returns:
        dict: Сообщение о статусе отправки email.

    Raises:
        HTTPException: Если email уже подтвержден.
    """
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
    """
    Отображение формы для сброса пароля.

    Этот эндпоинт отображает HTML-форму для ввода нового пароля,
    используя токен сброса пароля для верификации.

    Args:
        request (Request): Объект запроса, содержащий информацию о запросе.
        token (str): Токен сброса пароля.

    Returns:
        TemplateResponse: HTML-страница с формой для ввода нового пароля.

    Raises:
        HTTPException: Если токен недействителен или истек.
    """
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
    """
    Смена пароля пользователя.

    Этот эндпоинт позволяет пользователю сменить пароль, используя токен
    сброса пароля. Новый пароль должен отличаться от старого.

    Args:
        request (Request): Объект запроса, содержащий информацию о запросе.
        body (ConfirmPassword): Данные запроса, содержащие токен и новый пароль.
        db (AsyncSession): Асинхронная сессия базы данных, полученная через зависимость.

    Returns:
        dict: Сообщение о успешном обновлении пароля.

    Raises:
        HTTPException: Если токен недействителен, пользователь не найден,
        или новый пароль совпадает со старым.
    """
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
    
@router.patch('/avatar', response_model=UserResponse,
              dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def load_new_avatar(
    file:UploadFile = File(),
    user:Users = Depends(service.auth.get_current_user),
    db:AsyncSession = Depends(get_connection_db)):
    """
    Обработка загрузки нового аватаря для текущего пользователя .

    Этот эндпоинт позволяет аутентифицированному пользователю загрузать
    новое изображение аватара. Изабражение загружаетьс с Cloudinary и URL
    аватара пользователя обновляеться в базе данных.Обновленная информация о
    пользователе кешируется для бытрого доступа

    Args:
        file (UploadFile): Файл изображения аватара для загрузки.
        user (Users): Текущий аутентифицированный пользователь, полученный
        через зависимость.
        db (AsyncSession): Сессия базы данных, полученная через зависимость.


    Returns:
        UserResponse: Обновленная информация о пользователе с новым URL аватара.

    Raises:
        HTTPException: Если пользователь не найден или произошла ошибка загрузки.
    """
    public_id = f'folder/{user.email}'
    resurs = cloudinary.uploader.upload(file.file, public_id, owerride=True)
    resurs_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250,
        height=250,
        crop='fill',
        version=resurs.get('version')
    )
    user = await repo_users.update_avatar_url(user.email, resurs_url, db)
    service.auth.cashe.set(user.email, pickle.dumps(user))
    service.auth.cashe.expire(user.email, 500)
