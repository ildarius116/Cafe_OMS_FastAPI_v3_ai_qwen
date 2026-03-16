"""Скрипт для создания тестовых данных.

Запускается ПРИ ОСТАНОВЛЕННОМ uvicorn для добавления данных в БД.
Таблицы создаются автоматически при старте uvicorn.
"""

import sys
from app.database import SessionLocal
from app.models.user import User, UserLevel, UserStatus
from app.models.order import Order, OrderStatus, OrderItem
from app.models.menu_item import MenuItem
from app.core.security import get_password_hash


def create_test_data(recreate: bool = False):
    """Создаёт тестовые данные в БД.

    Args:
        recreate: Если True, удаляет существующие данные перед созданием.
    """

    db = SessionLocal()

    try:
        # Проверяем есть ли уже элементы меню
        if db.query(MenuItem).count() > 0:
            if not recreate:
                print("⚠️ База уже содержит данные!")
                print("\nПользователи:")
                for u in db.query(User).all()[:5]:
                    print(f"  - {u.email} / {u.level.value}")
                print("  ...")
                print("\nЗапустите с --recreate для пересоздания данных")
                return
            else:
                print("🗑️ Удаляем существующие данные...")
                # Удаляем в правильном порядке (из-за foreign keys)
                db.query(OrderItem).delete()
                db.query(Order).delete()
                db.query(User).delete()
                db.query(MenuItem).delete()
                db.commit()
                print("✅ Данные удалены")

        # Создание элементов меню
        menu_items = [
            MenuItem(name="Бургер", description="Сочный бургер с говядиной", price=350.0, category="Горячее", is_available=True),
            MenuItem(name="Картофель фри", description="Хрустящий картофель во фритюре", price=150.0, category="Закуски", is_available=True),
            MenuItem(name="Пицца Маргарита", description="Классическая пицца с томатами и моцареллой", price=800.0, category="Горячее", is_available=True),
            MenuItem(name="Кола", description="Газированный напиток", price=200.0, category="Напитки", is_available=True),
            MenuItem(name="Стейк рибай", description="Стейк из мраморной говядины", price=1500.0, category="Горячее", is_available=True),
            MenuItem(name="Салат Цезарь", description="Классический салат с курицей", price=350.0, category="Салаты", is_available=True),
            MenuItem(name="Кофе американо", description="Чёрный кофе", price=150.0, category="Напитки", is_available=True),
            MenuItem(name="Чизкейк", description="Нежный творожный десерт", price=220.0, category="Десерты", is_available=True),
            MenuItem(name="Борщ", description="Традиционный украинский суп", price=300.0, category="Супы", is_available=True),
            MenuItem(name="Хлебцы", description="Хрустящие хлебцы к борщу", price=50.0, category="Закуски", is_available=True),
            MenuItem(name="Паста Карбонара", description="Итальянская паста с беконом", price=450.0, category="Горячее", is_available=True),
            MenuItem(name="Чай зелёный", description="Ароматный зелёный чай", price=100.0, category="Напитки", is_available=True),
            MenuItem(name="Суп харчо", description="Острый грузинский суп", price=320.0, category="Супы", is_available=True),
            MenuItem(name="Оливье", description="Новогодний салат", price=280.0, category="Салаты", is_available=True),
            MenuItem(name="Тирамису", description="Итальянский десерт", price=250.0, category="Десерты", is_available=True),
        ]

        db.add_all(menu_items)
        db.commit()

        # Получаем ID элементов меню из БД (после commit ID обновляются)
        menu_dict = {mi.name: mi for mi in db.query(MenuItem).all()}

        # Создание пользователей
        users = [
            User(
                nickname='admin',
                name='Александр',
                surname='Петров',
                email='admin@cafe.ru',
                level=UserLevel.ADMIN,
                status=UserStatus.ACTIVE,
                hashed_password=get_password_hash('admin123')
            ),
            User(
                nickname='manager_anna',
                name='Анна',
                surname='Иванова',
                email='anna@cafe.ru',
                level=UserLevel.MANAGER,
                status=UserStatus.ACTIVE,
                hashed_password=get_password_hash('manager123')
            ),
            User(
                nickname='waiter_igor',
                name='Игорь',
                surname='Сидоров',
                email='igor@cafe.ru',
                level=UserLevel.STAFF,
                status=UserStatus.ACTIVE,
                hashed_password=get_password_hash('staff123')
            ),
            User(
                nickname='john_doe',
                name='John',
                surname='Doe',
                email='john@example.com',
                level=UserLevel.CLIENT,
                status=UserStatus.ACTIVE,
                hashed_password=get_password_hash('client123')
            ),
            User(
                nickname='pit2',
                name='Петя2',
                surname='Васечкин',
                email='pit_v2@example.com',
                level=UserLevel.CLIENT,
                status=UserStatus.ACTIVE,
                hashed_password=get_password_hash('123456')
            ),
        ]

        db.add_all(users)
        db.commit()

        # Получаем пользователей из БД (после commit ID обновляются)
        user_dict = {u.nickname: u for u in db.query(User).all()}

        # Создание заказов с элементами меню
        orders_data = [
            {
                "table_number": 5,
                "user_nickname": "admin",
                "status": OrderStatus.PENDING,
                "items": [
                    {"menu_item_name": "Бургер", "quantity": 2},
                    {"menu_item_name": "Картофель фри", "quantity": 1}
                ]
            },
            {
                "table_number": 3,
                "user_nickname": "manager_anna",
                "status": OrderStatus.READY,
                "items": [
                    {"menu_item_name": "Пицца Маргарита", "quantity": 1},
                    {"menu_item_name": "Кола", "quantity": 2}
                ]
            },
            {
                "table_number": 7,
                "user_nickname": "admin",
                "status": OrderStatus.PAID,
                "items": [
                    {"menu_item_name": "Стейк рибай", "quantity": 1},
                    {"menu_item_name": "Салат Цезарь", "quantity": 1}
                ]
            },
            {
                "table_number": 2,
                "user_nickname": "john_doe",
                "status": OrderStatus.PENDING,
                "items": [
                    {"menu_item_name": "Кофе американо", "quantity": 3},
                    {"menu_item_name": "Чизкейк", "quantity": 2}
                ]
            },
            {
                "table_number": 10,
                "user_nickname": "waiter_igor",
                "status": OrderStatus.READY,
                "items": [
                    {"menu_item_name": "Паста Карбонара", "quantity": 2}
                ]
            },
            {
                "table_number": 1,
                "user_nickname": "manager_anna",
                "status": OrderStatus.PAID,
                "items": [
                    {"menu_item_name": "Борщ", "quantity": 2},
                    {"menu_item_name": "Хлебцы", "quantity": 1}
                ]
            },
        ]

        # Создаём заказы и элементы заказа
        for order_data in orders_data:
            order = Order(
                table_number=order_data["table_number"],
                user_id=user_dict[order_data["user_nickname"]].id,
                status=order_data["status"],
                total_price=0
            )
            db.add(order)
            db.flush()  # Получаем ID заказа

            # Добавляем элементы заказа и считаем сумму
            total = 0.0
            for item_data in order_data["items"]:
                menu_item = menu_dict[item_data["menu_item_name"]]
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=menu_item.id,
                    quantity=item_data["quantity"],
                    price=menu_item.price
                )
                db.add(order_item)
                total += item_data["quantity"] * menu_item.price

            # Устанавливаем общую стоимость
            order.total_price = total

        db.commit()

        print("\n✅ Тестовые данные успешно созданы!")
        print(f"\nЭлементы меню ({len(menu_items)}):")
        for mi in menu_items:
            print(f"  - {mi.name}: {mi.price}₽ ({mi.category})")
        
        print(f"\nПользователи ({len(users)}):")
        for user in users:
            print(f"  - {user.email} / {user.level.value} (пароль: ***123)")
        
        print(f"\nЗаказы ({len(orders_data)}):")
        for order in db.query(Order).all():
            items_str = ", ".join([f"{oi.quantity}x {oi.menu_item.name}" for oi in order.order_items])
            print(f"  - Стол {order.table_number}: {items_str} = {order.total_price}₽ ({order.status.value})")

    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Создание тестовых данных для кафе")
    parser.add_argument("--recreate", action="store_true", help="Удалить существующие данные и создать заново")
    args = parser.parse_args()

    create_test_data(recreate=args.recreate)
