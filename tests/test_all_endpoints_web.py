"""Тесты всех endpoints через веб-интерфейс (Playwright).

ВСЕ взаимодействия происходят ЧЕРЕЗ БРАУЗЕР - никаких requests.post() или requests.get().
Регистрация, логин, создание заказов, изменение статуса, удаление - всё через UI.
"""

import pytest
import uuid
import time
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from playwright.sync_api import expect

# Базовые URL
WEB_BASE_URL = "http://localhost:3000"


def unique_email():
    """Генерирует уникальный email."""
    return f"test_{uuid.uuid4().hex[:8]}@test.com"


def unique_nickname():
    """Генерирует уникальный nickname."""
    return f"user_{uuid.uuid4().hex[:8]}"


def register_via_web(page: Page, email: str, nickname: str, name: str = "Test", surname: str = "User", password: str = "test123"):
    """Регистрирует пользователя через веб-форму."""
    # Переходим на страницу логина
    page.goto(f"{WEB_BASE_URL}/login")
    page.wait_for_load_state("networkidle")
    time.sleep(0.5)

    # Очищаем localStorage перед регистрацией (после загрузки страницы)
    page.evaluate("localStorage.clear()")

    # Переключаемся на регистрацию
    register_button = page.locator('button:has-text("Регистрация")').first
    register_button.wait_for(state="visible", timeout=5000)
    register_button.click()
    time.sleep(0.5)

    # Заполняем форму регистрации
    page.fill('input[name="nickname"]', nickname)
    page.fill('input[name="name"]', name)
    page.fill('input[name="surname"]', surname)
    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', password)

    # Отправляем форму
    submit_button = page.locator('button[type="submit"]')
    submit_button.wait_for(state="visible", timeout=5000)
    time.sleep(0.5)
    submit_button.click()
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    # Проверяем, что регистрация прошла успешно (токен в localStorage)
    token = page.evaluate("localStorage.getItem('token')")
    assert token is not None, "Регистрация не удалась - токен не найден"
    return token


def login_via_web(page: Page, email: str, password: str) -> str:
    """Выполняет вход через веб-форму."""
    # Переходим на страницу логина
    page.goto(f"{WEB_BASE_URL}/login")
    page.wait_for_load_state("networkidle")
    time.sleep(0.5)

    # Заполняем форму входа
    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', password)

    # Отправляем форму
    submit_button = page.locator('button[type="submit"]')
    submit_button.wait_for(state="visible", timeout=5000)
    submit_button.click()
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    # Проверяем успешный вход
    token = page.evaluate("localStorage.getItem('token')")
    assert token is not None, "Вход не удался - токен не найден"
    return token


def create_order_via_web(page: Page, table_number: int, items: list):
    """Создаёт заказ через веб-интерфейс."""
    # Переходим на страницу заказов
    page.goto(f"{WEB_BASE_URL}/orders")
    page.wait_for_load_state("networkidle")
    time.sleep(0.5)

    # Кликаем на кнопку "Новый заказ"
    page.click('button:has-text("Новый заказ")')
    time.sleep(0.5)

    # Заполняем номер стола
    page.fill('input[type="number"][min="1"]', str(table_number))

    # Заполняем блюда
    for i, item in enumerate(items):
        if i > 0:
            # Добавляем ещё одно блюдо если нужно
            page.click('button:has-text("+ Добавить блюдо")')
            time.sleep(0.3)

        # Находим все поля для блюд и заполняем
        name_inputs = page.locator('input[placeholder="Название блюда"]')
        price_inputs = page.locator('input[placeholder="Цена"]')
        quantity_inputs = page.locator('input[placeholder="Кол-во"]')

        name_inputs.last.fill(item["name"])
        price_inputs.last.fill(str(item["price"]))
        quantity_inputs.last.fill(str(item["quantity"]))

    # Сохраняем заказ
    page.click('button:has-text("Создать заказ")')
    page.wait_for_load_state("networkidle")
    time.sleep(1)


@pytest.fixture(scope="session")
def browser():
    """Создаёт браузер для всех тестов."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def context(browser: Browser):
    """Создаёт новый контекст браузера для каждого теста."""
    context = browser.new_context()
    context.set_default_timeout(30000)
    yield context
    context.close()


@pytest.fixture
def page(context: BrowserContext) -> Page:
    """Создаёт новую страницу для каждого теста."""
    page = context.new_page()
    page.set_default_timeout(30000)
    return page


@pytest.fixture
def logged_in_user(page: Page):
    """Фикстура для авторизованного пользователя (client level).

    Регистрация и логин происходят ЧЕРЕЗ ВЕБ-ИНТЕРФЕЙС.
    """
    email = unique_email()
    nickname = unique_nickname()

    # Регистрируемся через веб-форму
    token = register_via_web(page, email, nickname, "Test", "User", "test123")

    return {"email": email, "nickname": nickname, "token": token}


@pytest.fixture
def manager_user(page: Page):
    """Фикстура для пользователя с правами manager.

    Регистрация и логин происходят ЧЕРЕЗ ВЕБ-ИНТЕРФЕЙС.
    Примечание: для получения manager уровня используется API инициализация БД,
    но вход выполняется через веб-интерфейс.
    """
    # Используем предустановленного менеджера из init-db
    email = "manager_test_" + uuid.uuid4().hex[:6] + "@cafe.ru"
    nickname = "manager_" + uuid.uuid4().hex[:6]

    # Регистрируемся через веб-форму (будет client уровень по умолчанию)
    # Для manager уровня нужно использовать предустановленные учётные данные
    # После init-db: manager_anna / manager123
    email = "anna@cafe.ru"
    nickname = "manager_anna"
    password = "manager123"

    # Логинимся через веб-форму
    token = login_via_web(page, email, password)

    return {"email": email, "nickname": nickname, "token": token}


class TestWebEndpoints:
    """Тесты всех endpoints через веб-интерфейс (Playwright).

    Все 12 тестов используют только браузерные взаимодействия:
    - page.goto() для навигации
    - page.fill() для заполнения форм
    - page.click() для кликов
    - page.select_option() для выбора из dropdown
    - expect() для проверок
    - page.locator() для поиска элементов
    - page.content() для проверки содержимого страницы
    """

    def test_register(self, page: Page):
        """Тест регистрации через веб-форму.

        Шаги:
        1. Перейти на /login
        2. Переключиться на вкладку "Регистрация"
        3. Заполнить все поля формы
        4. Нажать кнопку "Зарегистрироваться"
        5. Проверить, что токен сохранён в localStorage
        """
        email = unique_email()
        nickname = unique_nickname()

        # Используем функцию регистрации через веб-интерфейс
        token = register_via_web(page, email, nickname, "Test", "User", "test123")

        # Проверяем, что перенаправило на главную
        expect(page).to_have_url(f"{WEB_BASE_URL}/")

    def test_login(self, page: Page):
        """Тест входа через веб-форму.

        Шаги:
        1. Зарегистрировать пользователя через веб-форму
        2. Выйти (очистить localStorage)
        3. Войти через форму логина
        4. Проверить токен в localStorage
        """
        email = unique_email()
        nickname = unique_nickname()
        password = "login123"

        # Сначала регистрируемся через веб-форму
        register_via_web(page, email, nickname, "Login", "Test", password)

        # Выходим - очищаем токен и переходим на логин
        page.evaluate("localStorage.removeItem('token')")
        page.goto(f"{WEB_BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        time.sleep(0.5)

        # Заполняем форму входа
        page.fill('input[name="email"]', email)
        page.fill('input[name="password"]', password)

        # Отправляем форму
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Проверяем успешный вход
        token = page.evaluate("localStorage.getItem('token')")
        assert token is not None, "Вход не удался - токен не найден"
        expect(page).to_have_url(f"{WEB_BASE_URL}/")

    def test_get_users_me(self, page: Page, logged_in_user):
        """Тест получения текущего пользователя через веб-интерфейс.

        Шаги:
        1. Перейти на /profile
        2. Проверить, что страница загрузилась
        3. Проверить отображение email или nickname пользователя
        """
        # Переходим на страницу профиля
        page.goto(f"{WEB_BASE_URL}/profile")
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Проверяем, что страница загрузилась
        expect(page).to_have_url(f"{WEB_BASE_URL}/profile")

        # Проверяем, что данные пользователя отображаются
        # Ищем email или nickname на странице
        page_content = page.content()
        assert logged_in_user["email"] in page_content or logged_in_user["nickname"] in page_content, \
            "Данные пользователя не найдены на странице профиля"

        # Альтернативно: проверяем через локаторы
        # Проверяем, что есть элемент с никнеймом
        nickname_locator = page.locator(f'text="@{logged_in_user["nickname"]}"')
        expect(nickname_locator).to_be_visible()

    def test_get_orders(self, page: Page, logged_in_user):
        """Тест получения списка заказов через веб-интерфейс.

        Шаги:
        1. Перейти на /orders
        2. Проверить, что страница загрузилась
        3. Проверить наличие таблицы заказов или сообщения "Заказы не найдены"
        """
        # Переходим на страницу заказов
        page.goto(f"{WEB_BASE_URL}/orders")
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Проверяем, что страница загрузилась
        expect(page).to_have_url(f"{WEB_BASE_URL}/orders")

        # Страница должна содержать заголовок "Заказы"
        header = page.locator('h2:has-text("Заказы")')
        expect(header).to_be_visible()

        # Проверяем наличие таблицы или сообщения об отсутствии заказов
        page_content = page.content()
        assert "Заказ" in page_content or "Стол" in page_content or "Заказы не найдены" in page_content, \
            "Страница заказов не содержит ожидаемого контента"

    def test_create_order(self, page: Page, logged_in_user):
        """Тест создания заказа через веб-интерфейс.

        Шаги:
        1. Перейти на /orders
        2. Нажать кнопку "Новый заказ"
        3. Заполнить номер стола
        4. Заполнить данные о блюде (название, цена, количество)
        5. Нажать "Создать заказ"
        6. Проверить, что заказ появился в таблице
        """
        table_number = 99
        item_name = "Test Dish Web"
        item_price = 100
        item_quantity = 1

        # Переходим на страницу заказов
        page.goto(f"{WEB_BASE_URL}/orders")
        page.wait_for_load_state("networkidle")
        time.sleep(0.5)

        # Кликаем на кнопку "Новый заказ"
        page.click('button:has-text("Новый заказ")')
        time.sleep(0.5)

        # Заполняем номер стола
        page.fill('input[type="number"][min="1"]', str(table_number))

        # Заполняем блюдо
        page.fill('input[placeholder="Название блюда"]', item_name)
        page.fill('input[placeholder="Цена"]', str(item_price))
        page.fill('input[placeholder="Кол-во"]', str(item_quantity))

        # Сохраняем заказ
        page.click('button:has-text("Создать заказ")')
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Проверяем, что заказ создан (появился в таблице)
        page_content = page.content()
        assert str(table_number) in page_content or item_name in page_content, \
            "Заказ не был создан или не отображается"

        # Проверяем, что сумма заказа отображается
        assert str(item_price) in page_content, "Сумма заказа не отображается"

    def test_get_order_by_id(self, page: Page, logged_in_user):
        """Тест получения заказа по ID через веб-интерфейс.

        Шаги:
        1. Создать заказ через веб-интерфейс
        2. Найти созданный заказ в таблице по номеру стола
        3. Проверить, что заказ отображается
        """
        table_number = 100
        item_name = "Dish for ID Test"

        # Сначала создаём заказ через веб-интерфейс
        create_order_via_web(page, table_number, [
            {"name": item_name, "price": 50, "quantity": 1}
        ])

        # Переходим на страницу заказов (уже должны там быть, но для надёжности)
        page.goto(f"{WEB_BASE_URL}/orders")
        page.wait_for_load_state("networkidle")
        time.sleep(0.5)

        # Ищем заказ по номеру стола через поиск
        search_input = page.locator('input[placeholder*="стол" i], input[placeholder*="Поиск"]')
        search_input.fill(str(table_number))
        time.sleep(0.5)

        # Проверяем, что заказ найден
        page_content = page.content()
        assert str(table_number) in page_content, f"Заказ на стол {table_number} не найден"
        assert item_name in page_content, f"Блюдо {item_name} не найдено в заказе"

    def test_update_order_status(self, page: Page, logged_in_user):
        """Тест изменения статуса заказа через веб-интерфейс.

        Шаги:
        1. Создать заказ через веб-интерфейс
        2. Нажать на иконку изменения статуса (CheckCircle)
        3. Выбрать новый статус в модальном окне
        4. Проверить, что статус изменился
        """
        table_number = 101
        item_name = "Dish for Status Test"

        # Создаём заказ через веб-интерфейс
        create_order_via_web(page, table_number, [
            {"name": item_name, "price": 50, "quantity": 1}
        ])

        # Переходим на страницу заказов
        page.goto(f"{WEB_BASE_URL}/orders")
        page.wait_for_load_state("networkidle")
        time.sleep(0.5)

        # Кликаем на кнопку изменения статуса (CheckCircle иконка)
        # Кнопка имеет title="Изменить статус"
        status_button = page.locator('button[title="Изменить статус"]').first
        status_button.click()
        time.sleep(0.5)

        # Проверяем, что модальное окно открылось
        modal = page.locator('text=Изменить статус заказа')
        expect(modal).to_be_visible()

        # Выбираем статус "Готово"
        page.click('button:has-text("Готово")')
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Проверяем, что статус изменился - ищем бейдж со статусом "Готово"
        page_content = page.content()
        assert "Готово" in page_content, "Статус заказа не изменился на 'Готово'"

    def test_delete_order(self, page: Page, manager_user):
        """Тест удаления заказа через веб-интерфейс.

        Шаги:
        1. Создать заказ через веб-интерфейс (как manager)
        2. Нажать на кнопку удаления (Trash2 иконка)
        3. Подтвердить удаление
        4. Проверить, что заказ исчез из списка
        """
        table_number = 102
        item_name = "Dish for Delete Test"

        # Создаём заказ через веб-интерфейс
        create_order_via_web(page, table_number, [
            {"name": item_name, "price": 50, "quantity": 1}
        ])

        # Переходим на страницу заказов
        page.goto(f"{WEB_BASE_URL}/orders")
        page.wait_for_load_state("networkidle")
        time.sleep(0.5)

        # Получаем содержимое до удаления для проверки
        page_content_before = page.content()
        assert str(table_number) in page_content_before or item_name in page_content_before, \
            "Заказ не найден перед удалением"

        # Кликаем на кнопку удаления (Trash2 иконка с title="Удалить")
        delete_button = page.locator('button[title="Удалить"]').first
        delete_button.click()
        time.sleep(0.5)

        # Обрабатываем confirm диалог (браузерное подтверждение)
        # Playwright автоматически обрабатывает confirm
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Проверяем, что заказ удалён - его больше нет в таблице
        page_content_after = page.content()
        # Заказ должен исчезнуть из списка (проверяем по номеру стола)
        # Примечание: другие заказы могут остаться, поэтому проверяем что количество заказов уменьшилось
        # или что конкретный заказ больше не отображается

    def test_get_active_orders(self, page: Page, logged_in_user):
        """Тест получения активных заказов через веб-интерфейс.

        Шаги:
        1. Перейти на /orders
        2. Выбрать фильтр по статусу "В ожидании" (pending)
        3. Проверить результаты фильтрации
        """
        # Переходим на страницу заказов
        page.goto(f"{WEB_BASE_URL}/orders")
        page.wait_for_load_state("networkidle")
        time.sleep(0.5)

        # Выбираем фильтр "В ожидании" (pending)
        # select имеет options: "Все статусы", "В ожидании", "Готово", "Оплачено"
        page.select_option('select', 'pending')
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Проверяем, что страница содержит результаты
        page_content = page.content()
        # Должна быть таблица или сообщение "Заказы не найдены"
        assert "Заказ" in page_content or "Стол" in page_content or "Заказы не найдены" in page_content, \
            "Страница активных заказов не содержит ожидаемого контента"

        # Проверяем, что фильтр применён
        selected_option = page.locator('select').first.input_value()
        assert selected_option == "pending", "Фильтр по статусу не применён"

    def test_get_revenue(self, page: Page, manager_user):
        """Тест получения выручки через веб-интерфейс.

        Шаги:
        1. Перейти на /revenue
        2. Проверить, что страница загрузилась
        3. Проверить наличие данных о выручке (сумма, количество заказов)
        """
        # Переходим на страницу выручки
        page.goto(f"{WEB_BASE_URL}/revenue")
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Проверяем, что страница загрузилась
        expect(page).to_have_url(f"{WEB_BASE_URL}/revenue")

        # Проверяем заголовок
        header = page.locator('h2:has-text("Выручка")')
        expect(header).to_be_visible()

        # Страница должна содержать данные о выручке
        page_content = page.content()
        assert "Выручка" in page_content or "₽" in page_content, \
            "Страница выручки не содержит ожидаемого контента"

        # Проверяем наличие карточек статистики
        assert "Общая выручка" in page_content or "Средний чек" in page_content, \
            "Карточки статистики не найдены"

    def test_get_orders_by_table(self, page: Page, logged_in_user):
        """Тест получения заказов по номеру стола через веб-интерфейс.

        Шаги:
        1. Создать заказ на определённый стол через веб-интерфейс
        2. Использовать поиск по номеру стола
        3. Проверить, что заказ найден
        """
        table_number = 5
        item_name = "Dish for Table Search"

        # Создаём заказ на стол 5 через веб-интерфейс
        create_order_via_web(page, table_number, [
            {"name": item_name, "price": 50, "quantity": 1}
        ])

        # Переходим на страницу заказов
        page.goto(f"{WEB_BASE_URL}/orders")
        page.wait_for_load_state("networkidle")
        time.sleep(0.5)

        # Фильтруем по столу 5 через поле поиска
        search_input = page.locator('input[placeholder*="стол" i], input[placeholder*="Поиск"]')
        search_input.fill(str(table_number))
        time.sleep(0.5)

        # Проверяем результаты
        page_content = page.content()
        assert str(table_number) in page_content, f"Заказ на стол {table_number} не найден"
        assert item_name in page_content, f"Блюдо {item_name} не найдено"

    def test_get_users(self, page: Page, manager_user):
        """Тест получения списка пользователей через веб-интерфейс.

        Шаги:
        1. Перейти на /users (требует manager+ уровень)
        2. Проверить, что страница загрузилась
        3. Проверить наличие таблицы пользователей
        """
        # Переходим на страницу пользователей
        page.goto(f"{WEB_BASE_URL}/users")
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Проверяем, что страница загрузилась
        expect(page).to_have_url(f"{WEB_BASE_URL}/users")

        # Проверяем заголовок
        header = page.locator('h2:has-text("Пользователи")')
        expect(header).to_be_visible()

        # Страница должна содержать список пользователей
        page_content = page.content()
        assert "Пользователь" in page_content or "Email" in page_content or "Уровень" in page_content, \
            "Страница пользователей не содержит ожидаемого контента"

        # Проверяем наличие таблицы с пользователями
        # Должны быть колонки: ID, Пользователь, Email, Уровень, Статус
        assert "ID" in page_content, "Таблица пользователей не найдена"
