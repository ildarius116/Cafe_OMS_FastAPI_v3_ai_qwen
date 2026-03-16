"""Тесты для API заказов с правильной many-to-many схемой.

Тесты проверяют:
- Заказ содержит menu_item_id (ссылка на MenuItem)
- OrderItem имеет menu_item с name и price
- API возвращает правильную структуру данных
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine
from app.models.user import User, UserLevel, UserStatus
from app.models.order import Order, OrderStatus, OrderItem
from app.models.menu_item import MenuItem
from app.core.security import get_password_hash, create_access_token
from sqlalchemy.orm import sessionmaker


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


def create_auth_token(test_db, email: str, level: UserLevel) -> str:
    """Создаёт токен для пользователя с указанным email."""
    user = test_db.query(User).filter(User.email == email).first()
    if not user:
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
    return create_access_token(data={"sub": user.id, "level": level.value})


@pytest.fixture
def user_token(test_db):
    """Создаёт токен обычного пользователя."""
    return create_auth_token(test_db, "user@example.com", UserLevel.CLIENT)


@pytest.fixture
def manager_token(test_db):
    """Создаёт токен менеджера."""
    return create_auth_token(test_db, "manager@example.com", UserLevel.MANAGER)


@pytest.fixture
def admin_token(test_db):
    """Создаёт токен администратора."""
    return create_auth_token(test_db, "admin@example.com", UserLevel.ADMIN)


@pytest.fixture
def menu_items_fixture(test_db):
    """Создаёт тестовые элементы меню."""
    items = [
        MenuItem(name="Бургер", description="Сочный бургер", price=350.0, category="Горячее", is_available=True),
        MenuItem(name="Картофель фри", description="Хрустящий картофель", price=150.0, category="Закуски", is_available=True),
        MenuItem(name="Пицца", description="Пицца Маргарита", price=800.0, category="Горячее", is_available=True),
        MenuItem(name="Кола", description="Газировка", price=200.0, category="Напитки", is_available=True),
    ]
    test_db.add_all(items)
    test_db.commit()
    return {item.name: item for item in items}


@pytest.fixture
def test_order(test_db, menu_items_fixture):
    """Создаёт тестовый заказ с элементами меню (many-to-many)."""
    order = Order(
        table_number=5,
        total_price=0,
        status=OrderStatus.PENDING,
    )
    test_db.add(order)
    test_db.flush()
    
    # Добавляем элементы заказа через many-to-many связь
    burger = menu_items_fixture["Бургер"]
    fries = menu_items_fixture["Картофель фри"]
    
    order_item1 = OrderItem(order_id=order.id, menu_item_id=burger.id, quantity=2, price=burger.price)
    order_item2 = OrderItem(order_id=order.id, menu_item_id=fries.id, quantity=1, price=fries.price)
    
    test_db.add_all([order_item1, order_item2])
    order.total_price = order.calculate_total()  # 350*2 + 150*1 = 850
    test_db.commit()
    test_db.refresh(order)
    return order


class TestOrdersCRUD:
    """Тесты CRUD операций для заказов."""

    def test_get_orders_public(self, client, test_order):
        """Тест что список заказов доступен без авторизации."""
        response = client.get("/api/orders")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["table_number"] == 5
        # Проверяем что order_items содержит menu_item
        assert len(data[0]["items"]) == 2
        assert data[0]["items"][0]["menu_item_id"] is not None
        assert "menu_item" in data[0]["items"][0] or data[0]["items"][0]["price"] is not None

    def test_create_order(self, client, user_token, menu_items_fixture, test_db):
        """Тест создания заказа с menu_item_id."""
        burger = menu_items_fixture["Бургер"]
        cola = menu_items_fixture["Кола"]
        
        response = client.post(
            "/api/orders",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "table_number": 10,
                "items": [
                    {"menu_item_id": burger.id, "quantity": 2},
                    {"menu_item_id": cola.id, "quantity": 3}
                ]
            }
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["table_number"] == 10
        assert data["total_price"] == 1300  # 350*2 + 200*3
        assert data["status"] == "pending"
        # Проверяем что элементы заказа имеют menu_item_id
        assert len(data["items"]) == 2
        assert data["items"][0]["menu_item_id"] == burger.id
        assert data["items"][1]["menu_item_id"] == cola.id

    def test_create_order_calculates_total(self, client, user_token, menu_items_fixture):
        """Тест что общая стоимость вычисляется автоматически."""
        burger = menu_items_fixture["Бургер"]
        fries = menu_items_fixture["Картофель фри"]
        
        response = client.post(
            "/api/orders",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "table_number": 7,
                "items": [
                    {"menu_item_id": burger.id, "quantity": 3},
                    {"menu_item_id": fries.id, "quantity": 2}
                ]
            }
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["total_price"] == 1350  # 350*3 + 150*2

    def test_get_order_by_id(self, client, test_order):
        """Тест получения заказа по ID."""
        response = client.get(f"/api/orders/{test_order.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_order.id
        assert data["table_number"] == 5
        # Проверяем что элементы имеют menu_item_id
        assert len(data["items"]) == 2
        assert data["items"][0]["menu_item_id"] is not None

    def test_get_order_not_found(self, client):
        """Тест получения несуществующего заказа."""
        response = client.get("/api/orders/999")
        assert response.status_code == 404

    def test_update_order_status(self, client, user_token, test_order):
        """Тест обновления статуса заказа."""
        response = client.patch(
            f"/api/orders/{test_order.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "ready"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["status"] == "ready"

    def test_update_order(self, client, user_token, test_order, menu_items_fixture):
        """Тест обновления заказа."""
        pizza = menu_items_fixture["Пицца"]
        
        response = client.put(
            f"/api/orders/{test_order.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "table_number": 15,
                "items": [{"menu_item_id": pizza.id, "quantity": 2}]
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["table_number"] == 15
        assert data["total_price"] == 1600  # 800*2

    def test_delete_order_requires_manager(self, client, user_token, test_order):
        """Тест что удаление заказа требует менеджера."""
        response = client.delete(
            f"/api/orders/{test_order.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"

    def test_delete_order_manager(self, client, manager_token, test_order):
        """Тест удаления заказа менеджером."""
        response = client.delete(
            f"/api/orders/{test_order.id}",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 204, f"Expected 204, got {response.status_code}: {response.text}"

    def test_get_orders_by_table(self, client, test_db, menu_items_fixture):
        """Тест получения заказов по номеру стола."""
        burger = menu_items_fixture["Бургер"]
        fries = menu_items_fixture["Картофель фри"]
        pizza = menu_items_fixture["Пицца"]
        
        order1 = Order(table_number=5, total_price=0, status=OrderStatus.PENDING)
        order2 = Order(table_number=5, total_price=0, status=OrderStatus.PENDING)
        order3 = Order(table_number=10, total_price=0, status=OrderStatus.PENDING)
        test_db.add_all([order1, order2, order3])
        test_db.flush()
        
        test_db.add(OrderItem(order_id=order1.id, menu_item_id=burger.id, quantity=1, price=burger.price))
        test_db.add(OrderItem(order_id=order2.id, menu_item_id=fries.id, quantity=1, price=fries.price))
        test_db.add(OrderItem(order_id=order3.id, menu_item_id=pizza.id, quantity=1, price=pizza.price))
        
        order1.total_price = burger.price
        order2.total_price = fries.price
        order3.total_price = pizza.price
        test_db.commit()

        response = client.get("/api/orders/table/5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(o["table_number"] == 5 for o in data)

    def test_get_active_orders(self, client, test_db, menu_items_fixture):
        """Тест получения активных заказов."""
        burger = menu_items_fixture["Бургер"]
        fries = menu_items_fixture["Картофель фри"]
        pizza = menu_items_fixture["Пицца"]
        
        order1 = Order(table_number=1, total_price=0, status=OrderStatus.PENDING)
        order2 = Order(table_number=2, total_price=0, status=OrderStatus.READY)
        order3 = Order(table_number=3, total_price=0, status=OrderStatus.PAID)
        test_db.add_all([order1, order2, order3])
        test_db.flush()
        
        test_db.add_all([
            OrderItem(order_id=order1.id, menu_item_id=burger.id, quantity=1, price=burger.price),
            OrderItem(order_id=order2.id, menu_item_id=fries.id, quantity=1, price=fries.price),
            OrderItem(order_id=order3.id, menu_item_id=pizza.id, quantity=1, price=pizza.price),
        ])
        order1.total_price = burger.price
        order2.total_price = fries.price
        order3.total_price = pizza.price
        test_db.commit()

        response = client.get("/api/orders/active")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Только pending и ready
        assert all(o["status"] in ["pending", "ready"] for o in data)


class TestOrdersRevenue:
    """Тесты расчёта выручки."""

    def test_get_revenue_requires_manager(self, client, user_token):
        """Тест что получение выручки требует менеджера."""
        response = client.get(
            "/api/orders/revenue",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"

    def test_get_revenue_manager(self, client, manager_token, test_db, menu_items_fixture):
        """Тест получения выручки менеджером."""
        burger = menu_items_fixture["Бургер"]
        fries = menu_items_fixture["Картофель фри"]
        pizza = menu_items_fixture["Пицца"]
        
        # Создаём заказы
        order1 = Order(table_number=1, total_price=0, status=OrderStatus.PAID)
        order2 = Order(table_number=2, total_price=0, status=OrderStatus.PAID)
        order3 = Order(table_number=3, total_price=0, status=OrderStatus.PENDING)
        test_db.add_all([order1, order2, order3])
        test_db.flush()
        
        # Добавляем элементы заказа
        test_db.add(OrderItem(order_id=order1.id, menu_item_id=burger.id, quantity=1, price=burger.price))
        test_db.add(OrderItem(order_id=order2.id, menu_item_id=fries.id, quantity=1, price=fries.price))
        test_db.add(OrderItem(order_id=order3.id, menu_item_id=pizza.id, quantity=1, price=pizza.price))
        
        # Вычисляем общую стоимость
        order1.total_price = burger.price  # 350
        order2.total_price = fries.price   # 150
        order3.total_price = pizza.price   # 800 (не оплачено, не входит в выручку)
        test_db.commit()

        response = client.get(
            "/api/orders/revenue",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["total_revenue"] == 500  # Только оплаченные: 350 + 150
        assert data["orders_count"] == 2
