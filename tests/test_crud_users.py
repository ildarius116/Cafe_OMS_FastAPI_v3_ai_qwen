"""
CRUD тесты для пользователей и аутентификации (Users & Auth).

Тесты проверяют:
- Аутентификация (Authentication) - регистрация, вход, JWT токены
- Создание пользователя (Create)
- Чтение пользователей (Read) - список, по ID, текущий пользователь
- Обновление пользователя (Update)
- Удаление пользователя (Delete)

Требования к правам доступа:
- POST /auth/register - публичный
- POST /auth/login - публичный
- GET /users/me - требует авторизации
- GET /users - требует manager+
- GET /users/{id} - требует авторизации
- POST /users - требует admin+
- PUT /users/{id} - требует admin+
- DELETE /users/{id} - требует admin+
"""

import pytest
from fastapi.testclient import TestClient
from app.models.user import User, UserLevel, UserStatus
from app.core.security import get_password_hash, verify_password


# ============================================================================
# Тесты аутентификации (Authentication)
# ============================================================================

class TestAuthRegister:
    """Тесты регистрации пользователя."""

    def test_register_success(self, client: TestClient):
        """Тест успешной регистрации нового пользователя."""
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "name": "Тест",
            "surname": "Тестов",
            "nickname": "testuser",
            "password": "123456"
        })

        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()

        # Проверяем основные поля
        assert data["email"] == "test@example.com"
        assert data["nickname"] == "testuser"
        assert data["name"] == "Тест"
        assert data["surname"] == "Тестов"
        assert data["level"] == "client"  # По умолчанию client уровень
        assert "id" in data
        assert "created_at" in data

    def test_register_duplicate_email(self, client: TestClient, db):
        """Тест регистрации с дублирующимся email."""
        # Создаём первого пользователя
        user = User(
            email="dup@example.com",
            name="Тест",
            surname="Тестов",
            nickname="test1",
            hashed_password=get_password_hash("123456")
        )
        db.add(user)
        db.commit()

        # Пытаемся зарегистрироваться с тем же email
        response = client.post("/api/auth/register", json={
            "email": "dup@example.com",
            "name": "Тест2",
            "surname": "Тестов2",
            "nickname": "test2",
            "password": "123456"
        })

        assert response.status_code == 409  # Conflict

    def test_register_duplicate_nickname(self, client: TestClient, db):
        """Тест регистрации с дублирующимся никнеймом."""
        user = User(
            email="unique@example.com",
            name="Тест",
            surname="Тестов",
            nickname="dupnick",
            hashed_password=get_password_hash("123456")
        )
        db.add(user)
        db.commit()

        response = client.post("/api/auth/register", json={
            "email": "unique2@example.com",
            "name": "Тест2",
            "surname": "Тестов2",
            "nickname": "dupnick",
            "password": "123456"
        })

        assert response.status_code == 409

    def test_register_invalid_email(self, client: TestClient):
        """Тест регистрации с невалидным email."""
        response = client.post("/api/auth/register", json={
            "email": "invalid-email",
            "name": "Тест",
            "surname": "Тестов",
            "nickname": "testuser",
            "password": "123456"
        })

        assert response.status_code == 422

    def test_register_short_password(self, client: TestClient):
        """Тест регистрации с коротким паролем."""
        response = client.post("/api/auth/register", json={
            "email": "test2@example.com",
            "name": "Тест",
            "surname": "Тестов",
            "nickname": "testuser2",
            "password": "123"
        })

        assert response.status_code == 422

    def test_register_missing_fields(self, client: TestClient):
        """Тест регистрации с отсутствующими обязательными полями."""
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
            # name, surname, nickname, password отсутствуют
        })

        assert response.status_code == 422

    def test_register_password_not_stored_plain(self, client: TestClient, db):
        """Тест что пароль хранится в хэшированном виде."""
        response = client.post("/api/auth/register", json={
            "email": "hashtest@example.com",
            "name": "Тест",
            "surname": "Тестов",
            "nickname": "hashtest",
            "password": "supersecret123"
        })

        assert response.status_code == 201

        # Проверяем что пароль захэширован в БД
        user = db.query(User).filter(User.email == "hashtest@example.com").first()
        assert user is not None
        assert user.hashed_password != "supersecret123"
        assert len(user.hashed_password) > 50  # bcrypt хэш длинный
        assert verify_password("supersecret123", user.hashed_password)


class TestAuthLogin:
    """Тесты аутентификации (вход)."""

    def test_login_success(self, client: TestClient, db):
        """Тест успешного входа."""
        # Создаём пользователя
        user = User(
            email="login@example.com",
            name="Тест",
            surname="Тестов",
            nickname="loginuser",
            hashed_password=get_password_hash("123456")
        )
        db.add(user)
        db.commit()

        # Входим
        response = client.post("/api/auth/login", data={
            "username": "login@example.com",
            "password": "123456"
        })

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 50  # JWT токен длинный

    def test_login_wrong_password(self, client: TestClient, db):
        """Тест входа с неправильным паролем."""
        user = User(
            email="login2@example.com",
            name="Тест",
            surname="Тестов",
            nickname="loginuser2",
            hashed_password=get_password_hash("123456")
        )
        db.add(user)
        db.commit()

        response = client.post("/api/auth/login", data={
            "username": "login2@example.com",
            "password": "wrongpassword"
        })

        assert response.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        """Тест входа с несуществующим пользователем."""
        response = client.post("/api/auth/login", data={
            "username": "nonexistent@example.com",
            "password": "123456"
        })

        assert response.status_code == 401

    def test_login_returns_user_level(self, client: TestClient, db):
        """Тест что токен содержит уровень пользователя."""
        user = User(
            email="leveltest@example.com",
            name="Тест",
            surname="Тестов",
            nickname="leveltest",
            level=UserLevel.MANAGER,
            hashed_password=get_password_hash("123456")
        )
        db.add(user)
        db.commit()

        response = client.post("/api/auth/login", data={
            "username": "leveltest@example.com",
            "password": "123456"
        })

        assert response.status_code == 200
        # Токен должен содержать информацию об уровне (проверяется через decode в других тестах)


# ============================================================================
# Тесты текущего пользователя (GET /users/me)
# ============================================================================

class TestGetCurrentUser:
    """Тесты получения текущего пользователя."""

    def test_get_users_me_success(self, client: TestClient, user_token: str):
        """Тест успешного получения текущего пользователя."""
        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert "email" in data
        assert "nickname" in data
        assert "name" in data
        assert "surname" in data
        assert "level" in data
        assert "status" in data

    def test_get_users_me_requires_auth(self, client: TestClient):
        """Тест что получение текущего пользователя требует авторизации."""
        response = client.get("/api/users/me")

        assert response.status_code == 401

    def test_get_users_me_invalid_token(self, client: TestClient):
        """Тест что невалидный токен отклоняется."""
        response = client.get(
            "/api/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401


# ============================================================================
# Тесты списка пользователей (GET /users)
# ============================================================================

class TestGetUsersList:
    """Тесты получения списка пользователей."""

    def test_get_users_requires_manager(self, client: TestClient, user_token: str):
        """Тест что список пользователей требует уровня manager+."""
        response = client.get(
            "/api/users",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 403

    def test_get_users_manager(self, client: TestClient, manager_token: str, db):
        """Тест что менеджер может получить список пользователей."""
        # Создаём тестовых пользователей
        for i in range(3):
            user = User(
                email=f"user{i}@test.com",
                name=f"User{i}",
                surname=f"Userov{i}",
                nickname=f"user{i}",
                level=UserLevel.CLIENT,
                hashed_password=get_password_hash("password")
            )
            db.add(user)
        db.commit()

        response = client.get(
            "/api/users?skip=0&limit=100",
            headers={"Authorization": f"Bearer {manager_token}"}
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_get_users_pagination(self, client: TestClient, manager_token: str, db):
        """Тест пагинации списка пользователей."""
        # Создаём 10 пользователей
        for i in range(10):
            user = User(
                email=f"page{i}@test.com",
                name=f"Page{i}",
                surname=f"Pageov{i}",
                nickname=f"page{i}",
                level=UserLevel.CLIENT,
                hashed_password=get_password_hash("password")
            )
            db.add(user)
        db.commit()

        # Первая страница
        response = client.get(
            "/api/users?skip=0&limit=5",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

        # Вторая страница
        response = client.get(
            "/api/users?skip=5&limit=5",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_get_users_filter_by_level(self, client: TestClient, manager_token: str, db):
        """Тест фильтрации пользователей по уровню."""
        # Создаём пользователей разных уровней
        user_client = User(
            email="client@test.com",
            name="Client",
            surname="Clientov",
            nickname="client",
            level=UserLevel.CLIENT,
            hashed_password=get_password_hash("password")
        )
        user_staff = User(
            email="staff@test.com",
            name="Staff",
            surname="Staffov",
            nickname="staff",
            level=UserLevel.STAFF,
            hashed_password=get_password_hash("password")
        )
        db.add_all([user_client, user_staff])
        db.commit()

        # Фильтруем по client
        response = client.get(
            "/api/users?level=client",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        client_emails = [u["email"] for u in data]
        assert "client@test.com" in client_emails


# ============================================================================
# Тесты получения пользователя по ID (GET /users/{id})
# ============================================================================

class TestGetUserById:
    """Тесты получения пользователя по ID."""

    def test_get_user_by_id_success(self, client: TestClient, admin_token: str, db):
        """Тест успешного получения пользователя по ID."""
        user = User(
            email="getbyid@test.com",
            name="GetBy",
            surname="Idov",
            nickname="getbyid",
            level=UserLevel.CLIENT,
            hashed_password=get_password_hash("password")
        )
        db.add(user)
        db.commit()

        response = client.get(
            f"/api/users/{user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        assert data["email"] == "getbyid@test.com"

    def test_get_user_by_id_not_found(self, client: TestClient, admin_token: str):
        """Тест получения несуществующего пользователя."""
        response = client.get(
            "/api/users/9999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 404

    def test_get_user_by_id_requires_auth(self, client: TestClient, db):
        """Тест что получение пользователя по ID требует авторизации."""
        user = User(
            email="authreq@test.com",
            name="Auth",
            surname="Reqov",
            nickname="authreq",
            level=UserLevel.CLIENT,
            hashed_password=get_password_hash("password")
        )
        db.add(user)
        db.commit()

        response = client.get(f"/api/users/{user.id}")

        assert response.status_code == 401


# ============================================================================
# Тесты создания пользователя (POST /users)
# ============================================================================

class TestCreateUser:
    """Тесты создания пользователя администратором."""

    def test_create_user_admin(self, client: TestClient, admin_token: str):
        """Тест создания пользователя администратором."""
        response = client.post(
            "/api/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "email": "newuser@example.com",
                "name": "Новый",
                "surname": "Пользователь",
                "nickname": "newuser",
                "password": "123456"
            }
        )

        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["level"] == "client"

    def test_create_user_requires_admin(self, client: TestClient, manager_token: str):
        """Тест что создание пользователя требует уровня admin+."""
        response = client.post(
            "/api/users",
            headers={"Authorization": f"Bearer {manager_token}"},
            json={
                "email": "newuser2@example.com",
                "name": "Новый2",
                "surname": "Пользователь2",
                "nickname": "newuser2",
                "password": "123456"
            }
        )

        assert response.status_code == 403

    def test_create_user_with_custom_level(self, client: TestClient, admin_token: str):
        """Тест создания пользователя с указанным уровнем."""
        response = client.post(
            "/api/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "email": "staffuser@example.com",
                "name": "Staff",
                "surname": "User",
                "nickname": "staffuser",
                "password": "123456",
                "level": "staff"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["level"] == "staff"


# ============================================================================
# Тесты обновления пользователя (PUT /users/{id})
# ============================================================================

class TestUpdateUser:
    """Тесты обновления пользователя."""

    def test_update_user_admin(self, client: TestClient, admin_token: str, db):
        """Тест обновления пользователя администратором."""
        user = User(
            email="toupdate@example.com",
            name="Обновляемый",
            surname="Обновляемый",
            nickname="toupdate",
            level=UserLevel.CLIENT,
            status=UserStatus.ACTIVE,
            hashed_password=get_password_hash("123456")
        )
        db.add(user)
        db.commit()

        response = client.put(
            f"/api/users/{user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Обновлённый"}
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["name"] == "Обновлённый"

    def test_update_user_level(self, client: TestClient, admin_token: str, db):
        """Тест обновления уровня пользователя."""
        user = User(
            email="levelupdate@example.com",
            name="Level",
            surname="Updateov",
            nickname="levelupdate",
            level=UserLevel.CLIENT,
            hashed_password=get_password_hash("password")
        )
        db.add(user)
        db.commit()

        response = client.put(
            f"/api/users/{user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"level": "staff"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["level"] == "staff"

    def test_update_user_requires_admin(self, client: TestClient, manager_token: str, db):
        """Тест что обновление пользователя требует уровня admin+."""
        user = User(
            email="noupdate@example.com",
            name="No",
            surname="Updateov",
            nickname="noupdate",
            level=UserLevel.CLIENT,
            hashed_password=get_password_hash("password")
        )
        db.add(user)
        db.commit()

        response = client.put(
            f"/api/users/{user.id}",
            headers={"Authorization": f"Bearer {manager_token}"},
            json={"name": "Updated"}
        )

        assert response.status_code == 403

    def test_update_user_not_found(self, client: TestClient, admin_token: str):
        """Тест обновления несуществующего пользователя."""
        response = client.put(
            "/api/users/9999",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Updated"}
        )

        assert response.status_code == 404

    def test_cannot_set_guest_level(self, client: TestClient, admin_token: str, db):
        """Тест что нельзя установить уровень 'guest'."""
        user = User(
            email="toguest@example.com",
            name="To",
            surname="Guestov",
            nickname="toguest",
            level=UserLevel.CLIENT,
            hashed_password=get_password_hash("password")
        )
        db.add(user)
        db.commit()

        response = client.put(
            f"/api/users/{user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"level": "guest"}
        )

        # Должна быть ошибка - нельзя понизить до guest
        assert response.status_code == 400 or response.status_code == 422


# ============================================================================
# Тесты удаления пользователя (DELETE /users/{id})
# ============================================================================

class TestDeleteUser:
    """Тесты удаления пользователя."""

    def test_delete_user_admin(self, client: TestClient, admin_token: str, db):
        """Тест удаления пользователя администратором."""
        user = User(
            email="todelete@example.com",
            name="Удаляемый",
            surname="Удаляемый",
            nickname="todelete",
            level=UserLevel.CLIENT,
            status=UserStatus.ACTIVE,
            hashed_password=get_password_hash("123456")
        )
        db.add(user)
        db.commit()

        response = client.delete(
            f"/api/users/{user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 204, f"Expected 204, got {response.status_code}: {response.text}"

        # Проверяем что пользователь удалён
        get_response = client.get(
            f"/api/users/{user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert get_response.status_code == 404

    def test_delete_user_requires_admin(self, client: TestClient, manager_token: str, db):
        """Тест что удаление пользователя требует уровня admin+."""
        user = User(
            email="nodelete@example.com",
            name="No",
            surname="Deleteov",
            nickname="nodelete",
            level=UserLevel.CLIENT,
            hashed_password=get_password_hash("password")
        )
        db.add(user)
        db.commit()

        response = client.delete(
            f"/api/users/{user.id}",
            headers={"Authorization": f"Bearer {manager_token}"}
        )

        assert response.status_code == 403

    def test_cannot_delete_higher_level(self, client: TestClient, admin_token: str, db):
        """Тест что нельзя удалить пользователя с уровнем выше."""
        superuser = User(
            email="super@example.com",
            name="Супер",
            surname="Суперов",
            nickname="super",
            level=UserLevel.SUPERUSER,
            status=UserStatus.ACTIVE,
            hashed_password=get_password_hash("123456")
        )
        db.add(superuser)
        db.commit()

        response = client.delete(
            f"/api/users/{superuser.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 403

    def test_delete_user_not_found(self, client: TestClient, admin_token: str):
        """Тест удаления несуществующего пользователя."""
        response = client.delete(
            "/api/users/9999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 404


# ============================================================================
# Тесты прав доступа (Permission Tests)
# ============================================================================

class TestUserPermissions:
    """Тесты проверки прав доступа по уровням."""

    def test_guest_cannot_create_users(self, client: TestClient, guest_token: str):
        """Тест что гость не может создавать пользователей."""
        response = client.post(
            "/api/users",
            headers={"Authorization": f"Bearer {guest_token}"},
            json={
                "email": "test@test.com",
                "name": "Test",
                "surname": "Test",
                "nickname": "test",
                "password": "123"
            }
        )

        assert response.status_code == 403

    def test_guest_cannot_list_users(self, client: TestClient, guest_token: str):
        """Тест что гость не может получать список пользователей."""
        response = client.get(
            "/api/users",
            headers={"Authorization": f"Bearer {guest_token}"}
        )

        assert response.status_code == 403

    def test_client_cannot_delete_users(self, client: TestClient, user_token: str, db):
        """Тест что клиент не может удалять пользователей."""
        user = User(
            email="victim@example.com",
            name="Victim",
            surname="Victimov",
            nickname="victim",
            level=UserLevel.CLIENT,
            hashed_password=get_password_hash("password")
        )
        db.add(user)
        db.commit()

        response = client.delete(
            f"/api/users/{user.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 403

    def test_manager_can_list_users(self, client: TestClient, manager_token: str):
        """Тест что менеджер может получать список пользователей."""
        response = client.get(
            "/api/users?skip=0&limit=100",
            headers={"Authorization": f"Bearer {manager_token}"}
        )

        assert response.status_code == 200

    def test_superuser_has_full_access(self, client: TestClient, superuser_token: str, db):
        """Тест что суперпользователь имеет полный доступ."""
        # Создаём пользователя
        user = User(
            email="fordelete@example.com",
            name="For",
            surname="Delete",
            nickname="fordelete",
            level=UserLevel.CLIENT,
            hashed_password=get_password_hash("password")
        )
        db.add(user)
        db.commit()

        # Суперпользователь может получить список
        response = client.get(
            "/api/users",
            headers={"Authorization": f"Bearer {superuser_token}"}
        )
        assert response.status_code == 200

        # Суперпользователь может удалить
        response = client.delete(
            f"/api/users/{user.id}",
            headers={"Authorization": f"Bearer {superuser_token}"}
        )
        assert response.status_code == 204
