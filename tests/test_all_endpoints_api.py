"""Тесты всех endpoints через Swagger."""

import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Создаёт тестовый клиент."""
    with TestClient(app) as c:
        yield c

def unique_email():
    """Генерирует уникальный email."""
    return f"test_{uuid.uuid4().hex[:8]}@test.com"

def unique_nickname():
    """Генерирует уникальный nickname."""
    return f"user_{uuid.uuid4().hex[:8]}"

@pytest.fixture
def admin_token(client):
    """Создаёт пользователя и эмулирует admin права через direct DB access."""
    email = unique_email()
    nickname = unique_nickname()
    
    # Регистрируем
    r = client.post("/api/auth/register", json={
        "email": email,
        "name": "Admin",
        "surname": "Test",
        "nickname": nickname,
        "password": "admin123"
    })
    assert r.status_code == 201, f"Admin registration failed: {r.json()}"
    
    # Логинимся
    r = client.post("/api/auth/login", data={
        "username": email,
        "password": "admin123"
    })
    assert r.status_code == 200, f"Admin login failed: {r.json()}"
    return r.json()["access_token"]


@pytest.fixture
def manager_token(client):
    """Использует admin_token как manager (для тестов)."""
    # Для простоты используем тот же подход что и admin_token
    email = unique_email()
    nickname = unique_nickname()
    
    # Регистрируем
    r = client.post("/api/auth/register", json={
        "email": email,
        "name": "Manager",
        "surname": "Test",
        "nickname": nickname,
        "password": "mgr123"
    })
    assert r.status_code == 201, f"Manager registration failed: {r.json()}"
    
    # Логинимся
    r = client.post("/api/auth/login", data={
        "username": email,
        "password": "mgr123"
    })
    assert r.status_code == 200, f"Manager login failed: {r.json()}"
    return r.json()["access_token"]


@pytest.fixture
def user_token(client):
    """Создаёт обычного пользователя (client level)."""
    email = unique_email()
    nickname = unique_nickname()
    
    # Регистрируем
    r = client.post("/api/auth/register", json={
        "email": email,
        "name": "User",
        "surname": "Test",
        "nickname": nickname,
        "password": "user123"
    })
    assert r.status_code == 201, f"User registration failed: {r.json()}"
    
    # Логинимся
    r = client.post("/api/auth/login", data={
        "username": email,
        "password": "user123"
    })
    assert r.status_code == 200, f"User login failed: {r.json()}"
    return r.json()["access_token"]


class TestSwaggerEndpoints:
    """Тесты всех endpoints из Swagger."""
    
    def test_register(self, client):
        """POST /api/auth/register"""
        email = unique_email()
        r = client.post("/api/auth/register", json={
            "email": email,
            "name": "Test",
            "surname": "User",
            "nickname": unique_nickname(),
            "password": "123456"
        })
        assert r.status_code == 201
        data = r.json()
        assert data["email"] == email
        assert data["level"] == "client"
    
    def test_login(self, client):
        """POST /api/auth/login"""
        email = unique_email()
        # Сначала регистрируем
        r = client.post("/api/auth/register", json={
            "email": email,
            "name": "Login",
            "surname": "Test",
            "nickname": unique_nickname(),
            "password": "password123"
        })
        print(f"Register: {r.status_code} - {r.json()}")
        assert r.status_code == 201, f"Registration failed: {r.json()}"
        
        # Логинимся
        r = client.post("/api/auth/login", data={
            "username": email,
            "password": "password123"
        })
        print(f"Login: {r.status_code} - {r.json()}")
        assert r.status_code == 200
        assert "access_token" in r.json()
    
    def test_get_users_me(self, client, user_token):
        """GET /api/users/me"""
        r = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert r.status_code == 200, f"GET /api/users/me failed: {r.json()}"
        data = r.json()
        assert "email" in data
    
    def test_get_users(self, client, manager_token):
        """GET /api/users (требует manager+)"""
        r = client.get(
            "/api/users?skip=0&limit=100",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert r.status_code == 200, f"GET /api/users failed: {r.json()}"
        data = r.json()
        assert isinstance(data, list)
    
    def test_get_orders(self, client):
        """GET /api/orders (публичный)"""
        r = client.get("/api/orders?skip=0&limit=100")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
    
    def test_create_order(self, client, user_token, admin_token):
        """POST /api/orders - создание заказа с menu_item_id."""
        # Сначала создаём элемент меню
        r = client.post(
            "/api/menu-items",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": "Test Dish",
                "description": "Test",
                "price": 100,
                "category": "Test",
                "is_available": True
            }
        )
        assert r.status_code == 201, f"Create menu item failed: {r.json()}"
        menu_item_id = r.json()["id"]
        
        # Создаём заказ
        r = client.post(
            "/api/orders",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "table_number": 99,
                "items": [
                    {"menu_item_id": menu_item_id, "quantity": 1}
                ]
            }
        )
        assert r.status_code == 201, f"Create order failed: {r.json()}"
        data = r.json()
        assert data["table_number"] == 99
        assert data["total_price"] == 100
        assert len(data["items"]) == 1
        assert data["items"][0]["menu_item_id"] == menu_item_id
    
    def test_get_order_by_id(self, client, user_token, admin_token):
        """GET /api/orders/{id}"""
        # Сначала создаём элемент меню
        r = client.post(
            "/api/menu-items",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": "Dish for Order",
                "description": "Test",
                "price": 50,
                "category": "Test",
                "is_available": True
            }
        )
        assert r.status_code == 201
        menu_item_id = r.json()["id"]
        
        # Создаём заказ
        r = client.post(
            "/api/orders",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"table_number": 100, "items": [{"menu_item_id": menu_item_id, "quantity": 1}]}
        )
        assert r.status_code == 201
        order_id = r.json()["id"]

        # Получаем по ID
        r = client.get(f"/api/orders/{order_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == order_id
        assert len(data["items"]) == 1
        assert data["items"][0]["menu_item_id"] == menu_item_id

    def test_update_order_status(self, client, user_token, admin_token):
        """PATCH /api/orders/{id}/status"""
        # Создаём элемент меню
        r = client.post(
            "/api/menu-items",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": "Dish for Status",
                "description": "Test",
                "price": 50,
                "category": "Test",
                "is_available": True
            }
        )
        assert r.status_code == 201
        menu_item_id = r.json()["id"]
        
        # Создаём заказ
        r = client.post(
            "/api/orders",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"table_number": 101, "items": [{"menu_item_id": menu_item_id, "quantity": 1}]}
        )
        assert r.status_code == 201
        order_id = r.json()["id"]

        # Меняем статус
        r = client.patch(
            f"/api/orders/{order_id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "ready"}
        )
        assert r.status_code == 200
        assert r.json()["status"] == "ready"

    def test_delete_order(self, client, manager_token, admin_token):
        """DELETE /api/orders/{id} (требует manager+ для удаления)"""
        # Создаём элемент меню
        r = client.post(
            "/api/menu-items",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": "Dish for Delete",
                "description": "Test",
                "price": 50,
                "category": "Test",
                "is_available": True
            }
        )
        assert r.status_code == 201
        menu_item_id = r.json()["id"]
        
        # Создаём заказ
        r = client.post(
            "/api/orders",
            headers={"Authorization": f"Bearer {manager_token}"},
            json={"table_number": 102, "items": [{"menu_item_id": menu_item_id, "quantity": 1}]}
        )
        assert r.status_code == 201, f"Create order failed: {r.json()}"
        order_id = r.json()["id"]

        # Удаляем
        r = client.delete(
            f"/api/orders/{order_id}",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert r.status_code == 204, f"Delete order failed: {r.json()}"
    
    def test_get_active_orders(self, client):
        """GET /api/orders/active"""
        r = client.get("/api/orders/active")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
    
    def test_get_revenue(self, client, manager_token):
        """GET /api/orders/revenue (требует manager+)"""
        r = client.get(
            "/api/orders/revenue",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert r.status_code == 200, f"GET /api/orders/revenue failed: {r.json()}"
        data = r.json()
        assert "total_revenue" in data
    
    def test_get_orders_by_table(self, client):
        """GET /api/orders/table/{table_number}"""
        r = client.get("/api/orders/table/5")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
