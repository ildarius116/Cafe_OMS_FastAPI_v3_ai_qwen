"""API маршруты для управления заказами."""

from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.database import get_db
from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderStatus,
    OrderStatusUpdate,
    OrderRevenue,
    OrderItemCreate,
)
from app.services.order_service import OrderService
from app.routers.auth import get_current_user
from app.models.user import User, UserLevel
from app.models.order import Order, OrderItem
from app.models.menu_item import MenuItem
from app.core.exceptions import NotFoundError

router = APIRouter()


def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    """Зависимость для получения OrderService."""
    return OrderService(db)


@router.get("", response_model=List[OrderResponse])
def get_orders(
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    table_number: Optional[int] = Query(None, gt=0, description="Фильтр по номеру стола"),
    status_filter: Optional[OrderStatus] = Query(None, alias="status", description="Фильтр по статусу"),
    search: Optional[str] = Query(None, description="Поиск по номеру стола или статусу"),
    service: OrderService = Depends(get_order_service)
):
    """
    Получение списка всех заказов.
    
    Поддерживает фильтрацию по номеру стола, статусу и поиск.
    """
    orders = service.get_all(
        skip=skip,
        limit=limit,
        table_number=table_number,
        status=status_filter,
        search=search
    )
    return orders


@router.get("/active", response_model=List[OrderResponse])
def get_active_orders(
    service: OrderService = Depends(get_order_service)
):
    """
    Получение активных заказов (не оплаченных).
    """
    orders = service.get_active()
    return orders


@router.get("/revenue", response_model=OrderRevenue)
def get_revenue(
    start_date: Optional[datetime] = Query(None, description="Начало периода"),
    end_date: Optional[datetime] = Query(None, description="Конец периода"),
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    """
    Расчёт выручки за период.
    
    Доступно пользователям с уровнем MANAGER и выше.
    """
    # Проверка прав
    allowed_levels = [UserLevel.MANAGER, UserLevel.ADMIN, UserLevel.DIRECTOR, UserLevel.SUPERUSER]
    if current_user.level not in allowed_levels:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра финансовой информации"
        )
    
    revenue_data = service.get_revenue(start_date=start_date, end_date=end_date)
    return revenue_data


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    service: OrderService = Depends(get_order_service)
):
    """
    Получение заказа по ID.
    """
    try:
        order = service.get_by_id(order_id)
        return order
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    """
    Создание нового заказа.
    
    Номер стола и список блюд указываются в запросе.
    Общая стоимость вычисляется автоматически.
    """
    order = service.create(order_data, user_id=current_user.id)
    return order


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order_data: OrderUpdate,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    """
    Обновление заказа.
    
    Можно изменить номер стола, список блюд и статус.
    """
    try:
        order = service.update(order_id, order_data)
        return order
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    """
    Изменение статуса заказа.
    
    Доступные статусы: pending, ready, paid.
    """
    try:
        order = service.update_status(order_id, status_data.status)
        return order
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    """
    Удаление заказа.
    
    Доступно пользователям с уровнем MANAGER и выше.
    """
    # Проверка прав
    allowed_levels = [UserLevel.MANAGER, UserLevel.ADMIN, UserLevel.DIRECTOR, UserLevel.SUPERUSER]
    if current_user.level not in allowed_levels:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления заказов"
        )
    
    try:
        service.delete(order_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/table/{table_number}", response_model=List[OrderResponse])
def get_orders_by_table(
    table_number: int,
    service: OrderService = Depends(get_order_service)
):
    """
    Получение заказов по номеру стола.
    """
    orders = service.get_by_table(table_number)
    return orders
