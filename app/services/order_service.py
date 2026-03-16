"""Сервис для управления заказами."""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session, joinedload

from app.models.order import Order, OrderStatus, OrderItem
from app.models.menu_item import MenuItem
from app.schemas.order import OrderCreate, OrderUpdate, OrderStatusUpdate, OrderItemCreate
from app.core.exceptions import NotFoundError, ValidationError


class OrderService:
    """
    Сервис для операций с заказами.

    Инкапсулирует бизнес-логику и работу с базой данных.
    """

    def __init__(self, db: Session):
        """
        Инициализирует сервис.

        Args:
            db: Сессия базы данных.
        """
        self.db = db

    def get_by_id(self, order_id: int) -> Order:
        """
        Получает заказ по ID.

        Args:
            order_id: Уникальный идентификатор заказа.

        Returns:
            Объект заказа.

        Raises:
            NotFoundError: Если заказ не найден.
        """
        order = self.db.query(Order).options(
            joinedload(Order.order_items).joinedload(OrderItem.menu_item)
        ).filter(Order.id == order_id).first()
        if not order:
            raise NotFoundError(f"Заказ с ID {order_id} не найден")
        return order

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        table_number: Optional[int] = None,
        status: Optional[OrderStatus] = None,
        search: Optional[str] = None
    ) -> List[Order]:
        """
        Получает список заказов с фильтрацией и пагинацией.

        Args:
            skip: Количество пропускаемых записей.
            limit: Максимальное количество записей.
            table_number: Фильтр по номеру стола.
            status: Фильтр по статусу.
            search: Поисковый запрос (по номеру стола или статусу).

        Returns:
            Список заказов.
        """
        query = self.db.query(Order).options(
            joinedload(Order.order_items).joinedload(OrderItem.menu_item)
        )

        # Фильтр по номеру стола
        if table_number is not None:
            query = query.filter(Order.table_number == table_number)

        # Фильтр по статусу
        if status:
            query = query.filter(Order.status == status)

        # Поисковый фильтр
        if search:
            try:
                table_num = int(search)
                query = query.filter(
                    or_(
                        Order.table_number == table_num,
                        Order.status.ilike(f"%{search}%")
                    )
                )
            except ValueError:
                query = query.filter(Order.status.ilike(f"%{search}%"))

        return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

    def create(self, data: OrderCreate, user_id: Optional[int] = None) -> Order:
        """
        Создаёт новый заказ.

        Args:
            data: Данные для создания заказа.
            user_id: ID пользователя, создавшего заказ.

        Returns:
            Созданный объект заказа.

        Raises:
            NotFoundError: Если элемент меню не найден.
            ValidationError: Если данные некорректны.
        """
        # Проверяем что все menu_item_id существуют
        menu_item_ids = [item.menu_item_id for item in data.items]
        menu_items = self.db.query(MenuItem).filter(MenuItem.id.in_(menu_item_ids)).all()
        
        if len(menu_items) != len(menu_item_ids):
            found_ids = {mi.id for mi in menu_items}
            missing_ids = set(menu_item_ids) - found_ids
            raise NotFoundError(f"Элементы меню с ID {missing_ids} не найдены")
        
        # Проверяем что все элементы доступны
        for mi in menu_items:
            if not mi.is_available:
                raise ValidationError(f"Элемент меню '{mi.name}' недоступен для заказа")
        
        # Создаём заказ
        order = Order(
            table_number=data.table_number,
            user_id=user_id,
            status=OrderStatus.PENDING,
            total_price=0
        )
        
        self.db.add(order)
        self.db.flush()  # Получаем ID заказа
        
        # Создаём элементы заказа
        for item_data in data.items:
            menu_item = next(mi for mi in menu_items if mi.id == item_data.menu_item_id)
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item_data.menu_item_id,
                quantity=item_data.quantity,
                price=menu_item.price,  # Копируем цену на момент заказа
                note=item_data.note
            )
            self.db.add(order_item)
        
        # Вычисляем общую стоимость
        order.total_price = order.calculate_total()
        
        self.db.commit()
        self.db.refresh(order)
        return order

    def update(self, order_id: int, data: OrderUpdate) -> Order:
        """
        Обновляет заказ.

        Args:
            order_id: ID заказа для обновления.
            data: Новые данные.

        Returns:
            Обновлённый объект заказа.

        Raises:
            NotFoundError: Если заказ не найден.
        """
        order = self.get_by_id(order_id)

        # Обновление полей
        if data.table_number is not None:
            order.table_number = data.table_number
        
        if data.status is not None:
            order.status = data.status
        
        # Обновление элементов заказа
        if data.items is not None:
            # Удаляем старые элементы
            self.db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()
            
            # Проверяем что все menu_item_id существуют
            menu_item_ids = [item.menu_item_id for item in data.items]
            menu_items = self.db.query(MenuItem).filter(MenuItem.id.in_(menu_item_ids)).all()
            
            if len(menu_items) != len(menu_item_ids):
                found_ids = {mi.id for mi in menu_items}
                missing_ids = set(menu_item_ids) - found_ids
                raise NotFoundError(f"Элементы меню с ID {missing_ids} не найдены")
            
            # Создаём новые элементы
            for item_data in data.items:
                menu_item = next(mi for mi in menu_items if mi.id == item_data.menu_item_id)
                order_item = OrderItem(
                    order_id=order_id,
                    menu_item_id=item_data.menu_item_id,
                    quantity=item_data.quantity,
                    price=menu_item.price,
                    note=item_data.note
                )
                self.db.add(order_item)
            
            # Пересчитываем общую стоимость
            order.total_price = order.calculate_total()

        order.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(order)
        return order

    def update_status(self, order_id: int, status) -> Order:
        """
        Обновляет статус заказа.

        Args:
            order_id: ID заказа для обновления.
            status: Новый статус (OrderStatus enum или значение).

        Returns:
            Обновлённый объект заказа.

        Raises:
            NotFoundError: Если заказ не найден.
        """
        order = self.get_by_id(order_id)
        order.status = status
        order.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(order)
        return order

    def delete(self, order_id: int) -> None:
        """
        Удаляет заказ.

        Args:
            order_id: ID заказа для удаления.

        Raises:
            NotFoundError: Если заказ не найден.
        """
        order = self.get_by_id(order_id)
        self.db.delete(order)
        self.db.commit()

    def get_active(self) -> List[Order]:
        """
        Получает активные заказы (pending или ready).

        Returns:
            Список активных заказов.
        """
        return self.db.query(Order).options(
            joinedload(Order.order_items).joinedload(OrderItem.menu_item)
        ).filter(
            Order.status.in_([OrderStatus.PENDING, OrderStatus.READY])
        ).order_by(Order.created_at.desc()).all()

    def get_by_table(self, table_number: int) -> List[Order]:
        """
        Получает заказы по номеру стола.

        Args:
            table_number: Номер стола.

        Returns:
            Список заказов для указанного стола.
        """
        return self.db.query(Order).options(
            joinedload(Order.order_items).joinedload(OrderItem.menu_item)
        ).filter(
            Order.table_number == table_number
        ).order_by(Order.created_at.desc()).all()

    def get_revenue(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """
        Вычисляет выручку за период.

        Args:
            start_date: Начало периода.
            end_date: Конец периода.

        Returns:
            Словарь с общей выручкой и количеством заказов.
        """
        query = self.db.query(Order).filter(Order.status == OrderStatus.PAID)

        if start_date:
            query = query.filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)

        orders = query.all()
        total_revenue = sum(order.total_price for order in orders)

        return {
            "total_revenue": total_revenue,
            "orders_count": len(orders),
            "period_start": start_date,
            "period_end": end_date
        }
