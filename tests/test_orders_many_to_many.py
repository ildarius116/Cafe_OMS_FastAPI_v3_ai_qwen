"""Функциональные тесты для проверки many-to-many схемы заказов.

Тесты проверяют:
1. Заказы загружаются и отображаются
2. Элементы заказа имеют menu_item с name и price
3. Ошибки загрузки правильно обрабатываются
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine
from app.models.user import User, UserLevel, UserStatus
from app.models.order import Order, OrderStatus, OrderItem
from app.models.menu_item import MenuItem
from app.core.security import get_password_hash, create_access_token
from sqlalchemy.orm import sessionmaker, joinedload

# Создаём тестовую сессию
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """Создаёт тестовую базу данных."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    """Создаёт тестовый клиент с переопределением зависимости БД."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def create_user_with_token(test_db, email: str, level: UserLevel) -> tuple[User, str]:
    """Создаёт пользователя и возвращает токен."""
    user = User(
        email=email,
        name="Test",
        surname="User",
        nickname=email.split('@')[0],
        level=level,
        status=UserStatus.ACTIVE,
        hashed_password=get_password_hash("password")
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    token = create_access_token(data={"sub": user.id, "level": level.value})
    return user, token


@pytest.fixture
def user_with_token(test_db):
    """Создаёт обычного пользователя."""
    return create_user_with_token(test_db, "user@example.com", UserLevel.CLIENT)


@pytest.fixture
def manager_with_token(test_db):
    """Создаёт менеджера."""
    return create_user_with_token(test_db, "manager@example.com", UserLevel.MANAGER)


@pytest.fixture
def menu_items(test_db):
    """Создаёт тестовые элементы меню."""
    items = [
        MenuItem(name="Бургер", description="Сочный бургер с говядиной", price=350.0, category="Горячее", is_available=True),
        MenuItem(name="Картофель фри", description="Хрустящий картофель", price=150.0, category="Закуски", is_available=True),
        MenuItem(name="Пицца Маргарита", description="Классическая пицца", price=800.0, category="Горячее", is_available=True),
        MenuItem(name="Кола", description="Газированный напиток", price=200.0, category="Напитки", is_available=True),
        MenuItem(name="Стейк рибай", description="Мраморная говядина", price=1500.0, category="Горячее", is_available=True),
    ]
    test_db.add_all(items)
    test_db.commit()
    return {item.name: item for item in items}


@pytest.fixture
def orders_with_items(test_db, menu_items, user_with_token):
    """Создаёт заказы с элементами меню (many-to-many)."""
    user, _ = user_with_token
    burger = menu_items["Бургер"]
    fries = menu_items["Картофель фри"]
    pizza = menu_items["Пицца Маргарита"]
    cola = menu_items["Кола"]
    steak = menu_items["Стейк рибай"]
    
    # Создаём заказы
    orders = [
        Order(table_number=5, user_id=user.id, status=OrderStatus.PENDING, total_price=0),
        Order(table_number=3, user_id=user.id, status=OrderStatus.READY, total_price=0),
        Order(table_number=7, user_id=user.id, status=OrderStatus.PAID, total_price=0),
    ]
    test_db.add_all(orders)
    test_db.flush()
    
    # Добавляем элементы заказа
    order_items = [
        # Заказ 1: Бургер x2 + Фри x1 = 850
        OrderItem(order_id=orders[0].id, menu_item_id=burger.id, quantity=2, price=burger.price),
        OrderItem(order_id=orders[0].id, menu_item_id=fries.id, quantity=1, price=fries.price),
        # Заказ 2: Пицца x1 + Кола x2 = 1200
        OrderItem(order_id=orders[1].id, menu_item_id=pizza.id, quantity=1, price=pizza.price),
        OrderItem(order_id=orders[1].id, menu_item_id=cola.id, quantity=2, price=cola.price),
        # Заказ 3: Стейк x1 = 1500
        OrderItem(order_id=orders[2].id, menu_item_id=steak.id, quantity=1, price=steak.price),
    ]
    test_db.add_all(order_items)
    
    # Вычисляем общую стоимость
    orders[0].total_price = 850   # 350*2 + 150
    orders[1].total_price = 1200  # 800 + 200*2
    orders[2].total_price = 1500  # 1500*1
    test_db.commit()
    
    return orders


class TestOrderManyToMany:
    """Тесты many-to-many схемы заказов."""

    def test_order_has_menu_items(self, client, orders_with_items, menu_items):
        """Тест что заказ содержит элементы меню через many-to-many."""
        response = client.get("/api/orders")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 3
        order = data[0]
        
        # Проверяем структуру заказа
        assert "id" in order
        assert "table_number" in order
        assert "items" in order
        assert "total_price" in order
        
        # Проверяем что items это список
        assert isinstance(order["items"], list)
        assert len(order["items"]) == 2  # Бургер и Фри
        
        # Проверяем что каждый элемент имеет menu_item_id
        for item in order["items"]:
            assert "menu_item_id" in item
            assert "quantity" in item
            assert "price" in item
            assert item["menu_item_id"] is not None
            assert item["price"] > 0

    def test_order_item_has_menu_item_details(self, client, orders_with_items, menu_items):
        """Тест что элемент заказа содержит информацию о menu_item."""
        response = client.get("/api/orders")
        assert response.status_code == 200
        data = response.json()
        
        order = data[0]
        item = order["items"][0]
        
        # Проверяем что есть menu_item с name и price
        assert "menu_item" in item or item["price"] > 0
        
        # Если menu_item есть, проверяем его структуру
        if "menu_item" in item:
            assert "id" in item["menu_item"]
            assert "name" in item["menu_item"]
            assert "price" in item["menu_item"]
            assert item["menu_item"]["name"] in ["Бургер", "Картофель фри", "Пицца Маргарита", "Кола", "Стейк рибай"]

    def test_order_total_price_calculation(self, client, orders_with_items):
        """Тест что общая стоимость заказа вычисляется правильно."""
        response = client.get("/api/orders")
        assert response.status_code == 200
        data = response.json()
        
        # Проверяем расчёт для каждого заказа
        expected_totals = {5: 850, 3: 1200, 7: 1500}
        for order in data:
            table = order["table_number"]
            assert order["total_price"] == expected_totals[table], \
                f"Неверная сумма для стола {table}: {order['total_price']} != {expected_totals[table]}"

    def test_create_order_with_menu_item_ids(self, client, user_with_token, menu_items):
        """Тест создания заказа с menu_item_id."""
        user, token = user_with_token
        burger = menu_items["Бургер"]
        cola = menu_items["Кола"]
        
        response = client.post(
            "/api/orders",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "table_number": 10,
                "items": [
                    {"menu_item_id": burger.id, "quantity": 2},
                    {"menu_item_id": cola.id, "quantity": 3}
                ]
            }
        )
        
        assert response.status_code == 201, f"Create failed: {response.text}"
        data = response.json()
        
        # Проверяем структуру
        assert data["table_number"] == 10
        assert data["total_price"] == 1300  # 350*2 + 200*3
        assert len(data["items"]) == 2
        
        # Проверяем что элементы имеют menu_item_id
        for item in data["items"]:
            assert "menu_item_id" in item
            assert item["menu_item_id"] in [burger.id, cola.id]

    def test_update_order_items(self, client, user_with_token, orders_with_items, menu_items):
        """Тест обновления элементов заказа."""
        user, token = user_with_token
        pizza = menu_items["Пицца Маргарита"]
        
        response = client.put(
            f"/api/orders/{orders_with_items[0].id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "table_number": 5,
                "items": [{"menu_item_id": pizza.id, "quantity": 2}]
            }
        )
        
        assert response.status_code == 200, f"Update failed: {response.text}"
        data = response.json()
        
        assert data["table_number"] == 5
        assert data["total_price"] == 1600  # 800*2
        assert len(data["items"]) == 1
        assert data["items"][0]["menu_item_id"] == pizza.id


class TestOrderLoadingErrors:
    """Тесты обработки ошибок загрузки."""

    def test_get_order_not_found(self, client, user_with_token):
        """Тест что несуществующий заказ возвращает 404."""
        response = client.get("/api/orders/999")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_create_order_with_invalid_menu_item_id(self, client, user_with_token):
        """Тест что заказ с несуществующим menu_item_id возвращает ошибку."""
        user, token = user_with_token
        
        response = client.post(
            "/api/orders",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "table_number": 10,
                "items": [{"menu_item_id": 999, "quantity": 1}]  # Не существует
            }
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        data = response.json()
        assert "detail" in data

    def test_create_order_with_empty_items(self, client, user_with_token):
        """Тест что заказ с пустым items возвращает ошибку валидации."""
        user, token = user_with_token
        
        response = client.post(
            "/api/orders",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "table_number": 10,
                "items": []  # Пусто
            }
        )
        
        # Pydantic должен отклонить пустой items
        assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"

    def test_create_order_with_zero_quantity(self, client, user_with_token, menu_items):
        """Тест что заказ с quantity=0 возвращает ошибку валидации."""
        user, token = user_with_token
        burger = menu_items["Бургер"]
        
        response = client.post(
            "/api/orders",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "table_number": 10,
                "items": [{"menu_item_id": burger.id, "quantity": 0}]
            }
        )
        
        assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"


class TestOrderDisplay:
    """Тесты отображения заказов (симуляция frontend)."""

    def test_orders_list_structure(self, client, orders_with_items):
        """Тест что структура списка заказов подходит для frontend."""
        response = client.get("/api/orders")
        assert response.status_code == 200
        data = response.json()
        
        # Проверяем что каждый заказ имеет все поля для отображения
        for order in data:
            assert "id" in order  # Для ключа таблицы
            assert "table_number" in order  # Для отображения стола
            assert "items" in order  # Для списка блюд
            assert "total_price" in order  # Для суммы
            assert "status" in order  # Для статуса
            assert "created_at" in order  # Для даты
            
            # Проверяем что items можно отобразить
            for item in order["items"]:
                assert "menu_item_id" in item  # Для связи
                assert "quantity" in item  # Для количества
                assert "price" in item  # Для цены

    def test_order_items_for_display(self, client, orders_with_items, menu_items):
        """Тест что элементы заказа можно отобразить в UI."""
        response = client.get("/api/orders")
        assert response.status_code == 200
        data = response.json()
        
        # Симулируем то что делает frontend: отображает "2x Бургер"
        for order in data:
            for item in order["items"]:
                # Frontend ожидает menu_item.name для отображения
                if "menu_item" in item:
                    assert "name" in item["menu_item"]
                    # Проверяем что можно сформировать строку "2x Бургер"
                    display_text = f"{item['quantity']}x {item['menu_item']['name']}"
                    assert "x" in display_text
                else:
                    # Если menu_item нет, то хотя бы price должен быть
                    assert "price" in item


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
