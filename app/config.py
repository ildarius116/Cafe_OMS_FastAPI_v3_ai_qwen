from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/cafe_orders"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS - список разрешённых origin
    frontend_urls: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,http://localhost:8080,http://127.0.0.1:8080"

    model_config = ConfigDict(
        env_file=".env",
        extra='ignore'  # Игнорировать лишние поля из .env
    )


settings = Settings()
