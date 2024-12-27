from unittest.mock import AsyncMock, patch
import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from app.repository import users as repo_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.shemas.user import UserSchema
from app.models.base_model import UserTokensTable, Users

# from sqlalchemy.future import select, update
from sqlalchemy import update, select
from app.config.configurate import settings
from app.config.logger import logger

class TestAsyncContact(unittest.IsolatedAsyncioTestCase):
    """
    протестированные функции:
        get_user_by_email(email, db)
            - found
            - not found
        create_user(body, db)
            - avatar_url ok
            - avatar_url fail
        confirmed_user_email
        update_user_password
        update_avatar_url

    """

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user = Users(
            id=1,
            username="t_user",
            password="123",
            email="test@gmail.com",
            confirmed=True,
            avatar=None,
        )
        self.user_token = UserTokensTable(
            user_id=self.user.id,
            refresh_token="refresh_token_value",
            reset_password_token="re_pass_token_value",
            email_token="email_toke_value",
        )
        self.test_body = UserSchema(
            email="test@gmail.com", password="123", username="t_user"
        )
        self.email = "test@gmail.com"

    async def test_get_user_by_email_found(self):
        """пользователь найден в базе данных"""
        # настройка мока для возврата пользователя с бд
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mock_result

        result = await repo_user.get_user_by_email(self.email, self.session)

        # проверка что результат соответсвует ожидаемому
        self.assertEqual(result, self.user)
        self.assertEqual(result.email, self.email)
        self.session.execute.assert_called_once()

    async def test_get_user_by_email_not_found(self):
        """пользователь не найден в базе данных"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mock_result

        result = await repo_user.get_user_by_email(self.email, self.session)

        self.assertEqual(result, None)
        self.session.execute.assert_called_once()

    @patch("app.repository.users.Gravatar")
    async def test_create_user(self, mock_gravatar):
        """
        имитация работы Gravatar
            замена работы Gravatar
                g = Gravatart(body.email)
                avatar:str = g.get_image() => face url
        """
        grav_url = "testing_url"

        # настройка мока для граватара
        fake_gravatar = mock_gravatar.return_value
        fake_gravatar.get_image.return_value = grav_url

        # проверка работы мока
        avatar_url = fake_gravatar.get_image()
        self.assertEqual(avatar_url, grav_url)

        # создаем нового пользователя с фейковыйм аватаром
        new_user = Users(**self.test_body.model_dump(), avatar=avatar_url)
        self.assertEqual(new_user.avatar, avatar_url)
        self.assertEqual(new_user.email, self.test_body.email)

        # тест содание пользователя
        result = await repo_user.create_user(self.test_body, self.session)

        self.assertEqual(result.avatar, grav_url)
        self.assertEqual(result.email, self.test_body.email)
        self.assertEqual(result.id, new_user.id)
        self.assertEqual(result.username, new_user.username)
        self.assertEqual(result.password, new_user.password)
        self.assertEqual(result.email, new_user.email)
        self.assertEqual(result.avatar, new_user.avatar)

        # проверка вызовов методова сессии
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()

    @patch("app.repository.users.Gravatar.get_image")
    async def test_create_usre_avatar_error(self, mock_gravatar):
        mock_gravatar.side_effect = Exception("Gravatar error")
        result = await repo_user.create_user(self.test_body, self.session)

        self.assertIsNone(result.avatar)
        self.assertEqual(result.email, self.test_body.email)

        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()

    @patch("app.repository.users.get_user_by_email")
    async def test_confirmed_user_email(self, mock_get_email):
        """chamge fill confirm=True in user table"""
        mock_get_email.return_value = self.user

        await repo_user.confirmed_email(self.user.email, self.session)

        self.assertTrue(self.user.confirmed)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()

    @patch("app.repository.users.get_user_by_email")
    async def test_update_user_password(self, mock_get_email):
        """change fill password=>new_value in user table"""
        mock_get_email.return_value = self.user

        new_password = "new_password"
        await repo_user.update_user_password(
            user=self.user, password=new_password, db=self.session
        )

        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()
        self.assertEqual(self.user.password, new_password)

    @patch("app.repository.users.get_user_by_email")
    async def test_update_avatar_url(self, mock_get_email):
        """change fill acatart=>new_url in user table"""
        mock_get_email.return_value = self.user
        new_graw_url = "new_graw_url"

        await repo_user.update_avatar_url(
            email=self.user.email, url=new_graw_url, db=self.session
        )

        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()
        self.assertEqual(self.user.avatar, new_graw_url)

    @patch("app.repository.users.select")
    async def test_get_token(self, fake_select):
        """
        получить токен из базы данных
        дкоратор @patch для замены реальной функции select
        изоляция теста от базы данных
        fake_select.return_value - задает какой запрос будет сгенерирован
        при вызове select.Имитация запроса, который ищет записи в таблице
        ---
        настройка возвращаемого возвращаемого значения сессии
        """
        fake_select.return_value = select(UserTokensTable).filter_by(
            user_id=self.user.id
        )
        fake_result = MagicMock()
        fake_result.scalar_one_or_none.return_value = self.user_token
        self.session.execute.return_value = fake_result

        token_type = settings.refresh_token
        result = await repo_user.get_token(self.user, token_type, self.session)
        self.assertEqual(result, self.user_token.refresh_token)
        self.session.execute.assert_called_once()

    @patch("app.repository.users.select")
    async def test_get_token_not_found(self, fake_select):
        """токен не найден"""
        fake_select.return_value = select(UserTokensTable).filter_by(
            user_id=self.user.id
        )

        fake_result = MagicMock()
        fake_result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = fake_result

        result = await repo_user.get_token(
            self.user, settings.refresh_token, self.session
        )
        self.assertIsNone(result)
        self.session.execute.assert_called_once()

    @patch("app.repository.users.select")
    async def test_get_token_invalid_token(self, fake_select):
        fake_select.return_value = select(UserTokensTable).filter_by(
            user_id=self.user.id
        )

        fake_result = MagicMock()
        fake_result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = fake_result
        result = await repo_user.get_token(
            self.user, settings.refresh_token, self.session
        )
        self.assertIsNone(result)
        self.session.execute.assert_called_once()

    @patch("app.repository.users.select")
    async def test_get_token_db_error(self, fake_select):
        fake_select.return_value = select(UserTokensTable).filter_by(
            user_id=self.user.id
        )
        self.session.execute.side_effect = Exception("DB error")

        token_type = settings.refresh_token
        with self.assertRaises(Exception) as context:
            await repo_user.get_token(self.user, token_type, self.session)

        self.assertEqual(str(context.exception), "DB error")
        self.session.execute.assert_called_once()

    @patch("app.repository.users.select")
    @patch("app.repository.users.update")
    async def test_update_token_success(self, mock_update, mock_select):
        """
        успешно обновление токена на новой значение
        """

        # настройка мока для для select
        mock_select.return_value = select(UserTokensTable).filter_by(
            user_id=self.user.id
        )

        # настройка мока для выполнения запроса
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.user_token
        self.session.execute.return_value = mock_result

        # настройка мока для update
        mock_update.return_value = update(UserTokensTable).where(
            UserTokensTable.user_id == self.user.id
        )
        new_token_value = 'xxx'
        token_type = settings.refresh_token

        await repo_user.update_token(
            user=self.user,
            token=new_token_value,
            token_type=token_type,
            db=self.session,
        )

        self.assertEqual(self.user_token.refresh_token, new_token_value)
        self.session.execute.assert_called()
        self.assertEqual(self.session.execute.call_count, 2)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()
    
    @patch("app.repository.users.select")
    @patch("app.repository.users.update")
    async def test_update_token_none(self, fk_update, fk_select):

        fk_select.return_value = select(UserTokensTable).filter_by(
            user_id=self.user.id
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.user_token
        self.session.execute.return_value = mock_result

        fk_update.return_value = update(UserTokensTable).where(
            UserTokensTable.user_id == self.user.id
        )
        new_token_value = None
        token_type = settings.refresh_token
        await repo_user.update_token(self.user, new_token_value, 
                                     token_type, self.session)
        
        self.assertEqual(self.user_token.refresh_token, new_token_value)
        self.session.execute.assert_called()
        self.assertEqual(self.session.execute.call_count, 2)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()

    @patch("app.repository.users.select")
    @patch("app.repository.users.update")
    async def test_update_token_db_error(self, fk_update, fk_select):
        fk_select.return_value = select(UserTokensTable).filter_by(
            user_id=self.user.id
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.user_token
        self.session.execute.return_value = mock_result

        fk_update.return_value = update(UserTokensTable).where(
            UserTokensTable.user_id == self.user.id
        )
        new_token_value = 'xxx'
        token_type = settings.refresh_token
        self.session.execute.side_effect = Exception("DB error")
        with self.assertRaises(Exception) as context:
            await repo_user.update_token(
                self.user,
                new_token_value,
                token_type,
                self.session
            )
        
        self.assertEqual(str(context.exception), "DB error")
        self.session.rollback.assert_called_once()
        self.session.commit.assert_not_called()
        self.session.refresh.assert_not_called()
