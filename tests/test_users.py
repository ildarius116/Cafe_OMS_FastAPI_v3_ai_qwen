"""Тесты для API пользователей."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine
from app.models.user import User, UserLevel, UserStatus
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
def admin_token(test_db):
    """Создаёт токен администратора."""
    return create_auth_token(test_db, "admin@example.com", UserLevel.ADMIN)


@pytest.fixture
def manager_token(test_db):
    """Создаёт токен менеджера."""
    return create_auth_token(test_db, "manager@example.com", UserLevel.MANAGER)


class TestUsersCRUD:
    """Тесты CRUD операций для пользователей."""

    def test_get_users_requires_auth(self, client):
        """Тест что список пользователей требует авторизации."""
        response = client.get("/api/users")
        assert response.status_code == 401

    def test_get_users_manager(self, client, manager_token):
        """Тест что менеджер может получить список пользователей."""
        response = client.get(
            "/api/users",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        assert isinstance(response.json(), list)

    def test_create_user_admin(self, client, admin_token):
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

    def test_create_user_requires_admin(self, client, manager_token):
        """Тест что создание пользователя требует администратора."""
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
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"

    def test_update_user_admin(self, client, admin_token, test_db):
        """Тест обновления пользователя администратором."""
        # Создаём пользователя
        user = User(
            email="toupdate@example.com",
            name="Обновляемый",
            surname="Обновляемый",
            nickname="toupdate",
            level=UserLevel.CLIENT,
            status=UserStatus.ACTIVE,
            hashed_password=get_password_hash("123456")
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        response = client.put(
            f"/api/users/{user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Обновлённый"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["name"] == "Обновлённый"

    def test_delete_user_admin(self, client, admin_token, test_db):
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
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        response = client.delete(
            f"/api/users/{user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 204, f"Expected 204, got {response.status_code}: {response.text}"

    def test_cannot_delete_higher_level(self, client, admin_token, test_db):
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
        test_db.add(superuser)
        test_db.commit()
        test_db.refresh(superuser)

        response = client.delete(
            f"/api/users/{superuser.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
