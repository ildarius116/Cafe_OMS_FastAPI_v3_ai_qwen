"""Тесты для API аутентификации."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine
from app.models.user import User
from app.core.security import get_password_hash
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


class TestAuthRegister:
    """Тесты регистрации пользователя."""

    def test_register_success(self, client):
        """Тест успешной регистрации."""
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "name": "Тест",
            "surname": "Тестов",
            "nickname": "testuser",
            "password": "123456"
        })
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["nickname"] == "testuser"
        assert data["level"] == "client"

    def test_register_duplicate_email(self, client, test_db):
        """Тест регистрации с дублирующимся email."""
        # Создаём пользователя
        user = User(
            email="dup@example.com",
            name="Тест",
            surname="Тестов",
            nickname="test1",
            hashed_password=get_password_hash("123456")
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Пытаемся зарегистрироваться снова
        response = client.post("/api/auth/register", json={
            "email": "dup@example.com",
            "name": "Тест2",
            "surname": "Тестов2",
            "nickname": "test2",
            "password": "123456"
        })
        assert response.status_code == 409

    def test_register_duplicate_nickname(self, client, test_db):
        """Тест регистрации с дублирующимся никнеймом."""
        user = User(
            email="unique@example.com",
            name="Тест",
            surname="Тестов",
            nickname="dupnick",
            hashed_password=get_password_hash("123456")
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        response = client.post("/api/auth/register", json={
            "email": "unique2@example.com",
            "name": "Тест2",
            "surname": "Тестов2",
            "nickname": "dupnick",
            "password": "123456"
        })
        assert response.status_code == 409

    def test_register_invalid_email(self, client):
        """Тест регистрации с невалидным email."""
        response = client.post("/api/auth/register", json={
            "email": "invalid-email",
            "name": "Тест",
            "surname": "Тестов",
            "nickname": "testuser",
            "password": "123456"
        })
        assert response.status_code == 422

    def test_register_short_password(self, client):
        """Тест регистрации с коротким паролем."""
        response = client.post("/api/auth/register", json={
            "email": "test2@example.com",
            "name": "Тест",
            "surname": "Тестов",
            "nickname": "testuser2",
            "password": "123"
        })
        assert response.status_code == 422


class TestAuthLogin:
    """Тесты аутентификации."""

    def test_login_success(self, client, test_db):
        """Тест успешного входа."""
        # Создаём пользователя
        user = User(
            email="login@example.com",
            name="Тест",
            surname="Тестов",
            nickname="loginuser",
            hashed_password=get_password_hash("123456")
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Входим
        response = client.post("/api/auth/login", data={
            "username": "login@example.com",
            "password": "123456"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_db):
        """Тест входа с неправильным паролем."""
        user = User(
            email="login2@example.com",
            name="Тест",
            surname="Тестов",
            nickname="loginuser2",
            hashed_password=get_password_hash("123456")
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        response = client.post("/api/auth/login", data={
            "username": "login2@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Тест входа с несуществующим пользователем."""
        response = client.post("/api/auth/login", data={
            "username": "nonexistent@example.com",
            "password": "123456"
        })
        assert response.status_code == 401
