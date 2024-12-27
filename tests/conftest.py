import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
import asyncio
import pytest_asyncio

from app.main import app
from app.db.get_session import get_connection_db
from app.models.base_model import BaseModel, Users
from app.services.base import service

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False},
    poolclass=StaticPool

)
test_user = {
    "username": "test", 
    "email": "deadpool@example.com", 
    "password": "123",
    }

TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.drop_all)
            await conn.run_sync(BaseModel.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = service.password.get_password_hash(test_user["password"])
            current_user = Users(username=test_user["username"], email=test_user["email"], password=hash_password,
                                confirmed=True, role="ADMIN")
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    # Dependency override

    async def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        except Exception as err:
            
            await session.rollback()
            raise #повторно выбрасить исключение
        finally:
            await session.close()

    app.dependency_overrides[get_connection_db] = override_get_db

    yield TestClient(app)


@pytest_asyncio.fixture()
async def get_token():
    token = await service.jwt.create_access_token(data={"sub": test_user["email"]})
    return token


@pytest.fixture
def mock_password_service(monkeypatch):
    # Замокировать метод get_password_hash
    def mock_get_password_hash(password):
        return "mocked_hashed_password"
    monkeypatch.setattr("app.services.base.service.password.get_password_hash", mock_get_password_hash)
