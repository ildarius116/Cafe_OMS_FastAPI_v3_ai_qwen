"""Схемы Pydantic для пользователя."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, ConfigDict


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


class UserBase(BaseModel):
    """Базовая схема пользователя с общими полями."""
    
    nickname: str = Field(..., min_length=3, max_length=50, description="Никнейм пользователя")
    name: str = Field(..., min_length=1, max_length=100, description="Имя")
    surname: str = Field(..., min_length=1, max_length=100, description="Фамилия")
    email: str = Field(..., description="Электронная почта")
    level: UserLevel = Field(default=UserLevel.CLIENT, description="Уровень прав доступа")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="Статус аккаунта")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nickname": "john_doe",
                "name": "John",
                "surname": "Doe",
                "email": "john@example.com",
                "level": "client",
                "status": "active"
            }
        }
    )


class UserCreate(BaseModel):
    """Схема для создания нового пользователя (регистрация)."""
    
    nickname: str = Field(..., min_length=3, max_length=50, description="Никнейм пользователя")
    name: str = Field(..., min_length=1, max_length=100, description="Имя")
    surname: str = Field(..., min_length=1, max_length=100, description="Фамилия")
    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(..., min_length=6, max_length=128, description="Пароль")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nickname": "john_doe",
                "name": "John",
                "surname": "Doe",
                "email": "john@example.com",
                "password": "securepassword123"
            }
        }
    )


class UserUpdate(BaseModel):
    """Схема для обновления данных пользователя."""
    
    nickname: Optional[str] = Field(None, min_length=3, max_length=50, description="Никнейм пользователя")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Имя")
    surname: Optional[str] = Field(None, min_length=1, max_length=100, description="Фамилия")
    email: Optional[EmailStr] = Field(None, description="Электронная почта")
    level: Optional[UserLevel] = Field(None, description="Уровень прав доступа")
    status: Optional[UserStatus] = Field(None, description="Статус аккаунта")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Jane",
                "status": "active"
            }
        }
    )


class UserResponse(BaseModel):
    """Схема ответа с данными пользователя."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    nickname: str
    name: str
    surname: str
    email: str
    level: UserLevel
    status: UserStatus
    created_at: datetime
    updated_at: datetime


class UserInDB(UserResponse):
    """Схема пользователя в базе данных (с хэшем пароля)."""
    
    hashed_password: str


class UserLogin(BaseModel):
    """Схема для входа пользователя."""
    
    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(..., min_length=6, max_length=128, description="Пароль")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john@example.com",
                "password": "securepassword123"
            }
        }
    )


class Token(BaseModel):
    """Схема токена доступа."""
    
    access_token: str
    token_type: str = "bearer"
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )


class TokenData(BaseModel):
    """Схема данных токена."""
    
    user_id: Optional[int] = None
