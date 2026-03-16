"""Сервис для управления элементами меню."""

from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.menu_item import MenuItem
from app.schemas.menu_item import MenuItemCreate, MenuItemUpdate
from app.core.exceptions import NotFoundError, ConflictError


class MenuItemService:
    """
    Сервис для операций с элементами меню.

    Инкапсулирует бизнес-логику и работу с базой данных.
    """

    def __init__(self, db: Session):
        """
        Инициализирует сервис.

        Args:
            db: Сессия базы данных.
        """
        self.db = db

    def get_by_id(self, item_id: int) -> MenuItem:
        """
        Получает элемент меню по ID.

        Args:
            item_id: Уникальный идентификатор элемента.

        Returns:
            Объект элемента меню.

        Raises:
            NotFoundError: Если элемент не найден.
        """
        item = self.db.query(MenuItem).filter(MenuItem.id == item_id).first()
        if not item:
            raise NotFoundError(f"Элемент меню с ID {item_id} не найден")
        return item

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        is_available: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[MenuItem]:
        """
        Получает список элементов меню с фильтрацией и пагинацией.

        Args:
            skip: Количество пропускаемых записей.
            limit: Максимальное количество записей.
            category: Фильтр по категории.
            is_available: Фильтр по доступности.
            search: Поисковый запрос (по названию или описанию).

        Returns:
            Список элементов меню.
        """
        query = self.db.query(MenuItem)

        # Фильтр по категории
        if category:
            query = query.filter(MenuItem.category == category)

        # Фильтр по доступности
        if is_available is not None:
            query = query.filter(MenuItem.is_available == is_available)

        # Поисковый фильтр
        if search:
            query = query.filter(
                MenuItem.name.ilike(f"%{search}%") | 
                MenuItem.description.ilike(f"%{search}%")
            )

        return query.order_by(MenuItem.name).offset(skip).limit(limit).all()

    def create(self, data: MenuItemCreate) -> MenuItem:
        """
        Создаёт новый элемент меню.

        Args:
            data: Данные для создания элемента.

        Returns:
            Созданный объект элемента меню.

        Raises:
            ConflictError: Если элемент с таким именем уже существует.
        """
        # Проверяем нет ли элемента с таким именем
        existing = self.db.query(MenuItem).filter(
            MenuItem.name == data.name
        ).first()
        if existing:
            raise ConflictError(f"Элемент меню с именем '{data.name}' уже существует")

        item = MenuItem(
            name=data.name,
            description=data.description,
            price=data.price,
            category=data.category,
            is_available=data.is_available
        )

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update(self, item_id: int, data: MenuItemUpdate) -> MenuItem:
        """
        Обновляет элемент меню.

        Args:
            item_id: ID элемента для обновления.
            data: Новые данные.

        Returns:
            Обновлённый объект элемента меню.

        Raises:
            NotFoundError: Если элемент не найден.
        """
        item = self.get_by_id(item_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)

        item.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item_id: int) -> None:
        """
        Удаляет элемент меню.

        Args:
            item_id: ID элемента для удаления.

        Raises:
            NotFoundError: Если элемент не найден.
        """
        item = self.get_by_id(item_id)
        self.db.delete(item)
        self.db.commit()

    def get_categories(self) -> List[str]:
        """
        Получает список всех категорий.

        Returns:
            Список уникальных категорий.
        """
        result = self.db.query(MenuItem.category).filter(
            MenuItem.category.isnot(None)
        ).distinct().all()
        return [row[0] for row in result if row[0]]
