"""Скрипт для заполнения БД тестовыми данными."""

from app.database import get_session
from app.models.user import User, UserLevel, UserStatus
from app.models.order import Order, OrderStatus, OrderItem
from app.models.menu_item import MenuItem
from app.core.security import get_password_hash


def seed_database():
    """Заполняет БД тестовыми данными."""
    db = get_session()

    try:
        # Проверяем есть ли данные
        if db.query(User).count() > 0:
            return {"status": "exists", "message": "База уже содержит данные"}

        # Создаём пользователей
        users = [
            User(nickname='admin', name='Александр', surname='Петров', email='admin@cafe.ru', level=UserLevel.ADMIN, status=UserStatus.ACTIVE, hashed_password=get_password_hash('admin123')),
            User(nickname='manager_anna', name='Анна', surname='Иванова', email='anna@cafe.ru', level=UserLevel.MANAGER, status=UserStatus.ACTIVE, hashed_password=get_password_hash('manager123')),
            User(nickname='waiter_igor', name='Игорь', surname='Сидоров', email='igor@cafe.ru', level=UserLevel.STAFF, status=UserStatus.ACTIVE, hashed_password=get_password_hash('staff123')),
            User(nickname='john_doe', name='John', surname='Doe', email='john@example.com', level=UserLevel.CLIENT, status=UserStatus.ACTIVE, hashed_password=get_password_hash('client123')),
            User(nickname='pit2', name='Петя2', surname='Васечкин', email='pit_v2@example.com', level=UserLevel.CLIENT, status=UserStatus.ACTIVE, hashed_password=get_password_hash('123456')),
        ]
        db.add_all(users)
        db.commit()

        # Сначала создаём элементы меню
        menu_items_data = [
            {"name": "Бургер", "description": "Сочный бургер с говядиной", "price": 350.0, "category": "Горячее"},
            {"name": "Картофель фри", "description": "Хрустящий картофель", "price": 150.0, "category": "Закуски"},
            {"name": "Пицца Маргарита", "description": "Классическая пицца", "price": 800.0, "category": "Горячее"},
            {"name": "Кола", "description": "Газированный напиток", "price": 200.0, "category": "Напитки"},
            {"name": "Стейк рибай", "description": "Стейк из мраморной говядины", "price": 1500.0, "category": "Горячее"},
            {"name": "Салат Цезарь", "description": "Классический салат", "price": 350.0, "category": "Салаты"},
            {"name": "Кофе американо", "description": "Чёрный кофе", "price": 150.0, "category": "Напитки"},
            {"name": "Чизкейк", "description": "Нежный чизкейк", "price": 220.0, "category": "Десерты"},
            {"name": "Паста Карбонара", "description": "Паста с беконом", "price": 450.0, "category": "Горячее"},
            {"name": "Борщ", "description": "Традиционный украинский борщ", "price": 300.0, "category": "Супы"},
            {"name": "Хлебцы", "description": "Хрустящие хлебцы к борщу", "price": 50.0, "category": "Закуски"},
        ]
        
        menu_items = []
        for mi_data in menu_items_data:
            menu_item = MenuItem(**mi_data)
            db.add(menu_item)
            menu_items.append(menu_item)
        db.commit()

        # Создаём заказы с элементами
        # Order 1: table 5, user 1, pending
        order1 = Order(table_number=5, status=OrderStatus.PENDING, user_id=1, total_price=0)
        db.add(order1)
        db.flush()
        db.add(OrderItem(order_id=order1.id, menu_item_id=menu_items[0].id, quantity=2, price=menu_items[0].price))  # Бургер
        db.add(OrderItem(order_id=order1.id, menu_item_id=menu_items[1].id, quantity=1, price=menu_items[1].price))  # Картофель фри
        db.flush()  # Важно: flush перед calculate_total чтобы order_items загрузились
        order1.total_price = sum(item.quantity * item.price for item in order1.order_items)

        # Order 2: table 3, user 2, ready
        order2 = Order(table_number=3, status=OrderStatus.READY, user_id=2, total_price=0)
        db.add(order2)
        db.flush()
        db.add(OrderItem(order_id=order2.id, menu_item_id=menu_items[2].id, quantity=1, price=menu_items[2].price))  # Пицца Маргарита
        db.add(OrderItem(order_id=order2.id, menu_item_id=menu_items[3].id, quantity=2, price=menu_items[3].price))  # Кола
        db.flush()
        order2.total_price = sum(item.quantity * item.price for item in order2.order_items)

        # Order 3: table 7, user 1, paid
        order3 = Order(table_number=7, status=OrderStatus.PAID, user_id=1, total_price=0)
        db.add(order3)
        db.flush()
        db.add(OrderItem(order_id=order3.id, menu_item_id=menu_items[4].id, quantity=1, price=menu_items[4].price))  # Стейк рибай
        db.add(OrderItem(order_id=order3.id, menu_item_id=menu_items[5].id, quantity=1, price=menu_items[5].price))  # Салат Цезарь
        db.flush()
        order3.total_price = sum(item.quantity * item.price for item in order3.order_items)

        # Order 4: table 2, user 4, pending
        order4 = Order(table_number=2, status=OrderStatus.PENDING, user_id=4, total_price=0)
        db.add(order4)
        db.flush()
        db.add(OrderItem(order_id=order4.id, menu_item_id=menu_items[6].id, quantity=3, price=menu_items[6].price))  # Кофе американо
        db.add(OrderItem(order_id=order4.id, menu_item_id=menu_items[7].id, quantity=2, price=menu_items[7].price))  # Чизкейк
        db.flush()
        order4.total_price = sum(item.quantity * item.price for item in order4.order_items)

        # Order 5: table 10, user 3, ready
        order5 = Order(table_number=10, status=OrderStatus.READY, user_id=3, total_price=0)
        db.add(order5)
        db.flush()
        db.add(OrderItem(order_id=order5.id, menu_item_id=menu_items[8].id, quantity=2, price=menu_items[8].price))  # Паста Карбонара
        db.flush()
        order5.total_price = sum(item.quantity * item.price for item in order5.order_items)

        # Order 6: table 1, user 2, paid
        order6 = Order(table_number=1, status=OrderStatus.PAID, user_id=2, total_price=0)
        db.add(order6)
        db.flush()
        db.add(OrderItem(order_id=order6.id, menu_item_id=menu_items[9].id, quantity=2, price=menu_items[9].price))  # Борщ
        db.add(OrderItem(order_id=order6.id, menu_item_id=menu_items[10].id, quantity=1, price=menu_items[10].price))  # Хлебцы
        db.flush()
        order6.total_price = sum(item.quantity * item.price for item in order6.order_items)

        db.commit()

        return {
            "status": "created",
            "users": len(users),
            "menu_items": len(menu_items),
            "orders": 6,
            "message": "Тестовые данные созданы"
        }

    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


if __name__ == "__main__":
    result = seed_database()
    print(result)
