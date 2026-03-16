"""API маршруты для управления пользователями."""

from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLevel,
    UserStatus,
)
from app.services.user_service import UserService
from app.routers.auth import get_current_user
from app.models.user import User
from app.core.exceptions import PermissionError, ConflictError, NotFoundError

router = APIRouter()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Зависимость для получения UserService."""
    return UserService(db)


@router.get("", response_model=List[UserResponse])
def get_users(
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    search: Optional[str] = Query(None, description="Поиск по имени, фамилии, email"),
    level: Optional[UserLevel] = Query(None, description="Фильтр по уровню доступа"),
    status_filter: Optional[UserStatus] = Query(None, alias="status", description="Фильтр по статусу"),
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Получение списка пользователей.
    
    Доступно пользователям с уровнем MANAGER и выше.
    """
    # Проверка прав: только менеджер и выше
    allowed_levels = [UserLevel.MANAGER, UserLevel.ADMIN, UserLevel.DIRECTOR, UserLevel.SUPERUSER]
    if current_user.level not in allowed_levels:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра списка пользователей"
        )
    
    users = service.get_all(
        skip=skip,
        limit=limit,
        search=search,
        level=level,
        status=status_filter
    )
    return users


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Получение информации о текущем пользователе.
    """
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Получение пользователя по ID.
    """
    # Проверка прав: можно смотреть только пользователей с уровнем ниже своего
    try:
        target_user = service.get_by_id(user_id)
        
        # Проверка иерархии
        hierarchy = [
            UserLevel.GUEST, UserLevel.CLIENT, UserLevel.STAFF,
            UserLevel.MANAGER, UserLevel.ADMIN, UserLevel.DIRECTOR, UserLevel.SUPERUSER
        ]
        
        user_level_index = hierarchy.index(current_user.level)
        target_level_index = hierarchy.index(target_user.level)
        
        # Можно смотреть только пользователей с уровнем ниже своего
        # Исключение: суперпользователь видит всех
        if current_user.level != UserLevel.SUPERUSER and target_level_index >= user_level_index:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для просмотра этого пользователя"
            )
        
        return target_user
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Создание нового пользователя.
    
    Доступно пользователям с уровнем ADMIN и выше.
    """
    # Проверка прав: только администратор и выше
    allowed_levels = [UserLevel.ADMIN, UserLevel.DIRECTOR, UserLevel.SUPERUSER]
    if current_user.level not in allowed_levels:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для создания пользователей"
        )
    
    try:
        user = service.create(user_data, creator_level=current_user.level)
        return user
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Обновление данных пользователя.
    
    Доступно пользователям с уровнем ADMIN и выше для пользователей с уровнем ниже.
    """
    # Проверка прав: только администратор и выше
    allowed_levels = [UserLevel.ADMIN, UserLevel.DIRECTOR, UserLevel.SUPERUSER]
    if current_user.level not in allowed_levels:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для редактирования пользователей"
        )
    
    try:
        user = service.update(user_id, user_data, updater_level=current_user.level)
        return user
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Удаление пользователя.
    
    Доступно пользователям с уровнем ADMIN и выше для пользователей с уровнем ниже.
    """
    # Проверка прав: только администратор и выше
    allowed_levels = [UserLevel.ADMIN, UserLevel.DIRECTOR, UserLevel.SUPERUSER]
    if current_user.level not in allowed_levels:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления пользователей"
        )
    
    try:
        service.delete(user_id, deleter_level=current_user.level)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
