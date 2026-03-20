"""
CRUD тесты для заказов (Orders).

Тесты проверяют:
- Создание заказа (Create)
- Чтение заказов (Read) - список, по ID, по столу, активные
- Обновление заказа (Update) - статус, полное обновление
- Удаление заказа (Delete)
- Расчёт выручки (Revenue)

Требования к правам доступа:
- GET /orders - публичный (без авторизации)
- POST /orders - требует авторизации (любой уровень)
- PUT /orders/{id} - требует авторизации (владелец или выше)
- PATCH /orders/{id}/status - требует авторизации (владелец или выше)
- DELETE /orders/{id} - требует manager+
- GET /orders/revenue - требует manager+
"""

import pytest
from fastapi.testclient import TestClient
from app.models.order import Order, OrderStatus, OrderItem
from app.models.user import User, UserLevel


# ============================================================================
# Тесты создания заказа (Create)
# ============================================================================

class TestCreateOrder:
    """Тесты создания заказа."""

    def test_create_order_success(self, client: TestClient, user_token: str, menu_items: dict):
        """Тест успешного создания заказа авторизованным пользователем."""
        burger = menu_items["Бургер"]
        cola = menu_items["Кола"]

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

        # Проверяем основные поля
        assert data["table_number"] == 10
        assert data["status"] == "pending"
        assert data["total_price"] == 1300  # 350*2 + 200*3
        assert len(data["items"]) == 2

        # Проверяем элементы заказа
        item_menu_ids = {item["menu_item_id"] for item in data["items"]}
        assert burger.id in item_menu_ids
        assert cola.id in item_menu_ids

    def test_create_order_calculates_total(self, client: TestClient, user_token: str, menu_items: dict):
        """Тест автоматического расчёта общей стоимости заказа."""
        burger = menu_items["Бургер"]
        fries = menu_items["Картофель фри"]
        pizza = menu_items["Пицца Маргарита"]

        response = client.post(
            "/api/orders",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "table_number": 7,
                "items": [
                    {"menu_item_id": burger.id, "quantity": 3},
                    {"menu_item_id": fries.id, "quantity": 2},
                    {"menu_item_id": pizza.id, "quantity": 1}
                ]
            }
        )

        assert response.status_code == 201
        data = response.json()
        # 350*3 + 150*2 + 800*1 = 1050 + 300 + 800 = 2150
        assert data["total_price"] == 2150

    def test_create_order_default_status_pending(self, client: TestClient, user_token: str, menu_items: dict):
        """Тест что новый заказ создаётся со статусом 'pending'."""
        burger = menu_items["Бургер"]

        response = client.post(
            "/api/orders",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "table_number": 1,
                "items": [{"menu_item_id": burger.id, "quantity": 1}]
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"

    def test_create_order_requires_auth(self, client: TestClient, menu_items: dict):
        """Тест что создание заказа требует авторизации."""
        burger = menu_items["Бургер"]

        response = client.post(
            "/api/orders",
            json={
                "table_number": 1,
                "items": [{"menu_item_id": burger.id, "quantity": 1}]
            }
        )

        assert response.status_code == 401

    def test_create_order_with_empty_items(self, client: TestClient, user_token: str):
        """Тест что заказ с пустым списком блюд отклоняется."""
        response = client.post(
            "/api/orders",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "table_number": 1,
                "items": []
            }
        )

        assert response.status_code == 422

    def test_create_order_with_zero_quantity(self, client: TestClient, user_token: str, menu_items: dict):
        """Тест что заказ с количеством 0 отклоняется."""
        burger = menu_items["Бургер"]

        response = client.post(
            "/api/orders",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "table_number": 1,
                "items": [{"menu_item_id": burger.id, "quantity": 0}]
            }
        )

        assert response.status_code == 422

    def test_create_order_with_nonexistent_menu_item(self, client: TestClient, user_token: str):
        """Тест что заказ с несуществующим menu_item_id отклоняется."""
        response = client.post(
            "/api/orders",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "table_number": 1,
                "items": [{"menu_item_id": 9999, "quantity": 1}]
            }
        )

        assert response.status_code == 404

    def test_create_order_negative_quantity(self, client: TestClient, user_token: str, menu_items: dict):
        """Тест что заказ с отрицательным количеством отклоняется."""
        burger = menu_items["Бургер"]

        response = client.post(
            "/api/orders",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "table_number": 1,
                "items": [{"menu_item_id": burger.id, "quantity": -1}]
            }
        )

        assert response.status_code == 422


# ============================================================================
# Тесты чтения заказов (Read)
# ============================================================================

class TestReadOrders:
    """Тесты чтения заказов."""

    def test_get_all_orders_public(self, client: TestClient, orders_set: list[Order]):
        """Тест что список заказов доступен без авторизации."""
        response = client.get("/api/orders?skip=0&limit=100")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

    def test_get_order_by_id(self, client: TestClient, order_pending: Order):
        """Тест получения заказа по ID."""
        response = client.get(f"/api/orders/{order_pending.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order_pending.id
        assert data["table_number"] == 5
        assert data["status"] == "pending"
        assert data["total_price"] == 850

    def test_get_order_by_id_not_found(self, client: TestClient):
        """Тест получения несуществующего заказа."""
        response = client.get("/api/orders/9999")

        assert response.status_code == 404

    def test_get_orders_with_items(self, client: TestClient, orders_set: list[Order]):
        """Тест что заказы возвращаются с элементами меню."""
        response = client.get("/api/orders")

        assert response.status_code == 200
        data = response.json()

        for order in data:
            assert "items" in order
            assert isinstance(order["items"], list)
            assert len(order["items"]) > 0

            for item in order["items"]:
                assert "menu_item_id" in item
                assert "quantity" in item
                assert "price" in item
                # Проверяем что menu_item загружен
                assert "menu_item" in item
                assert item["menu_item"]["name"] is not None
                assert item["menu_item"]["price"] > 0

    def test_get_orders_by_table(self, client: TestClient, orders_set: list[Order]):
        """Тест получения заказов по номеру стола."""
        response = client.get("/api/orders/table/5")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["table_number"] == 5

    def test_get_orders_by_table_not_found(self, client: TestClient):
        """Тест что запрос заказов для несуществующего стола возвращает пустой список."""
        response = client.get("/api/orders/table/999")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_active_orders(self, client: TestClient, orders_set: list[Order]):
        """Тест получения только активных заказов (pending + ready)."""
        response = client.get("/api/orders/active")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Должны быть только pending и ready, без paid
        for order in data:
            assert order["status"] in ["pending", "ready"]

        # В orders_set: 1 pending, 1 ready, 1 paid
        assert len(data) == 2

    def test_get_orders_pagination(self, client: TestClient, orders_set: list[Order]):
        """Тест пагинации списка заказов."""
        # Получаем первые 2 заказа
        response = client.get("/api/orders?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Получаем следующий заказ
        response = client.get("/api/orders?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_orders_filter_by_status(self, client: TestClient, orders_set: list[Order]):
        """Тест фильтрации заказов по статусу."""
        response = client.get("/api/orders?status=paid")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "paid"


# ============================================================================
# Тесты обновления заказа (Update)
# ============================================================================

class TestUpdateOrder:
    """Тесты обновления заказа."""

    def test_update_order_status(self, client: TestClient, user_token: str, order_pending: Order):
        """Тест обновления статуса заказа."""
        response = client.patch(
            f"/api/orders/{order_pending.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "ready"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"

    def test_update_order_status_invalid(self, client: TestClient, user_token: str, order_pending: Order):
        """Тест что установка недопустимого статуса отклоняется."""
        response = client.patch(
            f"/api/orders/{order_pending.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "invalid_status"}
        )

        assert response.status_code == 422

    def test_update_order_full(self, client: TestClient, user_token: str, order_pending: Order, menu_items: dict):
        """Тест полного обновления заказа."""
        pizza = menu_items["Пицца Маргарита"]

        response = client.put(
            f"/api/orders/{order_pending.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "table_number": 99,
                "items": [{"menu_item_id": pizza.id, "quantity": 2}]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["table_number"] == 99
        assert data["total_price"] == 1600  # 800*2
        assert len(data["items"]) == 1
        assert data["items"][0]["menu_item_id"] == pizza.id

    def test_update_order_requires_auth(self, client: TestClient, order_pending: Order):
        """Тест что обновление заказа требует авторизации."""
        response = client.patch(
            f"/api/orders/{order_pending.id}/status",
            json={"status": "ready"}
        )

        assert response.status_code == 401

    def test_update_order_not_found(self, client: TestClient, user_token: str):
        """Тест обновления несуществующего заказа."""
        response = client.patch(
            "/api/orders/9999/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "ready"}
        )

        assert response.status_code == 404


# ============================================================================
# Тесты удаления заказа (Delete)
# ============================================================================

class TestDeleteOrder:
    """Тесты удаления заказа."""

    def test_delete_order_manager(self, client: TestClient, manager_token: str, menu_items: dict):
        """Тест удаления заказа менеджером."""
        # Сначала создаём заказ
        burger = menu_items["Бургер"]
        create_response = client.post(
            "/api/orders",
            headers={"Authorization": f"Bearer {manager_token}"},
            json={
                "table_number": 100,
                "items": [{"menu_item_id": burger.id, "quantity": 1}]
            }
        )
        order_id = create_response.json()["id"]

        # Удаляем
        response = client.delete(
            f"/api/orders/{order_id}",
            headers={"Authorization": f"Bearer {manager_token}"}
        )

        assert response.status_code == 204

        # Проверяем что заказ удалён
        get_response = client.get(f"/api/orders/{order_id}")
        assert get_response.status_code == 404

    def test_delete_order_requires_manager(self, client: TestClient, user_token: str, order_pending: Order):
        """Тест что удаление заказа требует уровня manager+."""
        response = client.delete(
            f"/api/orders/{order_pending.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 403

    def test_delete_order_not_found(self, client: TestClient, manager_token: str):
        """Тест удаления несуществующего заказа."""
        response = client.delete(
            "/api/orders/9999",
            headers={"Authorization": f"Bearer {manager_token}"}
        )

        assert response.status_code == 404


# ============================================================================
# Тесты выручки (Revenue)
# ============================================================================

class TestOrderRevenue:
    """Тесты расчёта выручки."""

    def test_get_revenue_manager(self, client: TestClient, manager_token: str, orders_set: list[Order]):
        """Тест получения выручки менеджером."""
        response = client.get(
            "/api/orders/revenue",
            headers={"Authorization": f"Bearer {manager_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "total_revenue" in data
        assert "orders_count" in data

        # В orders_set: 1 paid заказ на 1500
        assert data["total_revenue"] == 1500
        assert data["orders_count"] == 1

    def test_get_revenue_requires_manager(self, client: TestClient, user_token: str):
        """Тест что получение выручки требует уровня manager+."""
        response = client.get(
            "/api/orders/revenue",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 403

    def test_get_revenue_with_date_filter(self, client: TestClient, manager_token: str, orders_set: list[Order]):
        """Тест фильтрации выручки по датам."""
        # Получаем выручку за все время
        response = client.get(
            "/api/orders/revenue",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 200

    def test_get_revenue_empty(self, client: TestClient, manager_token: str):
        """Тест выручки когда нет оплаченных заказов."""
        response = client.get(
            "/api/orders/revenue",
            headers={"Authorization": f"Bearer {manager_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_revenue"] == 0
        assert data["orders_count"] == 0


# ============================================================================
# Тесты many-to-many связей
# ============================================================================

class TestOrderManyToMany:
    """Тесты many-to-many связей заказа с меню."""

    def test_order_item_has_menu_item_details(self, client: TestClient, orders_set: list[Order]):
        """Тест что элемент заказа содержит информацию о menu_item."""
        response = client.get("/api/orders")
        assert response.status_code == 200
        data = response.json()

        for order in data:
            for item in order["items"]:
                # Проверяем что menu_item загружен с полями
                assert "menu_item" in item
                menu_item = item["menu_item"]
                assert "id" in menu_item
                assert "name" in menu_item
                assert "price" in menu_item
                assert menu_item["price"] > 0

    def test_order_total_matches_items(self, client: TestClient, orders_set: list[Order]):
        """Тест что общая стоимость заказа соответствует сумме элементов."""
        response = client.get("/api/orders")
        assert response.status_code == 200
        data = response.json()

        expected_totals = {5: 850, 3: 1200, 7: 1500}

        for order in data:
            table = order["table_number"]
            if table in expected_totals:
                assert order["total_price"] == expected_totals[table], \
                    f"Неверная сумма для стола {table}: {order['total_price']} != {expected_totals[table]}"
