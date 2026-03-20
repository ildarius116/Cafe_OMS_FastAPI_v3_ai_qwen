"""Модуль безопасности: хэширование паролей и JWT токены."""

from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from app.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие пароля хэшу.

    Args:
        plain_password: Пароль в открытом виде.
        hashed_password: Хэш пароля в БД.

    Returns:
        True если пароль верный, False иначе.
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """
    Хэширует пароль.

    Args:
        password: Пароль в открытом виде.

    Returns:
        Хэш пароля.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создаёт JWT токен доступа.

    Args:
        data: Данные для включения в токен (обычно {"sub": user_id}).
        expires_delta: Время действия токена. Если None, используется значение из настроек.

    Returns:
        JWT токен в виде строки.
    """
    to_encode = data.copy()

    # Преобразуем sub в строку (требование JWT)
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Декодирует JWT токен.
    
    Args:
        token: JWT токен.
    
    Returns:
        Данные токена или None если токен невалиден.
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None
