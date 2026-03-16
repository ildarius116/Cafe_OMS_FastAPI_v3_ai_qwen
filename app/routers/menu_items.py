"""API маршруты для управления элементами меню."""

from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.menu_item import MenuItemCreate, MenuItemUpdate, MenuItemResponse
from app.services.menu_item_service import MenuItemService
from app.models.user import User
from app.routers.auth import get_current_user
from app.core.exceptions import NotFoundError, ConflictError

router = APIRouter()


def get_menu_item_service(db: Session = Depends(get_db)) -> MenuItemService:
    """Зависимость для получения MenuItemService."""
    return MenuItemService(db)


@router.get("", response_model=List[MenuItemResponse])
def get_menu_items(
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    is_available: Optional[bool] = Query(None, description="Фильтр по доступности"),
    search: Optional[str] = Query(None, description="Поиск по названию или описанию"),
    service: MenuItemService = Depends(get_menu_item_service)
):
    """
    Получение списка элементов меню.

    Доступно всем авторизованным пользователям.
    """
    return service.get_all(
        skip=skip,
        limit=limit,
        category=category,
        is_available=is_available,
        search=search
    )


@router.get("/categories", response_model=List[str])
def get_categories(
    service: MenuItemService = Depends(get_menu_item_service)
):
    """
    Получение списка всех категорий.
    """
    return service.get_categories()


@router.get("/{item_id}", response_model=MenuItemResponse)
def get_menu_item(
    item_id: int,
    service: MenuItemService = Depends(get_menu_item_service)
):
    """
    Получение элемента меню по ID.
    """
    try:
        return service.get_by_id(item_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_menu_item(
    item_data: MenuItemCreate,
    current_user: User = Depends(get_current_user),
    service: MenuItemService = Depends(get_menu_item_service)
):
    """
    Создание нового элемента меню.

    Доступно пользователям с уровнем MANAGER и выше.
    """
    # Проверка прав
    allowed_levels = ["manager", "admin", "director", "superuser"]
    if current_user.level.value not in allowed_levels:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для создания элементов меню"
        )

    try:
        return service.create(item_data)
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.put("/{item_id}", response_model=MenuItemResponse)
def update_menu_item(
    item_id: int,
    item_data: MenuItemUpdate,
    current_user: User = Depends(get_current_user),
    service: MenuItemService = Depends(get_menu_item_service)
):
    """
    Обновление элемента меню.

    Доступно пользователям с уровнем MANAGER и выше.
    """
    # Проверка прав
    allowed_levels = ["manager", "admin", "director", "superuser"]
    if current_user.level.value not in allowed_levels:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для редактирования элементов меню"
        )

    try:
        return service.update(item_id, item_data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    service: MenuItemService = Depends(get_menu_item_service)
):
    """
    Удаление элемента меню.

    Доступно пользователям с уровнем ADMIN и выше.
    """
    # Проверка прав
    allowed_levels = ["admin", "director", "superuser"]
    if current_user.level.value not in allowed_levels:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления элементов меню"
        )

    try:
        service.delete(item_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
