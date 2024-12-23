from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.get_session import get_connection_db
import app.repository.contacts as repo_contacts
from app.shemas.contact import CreateContact

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/all", response_model=None)
async def get_all_contacts(
    db: AsyncSession = Depends(get_connection_db)
    ):
    """получить контакты"""
    contacts = await repo_contacts.get_contacts(db)
    return contacts


"""
создать обьект контакта
create_contact(тело, конект к базе данных)
    обьект контакта = подожди создать контакт в базе данных(
    тело,
    сессия базы данных)
тело в виде json валидируется pydantic
    {
  "first_name": "string",
  "last_name": "string",
  "email": "user2@example.com",
  "note": "string",
  "phone_number": "string"
    }
"""

@router.post("/", response_model=None)
async def create_contact(
        body:CreateContact,
        db: AsyncSession = Depends(get_connection_db),
        ):
    contact = await repo_contacts.create_contact(
        body,
        db
    )
    return contact

# @router.get('/search', response_model=None)
# async def search_contacts(
#         first_name,
#         last_name,
#         email,
#         db:AsyncSession = Depends(get_connection_db),
#        ):
#     """
#     Поиск контактов по first_name, last_name, email  GET
#     """
#     contacts = None
#     #login search
#     if not contacts:
#         raise HTTPException(status_code=404, detail='Not contacts found')
#     return contacts

# @router.get('/upcoming_birthdays', response_model=None)
# async def upcoming_birthdays(db: AsyncSession = Depends(get_connection_db),
#                              ):
#     """ 
#     получить список контактов ДР+7д
#     """
#     # logic work to db
#     upcoming_contacts = None
#     return upcoming_contacts

# @router.get("/{contact_id}", response_model=None)
# async def get_contact(
#     contact_id
# ):
#     """
#     взять контакт по id
#     """
#     #logic work in db
#     contact = None
#     return contact


# @router.put("/{contact_id}")
# async def update_contact(
#         body,
#         contact_id,
#         db: AsyncSession = Depends(get_connection_db),
#         ):
#     """ 
#     Обновить контакт по id PUT
#     http://127.0.0.1:8000/api/contacts/6
#     raw JSON: ContactCreateShema
#     auteticate: barer token: access token
#     """
    
#     return {}

# @router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_contact(
#         contact_id,
#         db: AsyncSession = Depends(get_connection_db),
#         ):
#     """
#     Удалить контакт по id
#     http://127.0.0.1:8000/api/contacts/5
#     auteticate: barer token: access token
#     """
#     # удалить контакт с базы даных

