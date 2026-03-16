"""Модель элемента меню."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class MenuItem(Base):
    """
    Модель элемента меню в базе данных.

    Атрибуты:
        id: Уникальный идентификатор элемента меню.
        name: Название блюда/напитка.
        description: Описание блюда.
        price: Цена за единицу.
        category: Категория блюда (закуски, супы, горячее и т.д.).
        is_available: Доступен ли элемент для заказа.
        created_at: Дата и время создания.
        updated_at: Дата и время последнего обновления.
    """

    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    category = Column(String(100), nullable=True, index=True)
    is_available = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Связь с элементами заказа
    order_items = relationship("OrderItem", back_populates="menu_item")

    def __repr__(self) -> str:
        return f"<MenuItem(id={self.id}, name='{self.name}', price={self.price})>"
