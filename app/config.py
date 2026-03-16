from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""

    # Database
    database_url: str = "sqlite:///./cafe.db"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS - список разрешённых origin
    frontend_urls: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"

    class Config:
        env_file = ".env"


settings = Settings()
