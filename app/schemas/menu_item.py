"""Схемы валидации для элементов меню."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class MenuItemBase(BaseModel):
    """Базовая схема элемента меню."""
    name: str = Field(..., min_length=1, max_length=255, description="Название блюда")
    description: Optional[str] = Field(None, max_length=1000, description="Описание блюда")
    price: float = Field(..., gt=0, description="Цена за единицу")
    category: Optional[str] = Field(None, max_length=100, description="Категория блюда")
    is_available: bool = Field(True, description="Доступен ли элемент для заказа")


class MenuItemCreate(MenuItemBase):
    """Схема для создания элемента меню."""
    pass


class MenuItemUpdate(BaseModel):
    """Схема для обновления элемента меню."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=100)
    is_available: Optional[bool] = None


class MenuItemResponse(MenuItemBase):
    """Схема ответа с элементом меню."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderItemBase(BaseModel):
    """Базовая схема элемента заказа."""
    menu_item_id: int = Field(..., description="ID элемента меню")
    quantity: int = Field(..., ge=1, description="Количество")
    note: Optional[str] = Field(None, max_length=255, description="Примечание")


class OrderItemCreate(OrderItemBase):
    """Схема для создания элемента заказа."""
    pass


class OrderItemResponse(BaseModel):
    """Схема ответа с элементом заказа."""
    id: int
    menu_item_id: int
    quantity: int
    price: float  # Цена на момент заказа
    note: Optional[str] = None
    menu_item: Optional[MenuItemResponse] = None

    model_config = ConfigDict(from_attributes=True)
