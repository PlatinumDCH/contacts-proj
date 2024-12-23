from fastapi import Depends, APIRouter, HTTPException, Path, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.get_session import get_connection_db
import app.repository.contacts as repo_contacts
from app.shemas.contact import CreateContact, ContactResponse

router = APIRouter(prefix="/contacts", tags=["contacts"])

"""
get_all_contacts  get http://127.0.0.1:8000/contacts/all 
    сделать запрос к бд, получить все контакты
create_contact post http://127.0.0.1:8000/contacts/
    (body:json, session_obj:AsyncSession)
{
  "first_name": "string",
  "last_name": "string",
  "email": "user2@example.com",
  "note": "string",
  "phone_number": "string"
    } { validate shema } -> запрос к бд на создание контакта
get_contact get http://127.0.0.1:8000/contacts/{contacts_id}
update_contacts put http://127.0.0.1:8000/contacts/{contacts_id}
    (id:int, body:json, session)
    1.проверить есть ли такой контак по id
    2.get_contact вернет объект конакта
    3.используя body обновить котакт в базе данных
    4.вернуть обьект контакта
delete_contacts delete http://127.0.0.1:8000/contacts/{contacts_id}
    (id:int, session)
    1.проверить что такой контакт есть 
    2.get_contact вернет обьект контакта
    3.запрос к базе данных на удаление контакта
"""


@router.get("/all", response_model=list[ContactResponse])
async def get_all_contacts(
    db: AsyncSession = Depends(get_connection_db)
    ):
    contacts = await repo_contacts.get_contacts(db)
    return contacts

@router.post("/", response_model=ContactResponse,status_code = status.HTTP_201_CREATED)
async def create_contact(
        body:CreateContact,
        db: AsyncSession = Depends(get_connection_db),
        )->ContactResponse:
    contact = await repo_contacts.create_contact(
        body,
        db
    )
    return contact


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id:int = Path(ge=1),
    db:AsyncSession = (Depends(get_connection_db))
):
    #logic work in db
    contact =  await repo_contacts.get_contact_by_id(
        contact_id=contact_id,
        db=db
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
        ):
    curent_contact = await repo_contacts.get_contact_by_id(
        contact_id=contact_id,
        db=db
    )
    if curent_contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='not found contact, fail id'
        )
    update_contact = await repo_contacts.update_contact(
        body,
        curent_contact,
        db
    )
    return update_contact

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
        contact_id:int,
        db: AsyncSession = Depends(get_connection_db),
        ):
    curent_contact = await repo_contacts.get_contact_by_id(
        contact_id=contact_id,
        db=db
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
