import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # general
    PROJECT_NAME: str = "MediFlow"
    ENV: str = os.getenv("ENV", "production")

    # database
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # redis / cache
    REDIS_URL: str = os.getenv("REDIS_URL")

    # jwt
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # stripe
    STRIPE_API_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

settings = Settings()