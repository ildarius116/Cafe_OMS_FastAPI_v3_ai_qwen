"""Схемы Pydantic для заказа."""

from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.menu_item import OrderItemResponse, OrderItemCreate


class OrderStatus(str, Enum):
    """Статусы заказа."""
    PENDING = "pending"      # В ожидании
    READY = "ready"          # Готово
    PAID = "paid"            # Оплачено


class OrderBase(BaseModel):
    """Базовая схема заказа с общими полями."""

    table_number: int = Field(..., gt=0, description="Номер стола")
    items: List[OrderItemCreate] = Field(..., min_length=1, description="Список заказанных блюд")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "table_number": 5,
                "items": [
                    {"menu_item_id": 1, "quantity": 2},
                    {"menu_item_id": 5, "quantity": 1}
                ]
            }
        }
    )


class OrderCreate(OrderBase):
    """Схема для создания нового заказа."""
    pass


class OrderUpdate(BaseModel):
    """Схема для обновления заказа."""

    table_number: Optional[int] = Field(None, gt=0, description="Номер стола")
    items: Optional[List[OrderItemCreate]] = Field(None, min_length=1, description="Список заказанных блюд")
    status: Optional[OrderStatus] = Field(None, description="Статус заказа")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ready"
            }
        }
    )


class OrderStatusUpdate(BaseModel):
    """Схема для обновления только статуса заказа."""

    status: OrderStatus = Field(..., description="Новый статус заказа")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "paid"
            }
        }
    )


class OrderResponse(BaseModel):
    """Схема ответа с данными заказа."""

    id: int
    table_number: int
    items: List[OrderItemResponse]  # Связь с MenuItem
    total_price: float
    status: OrderStatus
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "table_number": 5,
                "items": [
                    {"id": 1, "menu_item_id": 1, "quantity": 2, "price": 350.0, "menu_item": {"id": 1, "name": "Бургер", "price": 350.0}},
                    {"id": 2, "menu_item_id": 5, "quantity": 1, "price": 150.0, "menu_item": {"id": 5, "name": "Картофель фри", "price": 150.0}}
                ],
                "total_price": 850.0,
                "status": "pending",
                "user_id": 1,
                "created_at": "2026-03-14T10:30:00",
                "updated_at": "2026-03-14T10:30:00"
            }
        }
    )


class OrderInDB(OrderResponse):
    """Схема заказа в базе данных."""
    pass


class OrderRevenue(BaseModel):
    """Схема для расчёта выручки."""

    total_revenue: float = Field(..., description="Общая выручка")
    orders_count: int = Field(..., description="Количество оплаченных заказов")
    period_start: Optional[datetime] = Field(None, description="Начало периода")
    period_end: Optional[datetime] = Field(None, description="Конец периода")
