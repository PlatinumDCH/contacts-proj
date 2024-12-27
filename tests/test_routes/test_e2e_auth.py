from unittest.mock import Mock

import pytest
from sqlalchemy import select

from app.models.base_model import Users
from tests.conftest import TestingSessionLocal
from app.services.base import service


user_data = {
    "username": "agent", 
    "email": "agent007@gmail.com", 
    "password": "123"
    }



# def test_signup(client, monkeypatch):

#     pocess_email_confirmation = Mock()
#     monkeypatch.setattr("app.routers.auth", service.email.pocess_email_confirmation)
#     response = client.post("api/auth/signup", json=user_data)
#     assert response.status_code == 201, response.text
#     data = response.json()
#     assert data["username"] == user_data["username"]
#     assert data["email"] == user_data["email"]
#     assert "password" not in data
#     assert "avatar" in data
