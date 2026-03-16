"""Cafe Orders API — система управления заказами в кафе."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, users, orders, menu_items
from app.core.exceptions import AppError
from app.database import Base, engine, init_db
from app.models.user import User  # noqa: F401
from app.models.order import Order, OrderItem  # noqa: F401
from app.models.menu_item import MenuItem  # noqa: F401


def create_app() -> FastAPI:
    """Создаёт и настраивает приложение FastAPI."""

    # Создаём таблицы в БД при старте
    init_db()

    app = FastAPI(
        title="Cafe Orders API",
        description="API для управления заказами и пользователями в кафе",
        version="1.0.0",
    )

    # CORS middleware - разрешаем несколько frontend URL
    allow_origins = [url.strip() for url in settings.frontend_urls.split(",")]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Регистрация роутеров
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(users.router, prefix="/api/users", tags=["users"])
    app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
    app.include_router(menu_items.router, prefix="/api/menu-items", tags=["menu-items"])

    # Health check endpoint
    @app.get("/health", tags=["health"])
    def health_check():
        """Проверка работоспособности API."""
        return {"status": "ok", "version": "1.0.0"}

    # Глобальный обработчик исключений
    @app.exception_handler(AppError)
    async def app_error_handler(request, exc: AppError):
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )

    return app


# Создаём экземпляр приложения
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
