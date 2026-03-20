"""
Интеграционные тесты всех API endpoints.

Тесты проверяют работу всех endpoints через TestClient (FastAPI):
- Auth endpoints (/api/auth/*)
- Users endpoints (/api/users/*)
- Orders endpoints (/api/orders/*)
- Menu items endpoints (/api/menu-items/*)
- Health check endpoint (/health)

В отличие от CRUD тестов, эти тесты проверяют endpoints "снаружи",
без прямого доступа к базе данных.
"""

import pytest
import uuid
from fastapi.testclient import TestClient


# ============================================================================
# Утилиты
# ============================================================================

def unique_email() -> str:
    """Генерирует уникальный email."""
    return f"test_{uuid.uuid4().hex[:8]}@test.com"


def unique_nickname() -> str:
    """Генерирует уникальный nickname."""
    return f"user_{uuid.uuid4().hex[:8]}"


# ============================================================================
# Фикстуры токенов
# ============================================================================

@pytest.fixture
def registered_user_token(client: TestClient) -> str:
    """Создаёт пользователя через API и возвращает токен."""
    email = unique_email()
    nickname = unique_nickname()

    # Регистрируем
    response = client.post("/api/auth/register", json={
        "email": email,
        "name": "Test",
        "surname": "User",
        "nickname": nickname,
        "password": "test123"
    })
    assert response.status_code == 201

    # Логинимся
    response = client.post("/api/auth/login", data={
        "username": email,
        "password": "test123"
    })
    assert response.status_code == 200

    return response.json()["access_token"]


@pytest.fixture
def admin_user_token(client: TestClient) -> str:
    """Создаёт администратора через API и возвращает токен."""
    email = unique_email()
    nickname = unique_nickname()

    # Регистрируем
    response = client.post("/api/auth/register", json={
        "email": email,
        "name": "Admin",
        "surname": "User",
        "nickname": nickname,
        "password": "admin123"
    })
    assert response.status_code == 201

    # Логинимся
    response = client.post("/api/auth/login", data={
        "username": email,
        "password": "admin123"
    })
    assert response.status_code == 200

    return response.json()["access_token"]


# ============================================================================
# Health Check
# ============================================================================

class TestHealthCheck:
    """Тесты health check endpoint."""

    def test_health_check(self, client: TestClient):
        """Тест проверки работоспособности API."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


# ============================================================================
# Auth Endpoints
# ============================================================================

class TestAuthEndpoints:
    """Тесты endpoints аутентификации."""

    def test_register_endpoint(self, client: TestClient):
        """POST /api/auth/register - регистрация."""
        email = unique_email()
        response = client.post("/api/auth/register", json={
            "email": email,
            "name": "Test",
            "surname": "User",
            "nickname": unique_nickname(),
            "password": "123456"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == email
        assert data["level"] == "client"

    def test_login_endpoint(self, client: TestClient):
        """POST /api/auth/login - вход."""
        email = unique_email()

        # Сначала регистрируем
        client.post("/api/auth/register", json={
            "email": email,
            "name": "Login",
            "surname": "Test",
            "nickname": unique_nickname(),
            "password": "password123"
        })

        # Логинимся
        response = client.post("/api/auth/login", data={
            "username": email,
            "password": "password123"
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_credentials(self, client: TestClient):
        """POST /api/auth/login - неправильные учётные данные."""
        response = client.post("/api/auth/login", data={
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        })

        assert response.status_code == 401


# ============================================================================
# Users Endpoints
# ============================================================================

class TestUsersEndpoints:
    """Тесты endpoints пользователей."""

    def test_get_users_me(self, client: TestClient, registered_user_token: str):
        """GET /api/users/me - текущий пользователь."""
        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {registered_user_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "nickname" in data

    def test_get_users_requires_manager(self, client: TestClient, registered_user_token: str):
        """GET /api/users - список пользователей (требует manager+)."""
        response = client.get(
            "/api/users?skip=0&limit=100",
            headers={"Authorization": f"Bearer {registered_user_token}"}
        )

        assert response.status_code == 403

    def test_get_user_by_id(self, client: TestClient, admin_user_token: str):
        """GET /api/users/{id} - пользователь по ID."""
        # Сначала получаем текущего пользователя чтобы узнать ID
        current = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {admin_user_token}"}
        )
        user_id = current.json()["id"]

        response = client.get(
            f"/api/users/{user_id}",
            headers={"Authorization": f"Bearer {admin_user_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id


# ============================================================================
# Orders Endpoints
# ============================================================================

class TestOrdersEndpoints:
    """Тесты endpoints заказов."""

    def test_get_orders_public(self, client: TestClient):
        """GET /api/orders - публичный доступ."""
        response = client.get("/api/orders?skip=0&limit=100")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_order(self, client: TestClient, registered_user_token: str, admin_user_token: str):
        """POST /api/orders - создание заказа."""
        # Сначала создаём элемент меню
        menu_response = client.post(
            "/api/menu-items",
            headers={"Authorization": f"Bearer {admin_user_token}"},
            json={
                "name": "Test Dish",
                "description": "Test",
                "price": 100,
                "category": "Test",
                "is_available": True
            }
        )
        assert menu_response.status_code == 201
        menu_item_id = menu_response.json()["id"]

        # Создаём заказ
        response = client.post(
            "/api/orders",
            headers={"Authorization": f"Bearer {registered_user_token}"},
            json={
                "table_number": 99,
                "items": [
                    {"menu_item_id": menu_item_id, "quantity": 1}
                ]
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["table_number"] == 99
        assert data["total_price"] == 100
        assert len(data["items"]) == 1

    def test_get_order_by_id(self, client: TestClient, registered_user_token: str, admin_user_token: str):
        """GET /api/orders/{id} - заказ по ID."""
        # Создаём элемент меню
        menu_response = client.post(
            "/api/menu-items",
            headers={"Authorization": f"Bearer {admin_user_token}"},
            json={
                "name": "Dish for Order",
                "description": "Test",
                "price": 50,
                "category": "Test",
                "is_available": True
            }
        )
        menu_item_id = menu_response.json()["id"]

        # Создаём заказ
        create_response = client.post(
            "/api/orders",
            headers={"Authorization": f"Bearer {registered_user_token}"},
            json={
                "table_number": 100,
                "items": [{"menu_item_id": menu_item_id, "quantity": 1}]
            }
        )
        order_id = create_response.json()["id"]

        # Получаем по ID
        response = client.get(f"/api/orders/{order_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order_id

    def test_update_order_status(self, client: TestClient, registered_user_token: str, admin_user_token: str):
        """PATCH /api/orders/{id}/status - изменение статуса."""
        # Создаём элемент меню
        menu_response = client.post(
            "/api/menu-items",
            headers={"Authorization": f"Bearer {admin_user_token}"},
            json={
                "name": "Dish for Status",
                "description": "Test",
                "price": 50,
                "category": "Test",
                "is_available": True
            }
        )
        menu_item_id = menu_response.json()["id"]

        # Создаём заказ
        create_response = client.post(
            "/api/orders",
            headers={"Authorization": f"Bearer {registered_user_token}"},
            json={
                "table_number": 101,
                "items": [{"menu_item_id": menu_item_id, "quantity": 1}]
            }
        )
        order_id = create_response.json()["id"]

        # Меняем статус
        response = client.patch(
            f"/api/orders/{order_id}/status",
            headers={"Authorization": f"Bearer {registered_user_token}"},
            json={"status": "ready"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"

    def test_get_active_orders(self, client: TestClient):
        """GET /api/orders/active - активные заказы."""
        response = client.get("/api/orders/active")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_orders_by_table(self, client: TestClient):
        """GET /api/orders/table/{table_number} - заказы по столу."""
        response = client.get("/api/orders/table/5")

        assert response.status_code == 200
        assert isinstance(response.json(), list)


# ============================================================================
# Menu Items Endpoints
# ============================================================================

class TestMenuItemsEndpoints:
    """Тесты endpoints меню."""

    def test_get_menu_items_public(self, client: TestClient):
        """GET /api/menu-items - публичный доступ."""
        response = client.get("/api/menu-items")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_menu_item_admin(self, client: TestClient, admin_user_token: str):
        """POST /api/menu-items - создание блюда (admin+)."""
        response = client.post(
            "/api/menu-items",
            headers={"Authorization": f"Bearer {admin_user_token}"},
            json={
                "name": "New Dish",
                "description": "Delicious",
                "price": 500,
                "category": "Main",
                "is_available": True
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Dish"
        assert data["price"] == 500

    def test_create_menu_item_requires_admin(self, client: TestClient, registered_user_token: str):
        """POST /api/menu-items - требует admin+."""
        response = client.post(
            "/api/menu-items",
            headers={"Authorization": f"Bearer {registered_user_token}"},
            json={
                "name": "Unauthorized Dish",
                "description": "Test",
                "price": 100,
                "category": "Test",
                "is_available": True
            }
        )

        assert response.status_code == 403

    def test_update_menu_item(self, client: TestClient, admin_user_token: str):
        """PUT /api/menu-items/{id} - обновление блюда."""
        # Создаём блюдо
        create_response = client.post(
            "/api/menu-items",
            headers={"Authorization": f"Bearer {admin_user_token}"},
            json={
                "name": "Update Test",
                "description": "Original",
                "price": 100,
                "category": "Test",
                "is_available": True
            }
        )
        menu_item_id = create_response.json()["id"]

        # Обновляем
        response = client.put(
            f"/api/menu-items/{menu_item_id}",
            headers={"Authorization": f"Bearer {admin_user_token}"},
            json={
                "name": "Updated Dish",
                "description": "Updated",
                "price": 200,
                "category": "Updated",
                "is_available": False
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Dish"
        assert data["price"] == 200

    def test_delete_menu_item(self, client: TestClient, admin_user_token: str):
        """DELETE /api/menu-items/{id} - удаление блюда."""
        # Создаём блюдо
        create_response = client.post(
            "/api/menu-items",
            headers={"Authorization": f"Bearer {admin_user_token}"},
            json={
                "name": "Delete Test",
                "description": "To Delete",
                "price": 100,
                "category": "Test",
                "is_available": True
            }
        )
        menu_item_id = create_response.json()["id"]

        # Удаляем
        response = client.delete(
            f"/api/menu-items/{menu_item_id}",
            headers={"Authorization": f"Bearer {admin_user_token}"}
        )

        assert response.status_code == 204

        # Проверяем что удалено
        get_response = client.get(f"/api/menu-items/{menu_item_id}")
        assert get_response.status_code == 404

    def test_get_menu_item_categories(self, client: TestClient):
        """GET /api/menu-items/categories - список категорий."""
        response = client.get("/api/menu-items/categories")

        assert response.status_code == 200
        assert isinstance(response.json(), list)


# ============================================================================
# Revenue Endpoint
# ============================================================================

class TestRevenueEndpoint:
    """Тесты endpoint выручки."""

    def test_get_revenue_requires_manager(self, client: TestClient, registered_user_token: str):
        """GET /api/orders/revenue - требует manager+."""
        response = client.get(
            "/api/orders/revenue",
            headers={"Authorization": f"Bearer {registered_user_token}"}
        )

        assert response.status_code == 403


# ============================================================================
# Error Handling
# ============================================================================

class TestErrorHandling:
    """Тесты обработки ошибок."""

    def test_404_not_found(self, client: TestClient):
        """Тест обработки 404 ошибки."""
        response = client.get("/api/nonexistent-endpoint")
        assert response.status_code == 404

    def test_401_unauthorized(self, client: TestClient):
        """Тест обработки 401 ошибки."""
        response = client.get(
            "/api/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    def test_422_validation_error(self, client: TestClient):
        """Тест обработки 422 ошибки валидации."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "invalid-email",  # Невалидный email
                "name": "Test",
                "surname": "User",
                "nickname": "test",
                "password": "12"  # Слишком короткий пароль
            }
        )
        assert response.status_code == 422

    def test_409_conflict_duplicate_email(self, client: TestClient):
        """Тест обработки 409 ошибки (дубликат)."""
        email = unique_email()
        nickname = unique_nickname()

        # Первая регистрация
        client.post("/api/auth/register", json={
            "email": email,
            "name": "Test",
            "surname": "User",
            "nickname": nickname,
            "password": "123456"
        })

        # Вторая регистрация с тем же email
        response = client.post("/api/auth/register", json={
            "email": email,
            "name": "Test2",
            "surname": "User2",
            "nickname": unique_nickname(),
            "password": "123456"
        })

        assert response.status_code == 409
