from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", alias="API_HOST")
    API_PORT: int = Field(default=8000, alias="API_PORT")
    DEBUG: bool = Field(default=True, alias="API_DEBUG")
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000"], alias="API_CORS_ORIGINS")

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql+psycopg2://bugninja_user:bugninja_password@localhost:5432/bugninja",
        alias="DATABASE_URL",
    )

    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379", alias="REDIS_URL")

    # JWT Configuration
    JWT_SECRET_KEY: str = Field(
        default="your-super-secret-jwt-token-with-at-least-32-characters-long",
        alias="JWT_SECRET_KEY",
    )
    JWT_ALGORITHM: str = Field(default="HS256", alias="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    model_config = SettingsConfigDict(extra="allow", case_sensitive=True, env_file=".env")


settings = Settings()
