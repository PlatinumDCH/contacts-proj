from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.base_model import Contacts
from typing import Sequence
from app.models.base_model import Users
from app.shemas.contact import CreateContact
from app.models.base_model import Contacts

async def get_contacts(limit:int,offset:int,db:AsyncSession, user:Users):
    """
    асинхронно получает список обьектов контактов, связанных с конкретным
    пользователем
    
    Args:
        limit (int) максимальное количество контактов для получения
        offset (int) к-во контактов, которые нужно пропустить перед началом 
        сбора обьектов контакта
        db (AsyncSession) сессия базы данных, используемая для выполнения запроса
        user (Users) пользователь, чьи нонтакты нобходимо получить
    Return:
        Sequence[Contacts] последовательность обьектов контактов, принадлежащих
        указанному пользователю
    """
    query = select(Contacts).where(Contacts.users_id==user.id).offset(offset).limit(limit) 
    result = await db.execute(query)
    contacts:Sequence[Contacts] = result.scalars().all()
    return contacts

async def create_contact(body:CreateContact,db:AsyncSession, user:Users)->Contacts:
    """
    асинхронно создает новый контакт в базе данных
    
    Args:
        body (CreateContact): Схема, содержащая детали контакта.
        db (AsyncSession): Асинхронная сессия базы данных.
        user (Users): Пользователь, с которым будет связан контакт.
    Return
        Contacts: Объект только что созданного контакта
    Description:
        Эта функция принимает схему создания контакта м сессию базы данных для
        создания новой записи контакта, связанной с конкретным пользователем.
        Она добавляет новый контакт в базу данных, ассинхронно комитит изменения
        и обновляет сессию для отражения иземенений
    """
    contact = Contacts(**body.model_dump(exclude_unset=True), users_id=user.id)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact

async def get_contact_by_id(contact_id:int, db:AsyncSession, user:Users)->Contacts|None:
    """
    получить контакт по его id для конткретного пользователя.

    Args:
        contact_id (int): id контакта, который нужно получить.
        db (AsyncSession): сессия базы данных для выполнения запроса.
        user (Users): пользователь чей контакт извлекается.

    Returns:
        Contacts | None: обьект контакта,если найден иначе None.
    """
    query = (
        select(Contacts)
        .filter(Contacts.id == contact_id, Contacts.users_id == user.id)
    )
    contact = await db.execute(query)
    return contact.scalar_one_or_none()



async def update_contact(body, contact:Contacts, db:AsyncSession)->Contacts:
    """
    асинхронно обновляет данные контакта в базе данных.

    Эта функция принимает словарь с обновленными данными контакти, применяет
    изменения к указанному обьекту контакта, фиксирует изменения в дабзе данных
    и обновляет обьект контакта, чтобы отразить его акуальное состояние.

    Args:
        body: обьект содержащий обновленные данные контакта.
        contact (Contacts): обьект контакта который нужно изменить.
        db (AsyncSession): сессия базы данным используяемая для операций.
        user (Users): пользователь, связанный с контактом.

    Returns:
        Contacts: обновленный обьект контакта.
    """
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(contact, key, value) 
    await db.commit()
    await db.refresh(contact)
    return contact

async def delete_contact(contact:Contacts, db:AsyncSession):
    """
    асинхронно удаляет контакты из базы данных.

    Args:
        contact (Contacts): экземаляо контакта который нужно удалить.
        db (AsyncSession): сессия базы данных, используемая для операции.

    Returns:
        None
    """
    await db.delete(contact)
    await db.commit()

    