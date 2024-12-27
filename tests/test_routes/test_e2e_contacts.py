from unittest.mock import Mock, patch, MagicMock

import pytest

from app.services.base import service


def test_get_todos(client, get_token, monkeypatch):
    monkeypatch.setattr("app.routers.auth.Request.client", MagicMock(host="127.0.0.1"))
    with patch.object(service.auth, 'cashe') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("api/contacts/all", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 0


def test_create_todo(client, get_token, monkeypatch):
    monkeypatch.setattr("app.routers.auth.Request.client", MagicMock(host="127.0.0.1"))
    with patch.object(service.auth, 'cashe') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("api/contacts", headers=headers, json={
            "first_name": "test_first",
            "last_name": "test_second",
            "email": "user@example.com",
            "note": "string",
            "phone_number": "string",
            "date_birthday": "2024-12-27"
            }
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert "id" in data
        assert data["note"] == "string"
        assert data["first_name"] == "test_first"