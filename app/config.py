from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:1111@localhost:5432/test_leads"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
