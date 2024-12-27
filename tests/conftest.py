import asyncio
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker, AsyncSession

from app.main import app
from app.models.base_model import Users, BaseModel
from app.db.get_session import get_connection_db
from app.services.base import service

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

test_user = {
    "username": "deadpool", 
    "email": "deadpool@example.com", 
    "password": "12345678"
    }

@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.drop_all)
            await conn.run_sync(BaseModel.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = service.password.get_password_hash(test_user["password"])
            current_user = Users(username=test_user["username"], email=test_user["email"], password=hash_password,
                                confirmed=True, role="admin")
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
            print(err)
            await session.rollback()
        finally:
            await session.close()

    app.dependency_overrides[get_connection_db] = override_get_db

    yield TestClient(app)


@pytest_asyncio.fixture()
async def get_token():
    token = await service.jwt.create_access_token(data={"sub": test_user["email"]})
    return token