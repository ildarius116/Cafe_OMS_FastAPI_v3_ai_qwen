"""Модели заказа и элементов заказа."""

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column, Integer, String, Float, DateTime,
    Enum as SQLEnum, ForeignKey, JSON, Boolean
)
from sqlalchemy.orm import relationship

from app.database import Base


class OrderStatus(str, Enum):
    """Статусы заказа."""
    PENDING = "pending"      # В ожидании
    READY = "ready"          # Готово
    PAID = "paid"            # Оплачено


class Order(Base):
    """
    Модель заказа в базе данных.

    Атрибуты:
        id: Уникальный идентификатор заказа.
        table_number: Номер стола.
        total_price: Общая стоимость заказа.
        status: Статус заказа.
        user_id: ID пользователя, создавшего заказ.
        created_at: Дата и время создания заказа.
        updated_at: Дата и время последнего обновления.
    """

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(Integer, nullable=False, index=True)
    total_price = Column(Float, default=0.0, nullable=False)
    status = Column(
        SQLEnum(OrderStatus),
        default=OrderStatus.PENDING,
        nullable=False,
        index=True
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Связи
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    # Алиас для совместимости с Pydantic схемами (items -> order_items)
    @property
    def items(self):
        """Возвращает элементы заказа (алиас на order_items)."""
        return self.order_items

    def calculate_total(self) -> float:
        """
        Вычисляет общую стоимость заказа.

        Returns:
            Общая стоимость всех элементов заказа.
        """
        return sum(item.quantity * item.price for item in self.order_items)

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, table={self.table_number}, status='{self.status}')>"


class OrderItem(Base):
    """
    Модель элемента заказа (связь many-to-many с MenuItem).

    Атрибуты:
        id: Уникальный идентификатор элемента.
        order_id: ID родительского заказа.
        menu_item_id: ID элемента меню.
        quantity: Количество.
        price: Цена на момент заказа (копируется из MenuItem).
        note: Примечание к заказу (опционально).
    """

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False, index=True)
    quantity = Column(Integer, default=1, nullable=False)
    price = Column(Float, nullable=False)  # Цена на момент заказа
    note = Column(String(255), nullable=True)

    # Связи
    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")

    def __repr__(self) -> str:
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, menu_item_id={self.menu_item_id}, quantity={self.quantity})>"
