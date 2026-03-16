"""Модель пользователя."""

from datetime import datetime
from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class UserLevel(str, Enum):
    """Уровни прав доступа пользователя."""
    GUEST = "guest"
    CLIENT = "client"
    STAFF = "staff"
    MANAGER = "manager"
    ADMIN = "admin"
    DIRECTOR = "director"
    SUPERUSER = "superuser"


class UserStatus(str, Enum):
    """Статус аккаунта пользователя."""
    ACTIVE = "active"
    INACTIVE = "inactive"


class User(Base):
    """
    Модель пользователя в базе данных.
    
    Атрибуты:
        id: Уникальный идентификатор.
        nickname: Никнейм пользователя (уникальный).
        name: Имя.
        surname: Фамилия.
        email: Электронная почта (уникальная).
        level: Уровень прав доступа.
        status: Статус аккаунта.
        hashed_password: Хэш пароля.
        created_at: Дата и время создания.
        updated_at: Дата и время последнего обновления.
    """
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    level = Column(
        SQLEnum(UserLevel),
        default=UserLevel.CLIENT,
        nullable=False
    )
    status = Column(
        SQLEnum(UserStatus),
        default=UserStatus.ACTIVE,
        nullable=False
    )
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Связи
    orders = relationship("Order", back_populates="user", lazy="select")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, nickname='{self.nickname}', email='{self.email}')>"
