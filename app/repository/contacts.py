from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.base_model import Contacts
from typing import Sequence
from app.models.base_model import Users
from app.shemas.contact import CreateContact
from app.models.base_model import Contacts

"""
get_contacts(db:AsyncSession)
    сформировать запрос к базе данных
    выполнить запрос
    получить все обьекты с запроса
    вернуть всех пользователей
"""

async def get_contacts(limit:int,offset:int,db:AsyncSession, user:Users):
    query = select(Contacts).where(Contacts.users_id==user.id).offset(offset).limit(limit) 
    result = await db.execute(query)
    contacts:Sequence[Contacts] = result.scalars().all()
    return contacts

"""
create contact(body:ContactCreatShema, db)
        создать обьект контакт Contacts(
                    body.first_name = first_name,
                    body.last_name = last_name,
                    body.email = email,
                    body.notes = notes,
                    body.phone_number = phone_number)
        < **body.model_dump(exclude_unset=True) = автоматически передаст только заданные поля >       
        добавить в дазу данных новый обьект
        асинхронно закомитить
        асинхронно обновить контакты
        вернуть обьект контакт
"""
async def create_contact(body:CreateContact,db:AsyncSession, user:Users)->Contacts:
    contact = Contacts(**body.model_dump(exclude_unset=True), users_id=user.id)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact

"""
получить контакт по id(id_contact:int, connecting database)
    запрос
    подожди выполнить запрос 
    вернуть первый контакт 
"""

async def get_contact_by_id(contact_id:int, db:AsyncSession, user:Users)->Contacts|None:
    query = (
        select(Contacts)
        .filter(Contacts.id == contact_id, Contacts.users_id == user.id)
    )
    contact = await db.execute(query)
    return contact.scalar_one_or_none()

"""
update_contact(body, contact-obj, session):
    обновить объект контакта
    законмитить
    рефрешнуть
    вернуть обьект контакта
"""

async def update_contact(body, contact:Contacts, db:AsyncSession, user:Users)->Contacts:
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(contact, key, value) 
    await db.commit()
    await db.refresh(contact)
    return contact

async def delete_contact(contact:Contacts, db:AsyncSession):
    await db.delete(contact)
    await db.commit()

    