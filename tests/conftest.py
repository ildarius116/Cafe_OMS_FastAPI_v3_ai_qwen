"""
Конфигурация pytest и общие фикстуры для тестов Cafe Orders.

Содержит:
- Базовые фикстуры для базы данных
- Фикстуры аутентификации (токены пользователей)
- Фикстуры тестовых данных (меню, заказы, пользователи)
- Утилиты для генерации уникальных данных
"""

import sys
import os
import uuid
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

# Добавляем корень проекта в path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import get_db, Base, engine, SessionLocal
from app.models.user import User, UserLevel, UserStatus
from app.models.order import Order, OrderStatus, OrderItem
from app.models.menu_item import MenuItem
from app.core.security import get_password_hash, create_access_token

from sqlalchemy.orm import sessionmaker

# ============================================================================
# Конфигурация pytest
# ============================================================================

pytest_plugins = []


# ============================================================================
# Утилиты
# ============================================================================

def unique_email() -> str:
    """Генерирует уникальный email."""
    return f"test_{uuid.uuid4().hex[:8]}@test.com"


def unique_nickname() -> str:
    """Генерирует уникальный nickname."""
    return f"user_{uuid.uuid4().hex[:8]}"


def create_auth_token(db, email: str, level: UserLevel, user_id: int = None) -> str:
    """
    Создаёт JWT токен для пользователя.
    
    Args:
        db: Сессия базы данных
        email: Email пользователя
        level: Уровень доступа
        user_id: ID пользователя (если есть)
    
    Returns:
        JWT токен
    """
    if user_id is None:
        user = db.query(User).filter(User.email == email).first()
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
            db.add(user)
            db.commit()
            db.refresh(user)
        user_id = user.id
    
    return create_access_token(data={"sub": user_id, "level": level.value})


# ============================================================================
# Фикстуры базы данных
# ============================================================================

@pytest.fixture(scope="session")
def db_engine():
    """Создаёт движок базы данных для тестов."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db(db_engine):
    """
    Создаёт тестовую сессию базы данных для каждого теста.
    
    Фикстура автоматически очищает БД после каждого теста.
    """
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    db_session = TestingSessionLocal()
    
    try:
        yield db_session
    finally:
        db_session.close()
        # Очищаем все таблицы после теста
        Base.metadata.drop_all(bind=db_engine)
        Base.metadata.create_all(bind=db_engine)


@pytest.fixture
def client(db):
    """
    Создаёт тестовый клиент FastAPI с переопределением зависимости БД.
    
    Usage:
        def test_example(client):
            response = client.get("/api/orders")
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# ============================================================================
# Фикстуры аутентификации
# ============================================================================

@pytest.fixture
def guest_token(db) -> str:
    """Токен гостя (minimal права)."""
    return create_auth_token(db, unique_email(), UserLevel.GUEST)


@pytest.fixture
def user_token(db) -> str:
    """Токен обычного пользователя (client level)."""
    return create_auth_token(db, unique_email(), UserLevel.CLIENT)


@pytest.fixture
def staff_token(db) -> str:
    """Токен сотрудника (staff level)."""
    return create_auth_token(db, unique_email(), UserLevel.STAFF)


@pytest.fixture
def manager_token(db) -> str:
    """Токен менеджера (manager level)."""
    return create_auth_token(db, unique_email(), UserLevel.MANAGER)


@pytest.fixture
def admin_token(db) -> str:
    """Токен администратора (admin level)."""
    return create_auth_token(db, unique_email(), UserLevel.ADMIN)


@pytest.fixture
def director_token(db) -> str:
    """Токен руководителя (director level)."""
    return create_auth_token(db, unique_email(), UserLevel.DIRECTOR)


@pytest.fixture
def superuser_token(db) -> str:
    """Токен суперпользователя (superuser level)."""
    return create_auth_token(db, unique_email(), UserLevel.SUPERUSER)


# ============================================================================
# Фикстуры тестовых данных - Menu Items
# ============================================================================

@pytest.fixture
def menu_item_burger(db) -> MenuItem:
    """Создаёт тестовое блюдо 'Бургер'."""
    item = MenuItem(
        name="Бургер",
        description="Сочный бургер с говядиной",
        price=350.0,
        category="Горячее",
        is_available=True
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@pytest.fixture
def menu_item_fries(db) -> MenuItem:
    """Создаёт тестовое блюдо 'Картофель фри'."""
    item = MenuItem(
        name="Картофель фри",
        description="Хрустящий картофель во фритюре",
        price=150.0,
        category="Закуски",
        is_available=True
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@pytest.fixture
def menu_item_pizza(db) -> MenuItem:
    """Создаёт тестовое блюдо 'Пицца Маргарита'."""
    item = MenuItem(
        name="Пицца Маргарита",
        description="Классическая пицца с томатами и моцареллой",
        price=800.0,
        category="Горячее",
        is_available=True
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@pytest.fixture
def menu_item_cola(db) -> MenuItem:
    """Создаёт тестовое блюдо 'Кола'."""
    item = MenuItem(
        name="Кола",
        description="Газированный напиток",
        price=200.0,
        category="Напитки",
        is_available=True
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@pytest.fixture
def menu_items(db) -> dict[str, MenuItem]:
    """
    Создаёт набор тестовых элементов меню.
    
    Returns:
        dict с ключами по названиям блюд
    """
    items_data = [
        {"name": "Бургер", "description": "Сочный бургер с говядиной", "price": 350.0, "category": "Горячее"},
        {"name": "Картофель фри", "description": "Хрустящий картофель во фритюре", "price": 150.0, "category": "Закуски"},
        {"name": "Пицца Маргарита", "description": "Классическая пицца с томатами и моцареллой", "price": 800.0, "category": "Горячее"},
        {"name": "Кола", "description": "Газированный напиток", "price": 200.0, "category": "Напитки"},
        {"name": "Стейк рибай", "description": "Стейк из мраморной говядины", "price": 1500.0, "category": "Горячее"},
        {"name": "Салат Цезарь", "description": "Классический салат с курицей", "price": 350.0, "category": "Салаты"},
        {"name": "Кофе американо", "description": "Чёрный кофе", "price": 150.0, "category": "Напитки"},
        {"name": "Чизкейк", "description": "Нежный творожный десерт", "price": 220.0, "category": "Десерты"},
    ]
    
    items = {}
    for item_data in items_data:
        item = MenuItem(**item_data, is_available=True)
        db.add(item)
        items[item.name] = item
    
    db.commit()
    
    for item in items.values():
        db.refresh(item)
    
    return items


# ============================================================================
# Фикстуры тестовых данных - Заказы
# ============================================================================

@pytest.fixture
def order_pending(db, user_token, menu_items) -> Order:
    """Создаёт заказ в статусе 'pending'."""
    # Получаем user_id из токена
    user = db.query(User).filter(User.email.startswith("test_")).first()
    if not user:
        user = User(
            email=unique_email(),
            name="Test",
            surname="User",
            nickname="testuser",
            level=UserLevel.CLIENT,
            status=UserStatus.ACTIVE,
            hashed_password=get_password_hash("password")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    burger = menu_items["Бургер"]
    fries = menu_items["Картофель фри"]
    
    order = Order(
        table_number=5,
        user_id=user.id,
        status=OrderStatus.PENDING,
        total_price=0
    )
    db.add(order)
    db.flush()
    
    order_item1 = OrderItem(order_id=order.id, menu_item_id=burger.id, quantity=2, price=burger.price)
    order_item2 = OrderItem(order_id=order.id, menu_item_id=fries.id, quantity=1, price=fries.price)
    db.add_all([order_item1, order_item2])
    
    db.flush()
    order.total_price = order.calculate_total()  # 350*2 + 150 = 850
    db.commit()
    db.refresh(order)
    
    return order


@pytest.fixture
def order_ready(db, user_token, menu_items) -> Order:
    """Создаёт заказ в статусе 'ready'."""
    user = db.query(User).filter(User.email.startswith("test_")).first()
    if not user:
        user = User(
            email=unique_email(),
            name="Test",
            surname="User",
            nickname="testuser",
            level=UserLevel.CLIENT,
            status=UserStatus.ACTIVE,
            hashed_password=get_password_hash("password")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    pizza = menu_items["Пицца Маргарита"]
    cola = menu_items["Кола"]
    
    order = Order(
        table_number=3,
        user_id=user.id,
        status=OrderStatus.READY,
        total_price=0
    )
    db.add(order)
    db.flush()
    
    order_item1 = OrderItem(order_id=order.id, menu_item_id=pizza.id, quantity=1, price=pizza.price)
    order_item2 = OrderItem(order_id=order.id, menu_item_id=cola.id, quantity=2, price=cola.price)
    db.add_all([order_item1, order_item2])
    
    db.flush()
    order.total_price = order.calculate_total()  # 800 + 200*2 = 1200
    db.commit()
    db.refresh(order)
    
    return order


@pytest.fixture
def order_paid(db, user_token, menu_items) -> Order:
    """Создаёт заказ в статусе 'paid'."""
    user = db.query(User).filter(User.email.startswith("test_")).first()
    if not user:
        user = User(
            email=unique_email(),
            name="Test",
            surname="User",
            nickname="testuser",
            level=UserLevel.CLIENT,
            status=UserStatus.ACTIVE,
            hashed_password=get_password_hash("password")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    steak = menu_items["Стейк рибай"]
    
    order = Order(
        table_number=7,
        user_id=user.id,
        status=OrderStatus.PAID,
        total_price=0
    )
    db.add(order)
    db.flush()
    
    order_item = OrderItem(order_id=order.id, menu_item_id=steak.id, quantity=1, price=steak.price)
    db.add(order_item)
    
    db.flush()
    order.total_price = order.calculate_total()  # 1500
    db.commit()
    db.refresh(order)
    
    return order


@pytest.fixture
def orders_set(db, user_token, menu_items) -> list[Order]:
    """
    Создаёт набор заказов для комплексных тестов.
    
    Создаёт 3 заказа:
    - Стол 5: pending, Бургер x2 + Фри x1 = 850
    - Стол 3: ready, Пицца x1 + Кола x2 = 1200
    - Стол 7: paid, Стейк x1 = 1500
    """
    user = db.query(User).filter(User.email.startswith("test_")).first()
    if not user:
        user = User(
            email=unique_email(),
            name="Test",
            surname="User",
            nickname="testuser",
            level=UserLevel.CLIENT,
            status=UserStatus.ACTIVE,
            hashed_password=get_password_hash("password")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    orders_data = [
        {
            "table_number": 5,
            "status": OrderStatus.PENDING,
            "items": [("Бургер", 2), ("Картофель фри", 1)]
        },
        {
            "table_number": 3,
            "status": OrderStatus.READY,
            "items": [("Пицца Маргарита", 1), ("Кола", 2)]
        },
        {
            "table_number": 7,
            "status": OrderStatus.PAID,
            "items": [("Стейк рибай", 1)]
        }
    ]
    
    orders = []
    for data in orders_data:
        order = Order(
            table_number=data["table_number"],
            user_id=user.id,
            status=data["status"],
            total_price=0
        )
        db.add(order)
        db.flush()
        
        for item_name, qty in data["items"]:
            menu_item = menu_items[item_name]
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=menu_item.id,
                quantity=qty,
                price=menu_item.price
            )
            db.add(order_item)
        
        db.flush()
        order.total_price = order.calculate_total()
        orders.append(order)
    
    db.commit()
    
    for order in orders:
        db.refresh(order)
    
    return orders


# ============================================================================
# Фикстуры Playwright (Web UI тесты)
# ============================================================================

WEB_BASE_URL = os.getenv("WEB_BASE_URL", "http://localhost:5173")


@pytest.fixture(scope="session")
def browser() -> Browser:
    """
    Создаёт браузер для всех тестов.
    
    Usage:
        def test_example(browser):
            page = browser.new_page()
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def context(browser: Browser) -> BrowserContext:
    """
    Создаёт новый контекст браузера для каждого теста.
    
    Каждый тест получает чистый контекст без cookies/localStorage.
    """
    context = browser.new_context()
    context.set_default_timeout(30000)
    yield context
    context.close()


@pytest.fixture
def page(context: BrowserContext) -> Page:
    """
    Создаёт новую страницу для каждого теста.
    
    Usage:
        def test_login(page):
            page.goto("http://localhost:5173/login")
    """
    page = context.new_page()
    page.set_default_timeout(30000)
    return page


# ============================================================================
# Утилиты для Web UI тестов
# ============================================================================

def register_via_ui(page: Page, email: str = None, nickname: str = None, 
                    name: str = "Test", surname: str = "User", 
                    password: str = "test123") -> str:
    """
    Регистрирует пользователя через веб-интерфейс.
    
    Args:
        page: Страница Playwright
        email: Email (генерируется если не указан)
        nickname: Никнейм (генерируется если не указан)
        name: Имя
        surname: Фамилия
        password: Пароль
    
    Returns:
        JWT токен после регистрации
    """
    if email is None:
        email = unique_email()
    if nickname is None:
        nickname = unique_nickname()
    
    # Переходим на страницу логина
    page.goto(f"{WEB_BASE_URL}/login")
    page.wait_for_load_state("networkidle")
    
    # Очищаем localStorage
    page.evaluate("localStorage.clear()")
    
    # Переключаемся на регистрацию
    register_button = page.locator('button:has-text("Регистрация")').first
    register_button.wait_for(state="visible", timeout=5000)
    register_button.click()
    
    # Заполняем форму
    page.fill('input[name="nickname"]', nickname)
    page.fill('input[name="name"]', name)
    page.fill('input[name="surname"]', surname)
    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', password)
    
    # Отправляем форму
    submit_button = page.locator('button[type="submit"]')
    submit_button.wait_for(state="visible", timeout=5000)
    submit_button.click()
    page.wait_for_load_state("networkidle")
    
    # Проверяем токен
    token = page.evaluate("localStorage.getItem('token')")
    assert token is not None, "Регистрация не удалась - токен не найден"
    
    return token


def login_via_ui(page: Page, email: str, password: str) -> str:
    """
    Выполняет вход через веб-интерфейс.
    
    Args:
        page: Страница Playwright
        email: Email
        password: Пароль
    
    Returns:
        JWT токен после входа
    """
    page.goto(f"{WEB_BASE_URL}/login")
    page.wait_for_load_state("networkidle")
    
    # Заполняем форму
    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', password)
    
    # Отправляем форму
    submit_button = page.locator('button[type="submit"]')
    submit_button.wait_for(state="visible", timeout=5000)
    submit_button.click()
    page.wait_for_load_state("networkidle")
    
    # Проверяем токен
    token = page.evaluate("localStorage.getItem('token')")
    assert token is not None, "Вход не удался - токен не найден"
    
    return token


def logout_via_ui(page: Page):
    """Выполняет выход через веб-интерфейс."""
    # Находим кнопку выхода
    logout_button = page.locator('button[title="Выйти"]')
    if logout_button.count() == 0:
        logout_button = page.locator('button:has-text("Выйти")')
    
    if logout_button.count() > 0:
        logout_button.first.click()
        page.wait_for_load_state("networkidle")
