"""API маршруты для аутентификации."""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.user_service import UserService
from app.core.security import create_access_token, verify_password
from app.core.exceptions import ConflictError, AuthenticationError
from app.config import settings
from app.models.user import UserLevel

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя.

    Новый пользователь автоматически получает уровень "client".
    """
    service = UserService(db)
    try:
        user = service.create(user_data, creator_level=UserLevel.CLIENT)
        return user
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Аутентификация пользователя.

    Возвращает JWT токен доступа.
    username может быть email или nickname.
    """
    service = UserService(db)

    # Поиск пользователя по username (email или nickname)

    # Сначала пробуем найти по email
    user = service.get_by_email(form_data.username)
    
    # Если не найдено, пробуем по nickname
    if not user:
        user = service.get_by_nickname(form_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учётные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Проверка пароля
    if not service.verify_password(user, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учётные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Проверка статуса аккаунта
    if user.status.value == "inactive":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт деактивирован"
        )

    # Создание токена
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id, "level": user.level.value},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/init-db")
def init_database():
    """
    Инициализирует БД тестовыми данными.
    
    Только для разработки! Удаляет старые данные и создаёт новые.
    """
    from app.seed import seed_database
    from app.database import get_session
    from app.models.user import User
    from app.models.order import Order, OrderItem
    
    db = get_session()
    try:
        # Очищаем старые данные
        db.query(OrderItem).delete()
        db.query(Order).delete()
        db.query(User).delete()
        db.commit()
        
        # Создаём новые
        return seed_database()
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Зависимость для получения текущего пользователя из токена.

    Используется в защищённых endpoints.
    """
    from jose import JWTError, jwt
    from app.core.exceptions import AuthenticationError, NotFoundError
    import logging

    logger = logging.getLogger(__name__)

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id: int = int(payload.get("sub"))  # Преобразуем из строки в int

        if user_id is None:
            logger.warning("No user_id in token")
            raise AuthenticationError()

    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise AuthenticationError()

    service = UserService(db)
    try:
        user = service.get_by_id(user_id)
    except NotFoundError as e:
        logger.warning(f"User {user_id} not found in database: {e}")
        raise AuthenticationError(f"Пользователь {user_id} не найден")

    if user.status.value == "inactive":
        logger.warning(f"User {user_id} is inactive")
        raise AuthenticationError("Аккаунт деактивирован")

    return user
