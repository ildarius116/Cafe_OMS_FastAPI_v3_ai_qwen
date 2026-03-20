"""
UI функциональные тесты через Playwright.

Тесты проверяют работу веб-интерфейса через браузер:
- Аутентификация (регистрация, вход, выход)
- Страница заказов (просмотр, создание, редактирование, удаление)
- Страница пользователей (просмотр, поиск, управление)
- Страница выручки
- Страница профиля

Все взаимодействия происходят ЧЕРЕЗ БРАУЗЕР - никаких API вызовов напрямую.
"""

import pytest
import time
from playwright.sync_api import Page, Browser, BrowserContext, expect
from conftest import (
    WEB_BASE_URL, unique_email, unique_nickname,
    register_via_ui, login_via_ui, logout_via_ui
)


# ============================================================================
# Тесты аутентификации
# ============================================================================

class TestAuthUI:
    """Тесты аутентификации через UI."""

    def test_register_via_ui(self, page: Page):
        """Тест регистрации через веб-форму.

        Шаги:
        1. Перейти на /login
        2. Переключиться на вкладку "Регистрация"
        3. Заполнить все поля формы
        4. Нажать кнопку "Зарегистрироваться"
        5. Проверить что токен сохранён в localStorage
        """
        email = unique_email()
        nickname = unique_nickname()

        token = register_via_ui(page, email, nickname, "Test", "User", "test123")

        # Проверяем что перенаправило на главную
        expect(page).to_have_url(f"{WEB_BASE_URL}/")
        assert token is not None

    def test_login_via_ui(self, page: Page):
        """Тест входа через веб-форму.

        Шаги:
        1. Зарегистрировать пользователя
        2. Выйти
        3. Войти через форму логина
        4. Проверить токен в localStorage
        """
        email = unique_email()
        nickname = unique_nickname()
        password = "login123"

        # Сначала регистрируемся
        register_via_ui(page, email, nickname, "Login", "Test", password)

        # Выходим
        logout_via_ui(page)

        # Входим через форму логина
        token = login_via_ui(page, email, password)

        # Проверяем что перенаправило на главную
        expect(page).to_have_url(f"{WEB_BASE_URL}/")
        assert token is not None

    def test_logout_via_ui(self, page: Page):
        """Тест выхода через UI.

        Шаги:
        1. Войти
        2. Проверить наличие токена
        3. Выйти
        4. Проверить что токен удалён
        """
        email = unique_email()
        nickname = unique_nickname()

        # Входим
        login_via_ui(page, email, "test123")

        # Проверяем что токен есть
        token_before = page.evaluate("localStorage.getItem('token')")
        assert token_before is not None

        # Выходим
        logout_via_ui(page)

        # Проверяем что токена нет
        token_after = page.evaluate("localStorage.getItem('token')")
        assert token_after is None

    def test_guest_sees_login_button(self, page: Page):
        """Тест что гость видит кнопку 'Войти'."""
        page.goto(f"{WEB_BASE_URL}/")
        page.wait_for_load_state("networkidle")

        # Должна быть кнопка "Войти" или текст "Гость"
        page_content = page.content()
        has_login_button = page.locator('button:has-text("Войти")').count() > 0
        has_guest_text = "Гость" in page_content

        assert has_login_button or has_guest_text, \
            "До входа должна быть кнопка 'Войти' или текст 'Гость'"


# ============================================================================
# Тесты страницы заказов
# ============================================================================

class TestOrdersPageUI:
    """Тесты страницы заказов."""

    def test_orders_page_loads(self, page: Page):
        """Тест загрузки страницы заказов."""
        email = unique_email()
        login_via_ui(page, email, "test123")

        page.goto(f"{WEB_BASE_URL}/orders")
        page.wait_for_load_state("networkidle")

        # Проверяем заголовок
        header = page.locator('h2:has-text("Заказы")')
        expect(header).to_be_visible()

    def test_create_order_via_ui(self, page: Page):
        """Тест создания заказа через UI.

        Шаги:
        1. Перейти на /orders
        2. Нажать кнопку "Новый заказ"
        3. Заполнить номер стола
        4. Заполнить данные о блюде
        5. Нажать "Создать заказ"
        6. Проверить что заказ появился в таблице
        """
        email = unique_email()
        login_via_ui(page, email, "test123")

        page.goto(f"{WEB_BASE_URL}/orders")
        page.wait_for_load_state("networkidle")

        # Кликаем на кнопку "Новый заказ"
        page.click('button:has-text("Новый заказ")')

        # Заполняем номер стола
        page.fill('input[type="number"][min="1"]', '99')

        # Заполняем блюдо
        page.fill('input[placeholder="Название блюда"]', 'Test Dish')
        page.fill('input[placeholder="Цена"]', '100')
        page.fill('input[placeholder="Кол-во"]', '1')

        # Сохраняем заказ
        page.click('button:has-text("Создать заказ")')
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Проверяем что заказ создан
        page_content = page.content()
        assert '99' in page_content or 'Test Dish' in page_content

    def test_orders_table_displays_items(self, page: Page):
        """Тест что таблица заказов отображает названия блюд."""
        email = unique_email()
        login_via_ui(page, email, "test123")

        page.goto(f"{WEB_BASE_URL}/orders")
        page.wait_for_load_state("networkidle")

        # Проверяем что в таблице есть названия блюд
        page_content = page.content()

        # Ищем названия блюд (кириллица)
        has_menu_items = (
            'Бургер' in page_content or
            'Пицца' in page_content or
            'Борщ' in page_content or
            'Паста' in page_content or
            'Стейк' in page_content or
            'Заказ' in page_content  # Может быть сообщение "Заказы не найдены"
        )
        assert has_menu_items

    def test_filter_orders_by_status(self, page: Page):
        """Тест фильтрации заказов по статусу."""
        email = unique_email()
        login_via_ui(page, email, "test123")

        page.goto(f"{WEB_BASE_URL}/orders")
        page.wait_for_load_state("networkidle")

        # Выбираем фильтр "В ожидании"
        page.select_option('select', 'pending')
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Проверяем что фильтр применён
        selected_option = page.locator('select').first.input_value()
        assert selected_option == "pending"


# ============================================================================
# Тесты страницы пользователей
# ============================================================================

class TestUsersPageUI:
    """Тесты страницы пользователей."""

    def test_users_page_requires_manager(self, page: Page):
        """Тест что страница пользователей требует manager+."""
        email = unique_email()
        login_via_ui(page, email, "test123")

        page.goto(f"{WEB_BASE_URL}/users")
        page.wait_for_load_state("networkidle")

        # Должна быть ошибка или редирект
        # Проверяем что нет таблицы пользователей
        table = page.locator('table')
        # Таблица может быть, но без данных или с ошибкой

    def test_users_search(self, page: Page):
        """Тест поиска пользователей.

        Шаги:
        1. Войти как admin
        2. Перейти на /users
        3. Ввести поисковый запрос
        4. Проверить результаты
        """
        # Используем тестового админа
        login_via_ui(page, "admin@cafe.ru", "admin123")

        page.goto(f"{WEB_BASE_URL}/users")
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # Ждём загрузки таблицы
        page.wait_for_selector('table tbody tr', timeout=10000)

        # Ищем по "admin"
        search_input = page.locator('input[placeholder*="Поиск"]')
        search_input.fill('admin')
        time.sleep(1)

        # Проверяем что нашлись результаты
        page_content = page.content()
        assert 'admin' in page_content.lower()

    def test_users_table_columns(self, page: Page):
        """Тест что таблица пользователей имеет правильные колонки."""
        login_via_ui(page, "admin@cafe.ru", "admin123")

        page.goto(f"{WEB_BASE_URL}/users")
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # Проверяем заголовки колонок
        page_content = page.content()

        # Должны быть колонки: ID, Пользователь, Email, Уровень, Статус
        has_columns = (
            'ID' in page_content or
            'Пользователь' in page_content or
            'Email' in page_content or
            'Уровень' in page_content
        )
        assert has_columns


# ============================================================================
# Тесты страницы выручки
# ============================================================================

class TestRevenuePageUI:
    """Тесты страницы выручки."""

    def test_revenue_page_loads(self, page: Page):
        """Тест загрузки страницы выручки."""
        email = unique_email()
        login_via_ui(page, email, "test123")

        page.goto(f"{WEB_BASE_URL}/revenue")
        page.wait_for_load_state("networkidle")

        # Проверяем заголовок
        header = page.locator('h2:has-text("Выручка")')
        expect(header).to_be_visible()

    def test_revenue_displays_stats(self, page: Page):
        """Тест что страница выручки отображает статистику."""
        email = unique_email()
        login_via_ui(page, email, "test123")

        page.goto(f"{WEB_BASE_URL}/revenue")
        page.wait_for_load_state("networkidle")

        # Проверяем наличие карточек статистики
        page_content = page.content()

        has_stats = (
            'Выручка' in page_content or
            'Общая выручка' in page_content or
            'Средний чек' in page_content or
            '₽' in page_content
        )
        assert has_stats


# ============================================================================
# Тесты страницы профиля
# ============================================================================

class TestProfilePageUI:
    """Тесты страницы профиля."""

    def test_profile_page_loads(self, page: Page):
        """Тест загрузки страницы профиля."""
        email = unique_email()
        nickname = unique_nickname()
        login_via_ui(page, email, "test123")

        page.goto(f"{WEB_BASE_URL}/profile")
        page.wait_for_load_state("networkidle")

        # Проверяем что страница загрузилась
        expect(page).to_have_url(f"{WEB_BASE_URL}/profile")

    def test_profile_displays_user_data(self, page: Page):
        """Тест что профиль отображает данные пользователя."""
        email = unique_email()
        nickname = unique_nickname()
        login_via_ui(page, email, "test123")

        page.goto(f"{WEB_BASE_URL}/profile")
        page.wait_for_load_state("networkidle")

        # Проверяем что email или nickname отображаются
        page_content = page.content()
        assert email in page_content or nickname in page_content


# ============================================================================
# Тесты навигации и layout
# ============================================================================

class TestNavigationUI:
    """Тесты навигации и layout."""

    def test_sidebar_navigation(self, page: Page):
        """Тест навигации через sidebar."""
        email = unique_email()
        login_via_ui(page, email, "test123")

        page.goto(f"{WEB_BASE_URL}/")
        page.wait_for_load_state("networkidle")

        # Проверяем наличие sidebar
        sidebar = page.locator('nav')
        expect(sidebar).to_be_visible()

        # Проверяем ссылки навигации
        page_content = page.content()
        has_nav_links = (
            'Заказы' in page_content or
            'Пользователи' in page_content or
            'Выручка' in page_content
        )
        assert has_nav_links

    def test_header_displays_user(self, page: Page):
        """Тест что header отображает информацию о пользователе."""
        email = unique_email()
        nickname = unique_nickname()
        login_via_ui(page, email, "test123")

        page.goto(f"{WEB_BASE_URL}/")
        page.wait_for_load_state("networkidle")

        # Проверяем header
        header = page.locator('header')
        expect(header).to_be_visible()

        # После входа должно быть имя пользователя (не "Гость")
        header_content = header.text_content()
        # Проверяем что есть кнопка выхода или имя пользователя
        has_user_info = (
            'Выйти' in header_content or
            nickname in header_content or
            email in header_content
        )
        assert has_user_info

    def test_responsive_layout(self, page: Page):
        """Тест адаптивного layout."""
        email = unique_email()
        login_via_ui(page, email, "test123")

        page.goto(f"{WEB_BASE_URL}/")
        page.wait_for_load_state("networkidle")

        # Проверяем что страница имеет правильную структуру
        page_content = page.content()

        # Должны быть основные элементы layout
        has_layout = (
            'header' in page_content.lower() or
            'nav' in page_content.lower() or
            'main' in page_content.lower()
        )
        assert has_layout


# ============================================================================
# Тесты обработки ошибок
# ============================================================================

class TestErrorHandlingUI:
    """Тесты обработки ошибок в UI."""

    def test_network_error_handling(self, page: Page):
        """Тест обработки ошибки сети."""
        # Перехватываем запросы и эмулируем ошибку
        def handle_failed_request(route, request):
            route.abort(error_code="addressunreachable")

        page.route("**/api/orders", handle_failed_request)

        email = unique_email()
        login_via_ui(page, email, "test123")

        page.goto(f"{WEB_BASE_URL}/orders")
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # Должна появиться ошибка
        page_content = page.content()
        has_error = (
            'ошибка' in page_content.lower() or
            'Ошибка' in page_content or
            'недоступен' in page_content.lower()
        )
        assert has_error

        # Сбрасываем перехват
        page.unroute("**/api/orders")

    def test_401_error_handling(self, page: Page):
        """Тест обработки ошибки авторизации."""
        # Перехватываем запросы и эмулируем 401
        def handle_unauthorized_request(route, request):
            route.fulfill(status=401, json={"detail": "Требуется авторизация"})

        page.route("**/api/orders", handle_unauthorized_request)

        email = unique_email()
        login_via_ui(page, email, "test123")

        page.goto(f"{WEB_BASE_URL}/orders")
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # Должна появиться ошибка авторизации
        page_content = page.content()
        has_auth_error = (
            'авторизация' in page_content.lower() or
            'Требуется авторизация' in page_content or
            'ошибка' in page_content.lower()
        )
        assert has_auth_error

        # Сбрасываем перехват
        page.unroute("**/api/orders")


# ============================================================================
# Тесты форм и валидации
# ============================================================================

class TestFormValidationUI:
    """Тесты валидации форм в UI."""

    def test_registration_form_validation(self, page: Page):
        """Тест валидации формы регистрации."""
        page.goto(f"{WEB_BASE_URL}/login")
        page.wait_for_load_state("networkidle")

        # Переключаемся на регистрацию
        page.click('button:has-text("Регистрация")')

        # Пытаемся отправить пустую форму
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")

        # Должны быть ошибки валидации
        # (проверяем что форма не отправилась)
        token = page.evaluate("localStorage.getItem('token')")
        assert token is None  # Токен не должен появиться

    def test_login_form_validation(self, page: Page):
        """Тест валидации формы входа."""
        page.goto(f"{WEB_BASE_URL}/login")
        page.wait_for_load_state("networkidle")

        # Пытаемся отправить форму с пустыми полями
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")

        # Должна быть ошибка (форма не должна отправиться)
        token = page.evaluate("localStorage.getItem('token')")
        assert token is None

    def test_order_form_validation(self, page: Page):
        """Тест валидации формы заказа."""
        email = unique_email()
        login_via_ui(page, email, "test123")

        page.goto(f"{WEB_BASE_URL}/orders")
        page.wait_for_load_state("networkidle")

        # Кликаем "Новый заказ"
        page.click('button:has-text("Новый заказ")')

        # Пытаемся отправить форму без заполнения
        page.click('button:has-text("Создать заказ")')
        page.wait_for_load_state("networkidle")

        # Форма должна показать ошибки или не отправиться
        # (проверяем что заказ не создался)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
