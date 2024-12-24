from fastapi import Depends, APIRouter, HTTPException, Path, status
from fastapi import Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.get_session import get_connection_db
import app.repository.contacts as repo_contacts
from app.services.base import service
from app.models.base_model import Users,Contacts
from app.shemas.contact import CreateContact, ContactResponse

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/all", response_model=list[ContactResponse])
async def get_all_contacts(
    limit:int = Query(10, ge=10, le=500),
    offset:int = Query(0, ge=0, le=10),
    db: AsyncSession = Depends(get_connection_db),
    user:Users=Depends(service.auth.get_current_user)
    )->list[Contacts]|None:
    """
    Получение всех контактов пользователя с пагинацией.

    Этот эндпоинт возвращает список контактов, принадлежащих текущему
    аутентифицированному пользователю, с поддержкой пагинации.

    Args:
        limit (int): Максимальное количество контактов для возврата.
        offset (int): Смещение для пагинации.
        db (AsyncSession): Асинхронная сессия базы данных, полученная через зависимость.
        user (Users): Текущий аутентифицированный пользователь.

    Returns:
        list[Contacts] | None: Список контактов или None, если контакты не найдены.
    """
    contacts = await repo_contacts.get_contacts(limit,offset,db,user)
    return contacts

@router.post("/", response_model=ContactResponse,status_code = status.HTTP_201_CREATED)
async def create_contact(
        body:CreateContact,
        db: AsyncSession = Depends(get_connection_db),
        user:Users = Depends(service.auth.get_current_user),
        )->ContactResponse:
    """
    Создание нового контакта для пользователя.

    Этот эндпоинт позволяет создать новый контакт для текущего
    аутентифицированного пользователя.

    Args:
        body (CreateContact): Данные для создания нового контакта.
        db (AsyncSession): Асинхронная сессия базы данных, полученная через зависимость.
        user (Users): Текущий аутентифицированный пользователь.

    Returns:
        ContactResponse: Информация о созданном контакте.
    """
    contact = await repo_contacts.create_contact(
        body,
        db,
        user
    )
    return contact


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id:int = Path(ge=1),
    db:AsyncSession = (Depends(get_connection_db)),
    user:Users = Depends(service.auth.get_current_user)
):
    """
    Получение информации о контакте по его ID.

    Этот эндпоинт возвращает информацию о контакте, принадлежащем
    текущему аутентифицированному пользователю, по его ID.

    Args:
        contact_id (int): ID контакта.
        db (AsyncSession): Асинхронная сессия базы данных, полученная через зависимость.
        user (Users): Текущий аутентифицированный пользователь.

    Returns:
        ContactResponse: Информация о контакте.

    Exception:
        HTTPException: Если контакт не найден.
    """
    #logic work in db
    contact =  await repo_contacts.get_contact_by_id(
        contact_id=contact_id,
        db=db,
        user=user
    )
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='not found ')
    return contact



@router.put("/{contact_id}")
async def update_contact(
        body:CreateContact,
        contact_id:int,
        db: AsyncSession = Depends(get_connection_db),
        user:Users = Depends(service.auth.get_current_user)
        ):
    """
    Обновление информации о контакте по его ID.

    Этот эндпоинт обновляет информацию о контакте, принадлежащем
    текущему аутентифицированному пользователю, по его ID.

    Args:
        body (CreateContact): Новые данные для обновления контакта.
        contact_id (int): ID контакта.
        db (AsyncSession): Асинхронная сессия базы данных, полученная через зависимость.
        user (Users): Текущий аутентифицированный пользователь.

    Returns:
        Обновленный контакт.

    Exceptions:
        HTTPException: Если контакт не найден.
    """
    curent_contact = await repo_contacts.get_contact_by_id(
        contact_id=contact_id,
        db=db,
        user=user
    )
    if curent_contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='not found contact, fail id'
        )
    update_contact = await repo_contacts.update_contact(
        body,
        curent_contact,
        db,
        user
    )
    return update_contact

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
        contact_id:int,
        db: AsyncSession = Depends(get_connection_db),
        user:Users = Depends(service.auth.get_current_user)
        ):
    """
    Удаление контакта по его ID.

    Этот эндпоинт удаляет контакт, принадлежащий текущему
    аутентифицированному пользователю, по его ID.

    Args:
        contact_id (int): ID контакта.
        db (AsyncSession): Асинхронная сессия базы данных, полученная через зависимость.
        user (Users): Текущий аутентифицированный пользователь.

    Returns:
        dict: Сообщение о статусе удаления контакта.

    Exceptions:
        HTTPException: Если контакт не найден или удаление невозможно из-за связанных данных.
    """
    curent_contact = await repo_contacts.get_contact_by_id(
        contact_id=contact_id,
        db=db,
        user=user
    )
    if curent_contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='not found contact, fail id'
        )
    try:
        await repo_contacts.delete_contact(curent_contact, db)
        return {
            'detail':'contact was deleted'
        }
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Cannot delete contact due to related data'
        )
