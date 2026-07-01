from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:1111@localhost:5432/test_leads"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:19092"
    KAFKA_LEADS_TOPIC: str = "leads.events.v1"
    KAFKA_MODERATION_TOPIC: str = "lead_moderation.events.v1"
    OUTBOX_POLL_INTERVAL: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
