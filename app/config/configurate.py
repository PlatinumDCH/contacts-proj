from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PG_URL:str="postgresql+asyncpg://postgres:000000@localhost:5432/contacts"
   
    class Config:
        """без этой штуки бд не конектится"""
        extra = 'ignore'
        env_file = '.env'
        env_file_encoding='utf-8'

settings = Settings()
