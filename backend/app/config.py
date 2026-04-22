from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    secret_key: str = Field(..., env="SECRET_KEY")
    database_url: str = Field(default="sqlite+aiosqlite:///./babyvision.db", env="DATABASE_URL")
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24
    cors_origins: list[str] = ["*"]
    enable_auth: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    inactivity_alert_minutes: int = 20

    class Config:
        env_file = ".env"

settings = Settings()
