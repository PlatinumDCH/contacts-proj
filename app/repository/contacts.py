from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.base_model import Contacts
from typing import Sequence
from app.shemas.contact import CreateContact
from app.models.base_model import Contacts

"""
get_contacts(db:AsyncSession)
    сформировать запрос к базе данных
    выполнить запрос
    получить все обьекты с запроса
    вернуть всех пользователей
"""

async def get_contacts(db:AsyncSession):
    query = select(Contacts) 
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
async def create_contact(body:CreateContact,db:AsyncSession)->Contacts:
    contact = Contacts(**body.model_dump(exclude_unset=True))
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact

