from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.get_session import get_connection_db


router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/", response_model=None)
async def get_contacts(
    limit: None,
    offset: None,
    db: AsyncSession = Depends(get_connection_db),
    ):
    """получить контакты"""
    contacts = None
    return contacts

@router.get("/all", response_model=None)
async def get_all_contacts(
    limit = None, 
    offset = None,
    db = None, 
    ):
    """ вернуть все контакты"""
    contacts = None
    return contacts

@router.post("/", response_model=None)
async def create_contact(
        body,
        db: AsyncSession = Depends(get_connection_db),
        ):
    """
    создать контакт
    """
    contact = None
    return contact

@router.get('/search', response_model=None)
async def search_contacts(
        first_name,
        last_name,
        email,
        db:AsyncSession = Depends(get_connection_db),
       ):
    """
    Поиск контактов по first_name, last_name, email  GET
    """
    contacts = None
    #login search
    if not contacts:
        raise HTTPException(status_code=404, detail='Not contacts found')
    return contacts

@router.get('/upcoming_birthdays', response_model=None)
async def upcoming_birthdays(db: AsyncSession = Depends(get_connection_db),
                             ):
    """
    получить список контактов ДР+7д
    """
    # logic work to db
    upcoming_contacts = None
    return upcoming_contacts

@router.get("/{contact_id}", response_model=None)
async def get_contact(
    contact_id
):
    """
    взять контакт по id
    """
    #logic work in db
    contact = None
    return contact


@router.put("/{contact_id}")
async def update_contact(
        body,
        contact_id,
        db: AsyncSession = Depends(get_connection_db),
        ):
    """ 
    Обновить контакт по id PUT
    http://127.0.0.1:8000/api/contacts/6
    raw JSON: ContactCreateShema
    auteticate: barer token: access token
    """
    
    return {}

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
        contact_id,
        db: AsyncSession = Depends(get_connection_db),
        ):
    """
    Удалить контакт по id
    http://127.0.0.1:8000/api/contacts/5
    auteticate: barer token: access token
    """
    # удалить контакт с базы даных
    
