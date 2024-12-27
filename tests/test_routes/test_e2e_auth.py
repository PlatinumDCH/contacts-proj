from unittest.mock import MagicMock, AsyncMock
from app.models.base_model import Users
from tests.conftest import TestingSessionLocal
from fastapi import status
from app.config import messages
import pytest
from sqlalchemy import select


user_data = {
        'username':'test',
        'email':'test@gmail.com',
        'password':'123',
    }

def test_create_user(client, monkeypatch):
    """успешная регистрация пользователя на сайте"""
    mock_email_service = AsyncMock()
    monkeypatch.setattr("app.routers.auth.Request.client", MagicMock(host="127.0.0.1"))
    monkeypatch.setattr("app.services.base.service.email.send_email", mock_email_service)

    response = client.post("/api/auth/signup",json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password" not in data

def test_user_already_exists(client, monkeypatch):
    """тест, такой пользователь уже есть в базе данных"""
    exists_user = {
        'username':'test',
        'email':'test@gmail.com',
        'password':'123',
    }
    mock_email_service = AsyncMock()
    monkeypatch.setattr("app.routers.auth.Request.client", MagicMock(host="127.0.0.1"))
    monkeypatch.setattr("app.services.base.service.email.send_email", mock_email_service)
    response = client.post("/api/auth/signup",json=exists_user)

    assert response.status_code == status.HTTP_409_CONFLICT, response.text
    data = response.json()
    assert data["detail"] == messages.ACCOUNT_EXIST


def test_not_confirmed_login(client, monkeypatch):
    """проверка того что почта пользователя не подтверждена"""
    monkeypatch.setattr("app.routers.auth.Request.client", MagicMock(host="127.0.0.1"))
    response = client.post(
        "api/auth/login",
        data={
                "username": user_data.get("email"), 
                "password": user_data.get("password")
            }
            )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Account not confirmed, check email"

@pytest.mark.asyncio
async def test_login(client, monkeypatch):
    """тест успешного логина"""
    monkeypatch.setattr("app.routers.auth.Request.client", MagicMock(host="127.0.0.1"))
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(Users).where(Users.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("email"), 
            "password": user_data.get("password")
            }
            )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data

confirmed_user = {
        'username':'test',
        'email':'test@gmail.com',
        'password':'123',
    }


def test_wrong_password_login(client, monkeypatch):
    """неправильный пароль"""
    monkeypatch.setattr("app.routers.auth.Request.client", MagicMock(host="127.0.0.1"))
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("email"), 
            "password": "password"
            }
            )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid pass"

def test_wrong_email_login(client, monkeypatch):
    """неправильный email"""
    monkeypatch.setattr("app.routers.auth.Request.client", MagicMock(host="127.0.0.1"))
    response = client.post(
        "api/auth/login",
        data={
            "username": "email", 
            "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"

def test_validation_error_login(client, monkeypatch):
    """обезательное поле email не передано"""
    monkeypatch.setattr("app.routers.auth.Request.client", MagicMock(host="127.0.0.1"))
    response = client.post(
        "api/auth/login",
        data={
            "password": user_data.get("password")})
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data

def test_forgot_password(client, monkeypatch):
    """забыл пароль, отправка письма на смену пароля"""
    monkeypatch.setattr("app.routers.auth.Request.client", MagicMock(host="127.0.0.1"))
    mock_email_service = AsyncMock()
    monkeypatch.setattr("app.services.base.service.email.send_email", mock_email_service)
    
    response = client.post(
        '/api/auth/reset_password_request',
        json = {
            'email': 'test@gmail.com'
        }
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'message': 'Check you email for reset password'
    }