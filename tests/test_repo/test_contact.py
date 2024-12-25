import unittest
from app.repository import contacts as cont
from app.models.base_model import Users, Contacts
from sqlalchemy.ext.asyncio import AsyncSession
from app.shemas.contact import CreateContact, ContactResponse
from unittest.mock import MagicMock, AsyncMock




class TestAsyncContact(unittest.IsolatedAsyncioTestCase):
    """
    протестированные функции:
        get_contact(limit, offset, db, user)
        get_contact_id(contact_id, db, user)
        create contact(body, db, user)
        delete contact(contact, db)
        update contact(body, contact, db)
    """

    def setUp(self):
        """
        базовый настройки для каждого теста отдельно
        применяются перед каждым тестом
        """
        self.User = Users(id=1, username='test_user', password='123')
        self.session = AsyncMock(spec=AsyncSession)
    
    async def test_get_contact(self):
        limit = 10
        offset = 0
        contacts  = [
            Contacts(id=1,first_name='test_first',last_name='test_last',
                     email='test@gmail.com', phone_number='+123'),
            Contacts(id=2,first_name='test_first2',last_name='test_last2',
                     email='test2@gmail.com', phone_number='+321'),
            Contacts(id=3,first_name='test_first3',last_name='test_last3',
                     email='test3@gmail.com', phone_number='+312')
        ]
        mocked_contact = MagicMock()
        mocked_contact.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contact
        result = await cont.get_contacts(limit, offset, self.session, self.User)
        self.assertEqual(result, contacts)

    async def test_get_contact_id(self):
        contact_id = 2
        mocked_contact = Contacts(
            id=contact_id,first_name='test_first',last_name='test_last',
            email='test@gmail.com', phone_number='+123'
        )
        mocked_query_result = MagicMock()
        mocked_query_result.scalar_one_or_none.return_value = mocked_contact
        self.session.execute.return_value = mocked_query_result
        result = await cont.get_contact_by_id(contact_id,self.session,self.User)
        self.session.execute.assert_called_once()
        self.assertEqual(result, mocked_contact)
    
    async def test_get_contact_id_faile(self):
        contact_id = 2
        mocked_query_results = MagicMock()
        mocked_query_results.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mocked_query_results
        result = await cont.get_contact_by_id(contact_id, self.session, self.User)
        self.session.execute.assert_called_once()
        self.assertIsNone(result)  

    async def test_create_contact(self):
        body = CreateContact(
            first_name='test_first_name',
            last_name='test_last_name',
            email = 'test@exexmple.com',
            note = 'test_notes',
            phone_number = '+380672730962',
            date_birthday = '1998-08-01'
        )
        result = await cont.create_contact(body, self.session, self.User)
        self.assertIsInstance(result, Contacts)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)

    async def test_update_contact(self):
        #входные данные
        body = ContactResponse(
            id=1,
            first_name='test_first_name',
            last_name='test_last_name',
            email = 'test@exexmple.com',
            note = 'testing notes',
            phone_number = '+380672730962',
            date_birthday = '1998-08-01'
        )
        #обьект контакта для обновления
        contact = Contacts(
            id=1,
            first_name='old_name',
            last_name='old_last_name',
            email='old@example.com',
            note='old note',
            phone_number='+1234567890',
            date_birthday='1990-01-01'
        )

        #мок методов сессии
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()

        #вызов функции
        result = await cont.update_contact(body, contact, self.session)

        self.assertIsInstance(result, Contacts)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.date_birthday, body.date_birthday)
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once_with(contact)
    
    async def test_deleted_contact(self):
        """тест на удаление контакта
        тестируется вызов методов delete commit"""
        contact_id = 1
        fail_contact_input = Contacts(
            id=contact_id,
            first_name='test_first_name',
            last_name='test_last_name',
            email = 'test@exexmple.com',
            phone_number = '+380672730962',
            date_birthday = '1998-08-01',
            users_id=self.User.id
        )
        
        await cont.delete_contact(fail_contact_input, self.session)
        self.session.delete.assert_awaited_once_with(fail_contact_input)
        self.session.commit.assert_awaited_once()

    async def test_delete_contact_not_called(self):
        """проверка что методы сессии не вызывабтся без вызова функции"""
        self.session.delete.assert_not_awaited()
        self.session.commit.assert_not_awaited()