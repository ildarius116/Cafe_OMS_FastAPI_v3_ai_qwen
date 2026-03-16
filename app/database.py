"""
Правильная работа с БД.

Для production используется SQLite с WAL режимом.
Для тестов используется БД в памяти (in-memory).
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Определяем тип БД
IS_SQLITE = settings.database_url.startswith("sqlite")
IS_MEMORY = ":memory:" in settings.database_url

# Создаем движок БД
if IS_SQLITE:
    engine = create_engine(
        settings.database_url,
        connect_args={
            "check_same_thread": False,
            "timeout": 60,
        },
        pool_pre_ping=True,
    )
    
    # Включаем WAL режим для SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=60000")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()
else:
    engine = create_engine(settings.database_url, pool_pre_ping=True)

# Сессия с правильной изоляцией
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    """
    Зависимость для получения сессии БД.
    
    Каждая запрос создаёт НОВУЮ сессию и закрывает её после использования.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Создаёт все таблицы в БД."""
    Base.metadata.create_all(bind=engine)


def reset_db():
    """Удаляет все таблицы (для тестов)."""
    Base.metadata.drop_all(bind=engine)


def get_session():
    """Получить сессию для скриптов (не для запросов API)."""
    return SessionLocal()
