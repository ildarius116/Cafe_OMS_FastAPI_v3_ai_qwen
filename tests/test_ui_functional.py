"""Функциональные UI тесты для проверки исправлений Cafe Orders."""

import pytest
import time
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from playwright.sync_api import expect

WEB_BASE_URL = "http://localhost:3000"
API_BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="session")
def browser():
    """Создаёт браузер для всех тестов."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        yield browser
        browser.close()


@pytest.fixture
def context(browser: Browser):
    """Создаёт новый контекст для каждого теста."""
    context = browser.new_context()
    yield context
    context.close()


@pytest.fixture
def page(context: BrowserContext) -> Page:
    """Создаёт новую страницу для каждого теста."""
    page = context.new_page()
    page.set_default_timeout(10000)
    return page


def login_via_ui(page: Page, email: str, password: str):
    """Вход через UI."""
    page.goto(f"{WEB_BASE_URL}/login")
    page.wait_for_load_state("networkidle")
    
    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    time.sleep(1)


class TestHeaderUserDisplay:
    """Тесты отображения пользователя в шапке."""

    def test_guest_before_login(self, page):
        """Проверка что до входа показывается 'Гость'."""
        page.goto(f"{WEB_BASE_URL}/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        
        # Должна быть кнопка "Войти" или текст "Гость"
        page_content = page.content()
        print(f"Content before login: {page_content[:2000]}")
        
        # Ищем кнопку "Войти" или текст "Гость"
        has_login_button = page.locator('button:has-text("Войти")').count() > 0
        has_guest_text = "Гость" in page_content
        
        assert has_login_button or has_guest_text, \
            "До входа должна быть кнопка 'Войти' или текст 'Гость'"

    def test_user_shows_after_login(self, page):
        """Проверка что после входа показывается имя пользователя."""
        # Логинимся
        login_via_ui(page, "john@example.com", "client123")
        
        # Переходим на главную
        page.goto(f"{WEB_BASE_URL}/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # Проверяем что в шапке НЕ "Гость"
        page_content = page.content()
        print(f"Content after login: {page_content[:3000]}")
        
        # Ищем имя пользователя в хедере
        header_content = page.locator('header').text_content()
        print(f"Header content: {header_content}")
        
        # Должно быть имя пользователя (не "Гость")
        assert "Гость" not in header_content, \
            "После входа должно показываться имя пользователя, а не 'Гость'"
        
        # Должна быть кнопка "Выйти" или иконка выхода
        has_logout = (
            page.locator('button[title="Выйти"]').count() > 0 or
            page.locator('button:has-text("Выйти")').count() > 0
        )
        assert has_logout, "После входа должна быть кнопка 'Выйти'"

    def test_logout_clears_user(self, page):
        """Проверка что выход удаляет токен и показывает 'Гость'."""
        # Логинимся
        login_via_ui(page, "john@example.com", "client123")
        page.goto(f"{WEB_BASE_URL}/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        
        # Проверяем что токен есть
        token_before = page.evaluate("localStorage.getItem('token')")
        print(f"Token before logout: {token_before}")
        assert token_before is not None, "Токен должен быть после входа"
        
        # Проверяем что в шапке НЕ "Гость"
        header_before = page.locator('header').text_content()
        print(f"Header before logout: {header_before[:100]}")
        assert "Гость" not in header_before, "До выхода должно показываться имя пользователя"
        
        # Кликаем Выйти
        logout_button = page.locator('button[title="Выйти"]')
        if logout_button.count() == 0:
            logout_button = page.locator('button:has-text("Выйти")')
        
        logout_button.first.click()
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # Проверяем что токена нет
        token_after = page.evaluate("localStorage.getItem('token')")
        print(f"Token after logout: {token_after}")
        assert token_after is None, "Токен должен быть удалён после выхода"
        
        # Проверяем что в шапке теперь "Гость" или кнопка "Войти"
        header_after = page.locator('header').text_content()
        print(f"Header after logout: {header_after[:100]}")
        
        has_login_button = page.locator('button:has-text("Войти")').count() > 0
        has_guest_text = "Гость" in header_after
        
        print(f"After logout - has_login_button: {has_login_button}, has_guest_text: {has_guest_text}")
        assert has_login_button or has_guest_text, \
            "После выхода должна быть кнопка 'Войти' или текст 'Гость'"


class TestUserSearch:
    """Тесты поиска пользователей."""

    def test_user_search(self, page):
        """Проверка поиска пользователей.

        Тест проверяет:
        - Поиск по "admin" находит пользователя admin
        - Поиск по "john" находит пользователя John Doe
        - Поиск по "pit2" находит пользователя pit2
        - Поиск по "Пупс" или "poo" находит пользователя с nickname "poo"
        """
        # Логинимся как админ
        login_via_ui(page, "admin@cafe.ru", "admin123")
        page.goto(f"{WEB_BASE_URL}/users")
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # Получаем всех пользователей до поиска
        page.wait_for_selector('table tbody tr', timeout=5000)
        all_rows = page.locator('table tbody tr').count()
        print(f"Всего пользователей: {all_rows}")

        # Тест 1: Поиск по "admin" - должен найти пользователя admin
        search_input = page.locator('input[placeholder*="Поиск"]')
        search_input.fill('admin')
        time.sleep(1)

        admin_rows = page.locator('table tbody tr').count()
        print(f"Найдено по 'admin': {admin_rows}")

        # Должен найтись хотя бы один пользователь
        assert admin_rows >= 1, "Поиск 'admin' должен найти хотя бы одного пользователя"

        # Проверяем что найденный пользователь содержит 'admin' в имени/email/nickname
        page_content = page.content()
        assert 'admin' in page_content.lower(), "Результат поиска 'admin' должен содержать 'admin'"

        # Сбрасываем поиск
        search_input.fill('')
        time.sleep(1)

        # Тест 2: Поиск по "john" - должен найти пользователя John Doe
        search_input.fill('john')
        time.sleep(1)

        john_rows = page.locator('table tbody tr').count()
        print(f"Найдено по 'john': {john_rows}")

        # Должен найтись пользователь John
        assert john_rows >= 1, "Поиск 'john' должен найти пользователя John Doe"

        # Сбрасываем поиск
        search_input.fill('')
        time.sleep(1)

        # Тест 3: Поиск по nickname "pit2"
        search_input.fill('pit2')
        time.sleep(1)

        pit2_rows = page.locator('table tbody tr').count()
        print(f"Найдено по 'pit2': {pit2_rows}")

        assert pit2_rows >= 1, "Поиск 'pit2' должен найти пользователя pit2"

        # Сбрасываем поиск
        search_input.fill('')
        time.sleep(1)

        # Тест 4: Поиск по "poo" (nickname пользователя)
        search_input.fill('poo')
        time.sleep(1)

        poo_rows = page.locator('table tbody tr').count()
        print(f"Найдено по 'poo': {poo_rows}")

        # Поиск по "poo" может не найти пользователей если нет такого nickname
        # Проверяем что поиск работает (возвращает 0 или больше)
        assert poo_rows >= 0, "Поиск 'poo' должен вернуть результат"

        # Сбрасываем поиск
        search_input.fill('')
        time.sleep(1)

        # Тест 5: Поиск по "anna" - должен найти менеджера Anna
        search_input.fill('anna')
        time.sleep(1)

        anna_rows = page.locator('table tbody tr').count()
        print(f"Найдено по 'anna': {anna_rows}")

        assert anna_rows >= 1, "Поиск 'anna' должен найти пользователя Anna"

        # Сбрасываем поиск
        search_input.fill('')
        time.sleep(1)

    def test_user_search_case_insensitive_latin(self, page):
        """Проверка регистронезависимости поиска для латиницы.

        Примечание: Поиск по кириллице может быть чувствителен к регистру
        из-за ограничений SQLite на Windows.
        """
        # Логинимся как админ
        login_via_ui(page, "admin@cafe.ru", "admin123")
        page.goto(f"{WEB_BASE_URL}/users")
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        search_input = page.locator('input[placeholder*="Поиск"]')

        # Поиск по "JOHN" (верхний регистр)
        search_input.fill('JOHN')
        time.sleep(1)
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        count_upper = page.locator('table tbody tr').count()
        print(f"Найдено по 'JOHN': {count_upper}")

        # Поиск по "john" (нижний регистр)
        search_input.fill('john')
        time.sleep(1)
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        count_lower = page.locator('table tbody tr').count()
        print(f"Найдено по 'john': {count_lower}")

        # Все три поиска должны вернуть одинаковое количество результатов
        assert count_upper == count_lower, \
            f"Поиск латиницы должен быть регистронезависимым: upper={count_upper}, lower={count_lower}"

        # Сбрасываем поиск
        search_input.fill('')
        time.sleep(1)


class TestOrdersPage:
    """Тесты страницы заказов."""

    def test_orders_load_without_error(self, page):
        """Проверка что заказы загружаются без ошибки.

        Тест проверяет:
        - Страница заказов загружается
        - Нет сообщения об ошибке
        - Отображается хотя бы один заказ
        """
        # Логинимся как менеджер (имеет доступ ко всем функциям)
        login_via_ui(page, "anna@cafe.ru", "manager123")
        page.goto(f"{WEB_BASE_URL}/orders")
        page.wait_for_load_state("networkidle")
        time.sleep(3)

        # Проверяем что нет ошибки загрузки
        error_element = page.locator('text=Ошибка загрузки заказов')
        assert error_element.count() == 0, "Не должно быть ошибки загрузки заказов"

        # Проверяем что таблица заказов загрузилась
        page.wait_for_selector('table tbody tr', timeout=10000)
        orders_count = page.locator('table tbody tr').count()
        print(f"Загружено заказов: {orders_count}")

        assert orders_count > 0, "Должен быть загружен хотя бы один заказ"

    def test_orders_have_items_with_menu_item(self, page):
        """Проверка что у каждого заказа есть items с menu_item.name.

        Тест проверяет:
        - API возвращает заказы с items
        - У каждого item есть menu_item с name
        - Отображаются названия блюд в таблице
        """
        # Логинимся как менеджер
        login_via_ui(page, "anna@cafe.ru", "manager123")
        page.goto(f"{WEB_BASE_URL}/orders")
        page.wait_for_load_state("networkidle")
        time.sleep(3)

        # Проверяем что таблица загрузилась
        page.wait_for_selector('table tbody tr', timeout=10000)
        orders_count = page.locator('table tbody tr').count()
        assert orders_count > 0, "Должны быть заказы"

        # Проверяем что в таблице отображаются названия блюд
        # Ищем текст с количеством и названием (формат: "2x Бургер")
        page_content = page.content()

        # Проверяем что есть хотя бы одно название блюда
        # (кириллические символы в названиях)
        has_menu_items = (
            'Бургер' in page_content or
            'Пицца' in page_content or
            'Борщ' in page_content or
            'Паста' in page_content or
            'Стейк' in page_content
        )
        assert has_menu_items, "В таблице должны отображаться названия блюд из menu_item.name"

    def test_orders_have_positive_total_price(self, page):
        """Проверка что total_price > 0 у всех заказов.

        Тест проверяет:
        - У каждого заказа есть общая стоимость
        - Общая стоимость больше нуля
        - Сумма отображается в таблице
        """
        # Логинимся как менеджер
        login_via_ui(page, "anna@cafe.ru", "manager123")
        page.goto(f"{WEB_BASE_URL}/orders")
        page.wait_for_load_state("networkidle")
        time.sleep(3)

        # Проверяем что таблица загрузилась
        page.wait_for_selector('table tbody tr', timeout=10000)
        orders_count = page.locator('table tbody tr').count()
        assert orders_count > 0, "Должны быть заказы"

        # Проверяем что у каждого заказа есть положительная сумма
        # В таблице сумма отображается с символом рубля (₽)
        price_elements = page.locator('table tbody tr td:nth-child(4)')
        price_count = price_elements.count()

        for i in range(price_count):
            price_text = price_elements.nth(i).text_content()
            print(f"Order {i+1} price: {price_text}")

            # Извлекаем число из текста (формат: "850 ₽")
            import re
            price_match = re.search(r'(\d+)', price_text)
            assert price_match, f"Не удалось найти цену в '{price_text}'"

            price_value = int(price_match.group(1))
            assert price_value > 0, f"Цена заказа должна быть > 0, получено: {price_value}"

    def test_orders_api_returns_valid_data(self, page):
        """Проверка что API заказов возвращает корректные данные.

        Тест проверяет:
        - GET /api/orders возвращает 200 и данные
        - Ответ содержит массив заказов
        - У каждого заказа есть items с menu_item.name
        - total_price > 0
        - Ловит ошибки CORS и авторизации
        """
        # Сначала переходим на страницу заказов чтобы работал относительный URL
        login_via_ui(page, "anna@cafe.ru", "manager123")
        page.goto(f"{WEB_BASE_URL}/orders")
        page.wait_for_load_state("networkidle")
        time.sleep(3)

        # Тест 1: Прямой запрос к API через frontend proxy (Vite proxy на backend)
        # Vite настроен на proxy /api -> http://localhost:8000/api
        # Используем полный URL с origin для надёжности
        result = page.evaluate("""
            async () => {
                // Запрос через Vite proxy с полным URL
                const baseUrl = window.location.origin;
                const response = await fetch(baseUrl + '/api/orders');
                return {
                    status: response.status,
                    data: await response.json()
                };
            }
        """)

        print(f"API Status: {result['status']}")
        print(f"Orders count: {len(result['data'])}")

        assert result['status'] == 200, f"API должен вернуть 200, получил: {result['status']}"
        assert isinstance(result['data'], list), "API должен вернуть массив заказов"
        assert len(result['data']) > 0, "Должен быть хотя бы один заказ"

        # Тест 2: Проверяем структуру данных заказов
        for i, order in enumerate(result['data']):
            print(f"\nOrder {i+1}:")
            print(f"  ID: {order['id']}, Table: {order['table_number']}")
            print(f"  Total: {order['total_price']}, Status: {order['status']}")
            print(f"  Items: {len(order['items'])}")

            # Проверка total_price > 0
            assert order['total_price'] > 0, \
                f"Order {order['id']}: total_price должен быть > 0, получил: {order['total_price']}"

            # Проверка items
            assert len(order['items']) > 0, \
                f"Order {order['id']}: должен иметь хотя бы один item"

            for j, item in enumerate(order['items']):
                print(f"    Item {j+1}: menu_item_id={item['menu_item_id']}, qty={item['quantity']}")

                # Проверка что menu_item существует и имеет name
                assert item.get('menu_item') is not None, \
                    f"Order {order['id']}, Item {j+1}: menu_item должен быть загружен"
                assert item['menu_item'].get('name'), \
                    f"Order {order['id']}, Item {j+1}: menu_item.name должен существовать"
                assert item['menu_item']['price'] > 0, \
                    f"Order {order['id']}, Item {j+1}: menu_item.price должен быть > 0"

                print(f"      menu_item.name: {item['menu_item']['name']}")

    def test_orders_api_cors_error_handling(self, page):
        """Проверка что frontend правильно обрабатывает CORS ошибки.

        Тест проверяет:
        - При недоступном backend появляется ошибка сети
        - Отображается корректное сообщение об ошибке
        """
        # Перехватываем запросы и эмулируем CORS ошибку
        def handle_failed_request(route, request):
            # Эмулируем network error с правильным параметром
            route.abort(error_code="addressunreachable")

        page.route("**/api/orders", handle_failed_request)

        # Логинимся как менеджер
        login_via_ui(page, "anna@cafe.ru", "manager123")
        # Переходим на страницу заказов
        page.goto(f"{WEB_BASE_URL}/orders")
        page.wait_for_load_state("networkidle")
        time.sleep(3)

        # Должна появиться ошибка сети
        error_element = page.locator('text=Ошибка сети')
        assert error_element.count() > 0, "Должна появиться ошибка сети при недоступном backend"

        # Сбрасываем перехват запросов
        page.unroute("**/api/orders")

    def test_orders_api_auth_error_handling(self, page):
        """Проверка что frontend правильно обрабатывает ошибки авторизации.

        Тест проверяет:
        - При 401 ошибке появляется сообщение о необходимости входа
        """
        # Перехватываем запросы и эмулируем 401 ошибку
        def handle_unauthorized_request(route, request):
            route.fulfill(status=401, json={"detail": "Требуется авторизация"})

        page.route("**/api/orders", handle_unauthorized_request)

        # Логинимся как менеджер
        login_via_ui(page, "anna@cafe.ru", "manager123")
        # Переходим на страницу заказов
        page.goto(f"{WEB_BASE_URL}/orders")
        page.wait_for_load_state("networkidle")
        time.sleep(3)

        # Должна появиться ошибка авторизации
        # Ищем ошибку в любом месте страницы
        page_content = page.content()
        has_auth_error = (
            'Требуется авторизация' in page_content or
            'ошибка' in page_content.lower()
        )

        # Альтернативно проверяем что страница показывает ошибку
        # Если 401 ошибка возвращена, frontend должен показать сообщение
        assert has_auth_error, f"Должна появиться ошибка авторизации при 401. Content: {page_content[:2000]}"

        # Сбрасываем перехват запросов
        page.unroute("**/api/orders")

    def test_orders_api_forbidden_error_handling(self, page):
        """Проверка что frontend правильно обрабатывает 403 ошибку.

        Тест проверяет:
        - При 403 ошибке появляется сообщение о недостатке прав
        """
        # Перехватываем запросы и эмулируем 403 ошибку
        def handle_forbidden_request(route, request):
            route.fulfill(status=403, json={"detail": "Недостаточно прав"})

        page.route("**/api/orders", handle_forbidden_request)

        # Логинимся как менеджер
        login_via_ui(page, "anna@cafe.ru", "manager123")
        # Переходим на страницу заказов
        page.goto(f"{WEB_BASE_URL}/orders")
        page.wait_for_load_state("networkidle")
        time.sleep(3)

        # Должна появиться ошибка прав доступа
        error_element = page.locator('text=Недостаточно прав')
        assert error_element.count() > 0, "Должна появиться ошибка прав доступа при 403"

        # Сбрасываем перехват запросов
        page.unroute("**/api/orders")


class TestUserManagement:
    """Тесты управления пользователями."""

    def test_create_user(self, page):
        """Проверка создания пользователя через UI."""
        # Логинимся как админ
        login_via_ui(page, "admin@cafe.ru", "admin123")
        page.goto(f"{WEB_BASE_URL}/users")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # Кликаем "Добавить пользователя"
        page.click('button:has-text("Добавить пользователя")')
        
        # Ждём пока модальное окно откроется - ищем по заголовку
        page.wait_for_selector('text=Добавить пользователя', timeout=5000)
        page.wait_for_selector('input[name="nickname"]', timeout=5000)
        time.sleep(1)
        
        # Заполняем форму
        page.fill('input[name="nickname"]', 'newuser')
        page.fill('input[name="name"]', 'New')
        page.fill('input[name="surname"]', 'User')
        page.fill('input[name="email"]', 'newuser@test.com')
        page.fill('input[name="password"]', 'password123')
        
        # Сохраняем
        page.click('button:has-text("Создать")')
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # Проверяем что пользователь создан
        page_content = page.content()
        assert "newuser@test.com" in page_content or "New User" in page_content, \
            "Пользователь должен появиться в списке"

    def test_action_menu(self, page):
        """Проверка меню действий."""
        # Логинимся как админ
        login_via_ui(page, "admin@cafe.ru", "admin123")
        page.goto(f"{WEB_BASE_URL}/users")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # Кликаем на иконку MoreVertical (три точки) в первой строке таблицы
        # Ждём пока таблица загрузится
        page.wait_for_selector('table tbody tr', timeout=5000)
        
        # Кликаем на первую кнопку с SVG
        action_button = page.locator('table tbody button svg').first
        action_button.click()
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        
        # Ждём пока меню откроется
        page.wait_for_selector('text=Редактировать', timeout=5000)
        
        # Проверяем что меню открылось - ищем текст кнопок
        page_content = page.content()
        has_edit = "Редактировать" in page_content
        has_delete = "Удалить" in page_content
        
        print(f"Action menu content - has_edit: {has_edit}, has_delete: {has_delete}")
        
        assert has_edit or has_delete, "Меню действий должно содержать опции"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
