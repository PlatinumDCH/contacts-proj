from unittest.mock import Mock, patch, AsyncMock, MagicMock

import pytest

from app.services.base import service


def test_get_me(client, get_token, monkeypatch):
    monkeypatch.setattr("app.routers.auth.Request.client", MagicMock(host="127.0.0.1"))
    with patch.object(service.auth, 'cashe') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("api/users/me", headers=headers)
        assert response.status_code == 200, response.text