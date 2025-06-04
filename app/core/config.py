import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    SYNC_DATABASE_URL: str = "postgresql+psycopg2://postgres:password@localhost:5432/imdb_db"
    ASYNC_DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/imdb_db"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Model
    MODEL_PATH: str = "./distilbert-imdb"

    # App
    APP_NAME: str = "IMDB Review Service"
    APP_VERSION: str = "1.0.0"

settings = Settings()