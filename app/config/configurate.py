from pydantic_settings import BaseSettings
from pydantic import EmailStr, ConfigDict
from fastapi import FastAPI
import redis.asyncio as redis
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter

class Settings(BaseSettings):
    PG_URL:str="postgresql+asyncpg://postgres:000000@localhost:5432/contacts"
    SECRET_KEY_JWT: str = "00000000000000000000000000000000"
    ALGORITHM: str = "HS256"
    MAIL_USERNAME:EmailStr = 'example@example.com'
    MAIL_PASSWORD: str|None = None
    MAIL_PORT: int = 587
    MAIL_SERVER: str = 'smtp.example.com'
    RABBITMQ_URL: str = 'http://localhost'
    REDIS_DOMAIN: str = 'http://localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str|None = None
    REDIS_URL: str = f'redis://{REDIS_DOMAIN}:{REDIS_PORT}'
    CLD_NAME: str = 'contacts_API'
    CLD_API_KEY: int = 125632
    CLD_API_SECRET: str = '<secret_key>'
    refresh_token:str = 'refresh_token'
    access_token:str = 'access_token'
    reset_password_token:str = 'reset_password_token'
    email_token:str = 'email_token'

    model_config = ConfigDict(extra='ignore',env_file=".env", env_file_encoding="utf-8")  # noqa

settings = Settings()

def configure_cors(app:FastAPI)->None:
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=['*']
    )

async def lifespan(app:FastAPI):
    redis_client = await redis.Redis (
        host=settings.REDIS_DOMAIN,
        port=settings.REDIS_PORT,
        db=0,
        password=settings.REDIS_PASSWORD,
    )
    await FastAPILimiter.init(redis_client)
    yield 