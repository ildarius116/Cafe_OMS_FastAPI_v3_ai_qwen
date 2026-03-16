# Отчёт о состоянии тестов

**Дата:** 14 марта 2026 г.

---

## 📊 Статус тестов

| Категория | Пройдено | Всего | % |
|-----------|----------|-------|---|
| **auth** | 8 | 8 | 100% |
| **orders** | 5 | 13 | 38% |
| **users** | 1 | 7 | 14% |
| **ИТОГО** | **14** | **28** | **50%** |

---

## ✅ Проходящие тесты

### Аутентификация (8/8)
- `test_register_success` — регистрация работает
- `test_register_duplicate_email` — защита от дубликатов email
- `test_register_duplicate_nickname` — защита от дубликатов nickname
- `test_register_invalid_email` — валидация email
- `test_register_short_password` — валидация пароля
- `test_login_success` — вход по email/nickname работает
- `test_login_wrong_password` — проверка пароля
- `test_login_nonexistent_user` — проверка существования пользователя

### Заказы (5/13)
- `test_get_orders_public` — публичный доступ к списку заказов
- `test_get_order_by_id` — получение заказа по ID
- `test_get_order_not_found` — обработка несуществующего заказа
- `test_get_orders_by_table` — поиск по столу
- `test_get_active_orders` — получение активных заказов

### Пользователи (1/7)
- `test_get_users_requires_auth` — требуется авторизация

---

## ❌ Проваливающиеся тесты

Все провалы с ошибкой **401 Unauthorized** вместо ожидаемого статуса.

### Причина
Тесты создают изолированную БД для каждого теста, но не создают пользователей с нужными уровнями доступа (manager, admin) перед выполнением операций.

### Список failing тестов:
1. `test_create_order` — требует авторизованного пользователя
2. `test_create_order_calculates_total` — требует авторизованного пользователя
3. `test_update_order_status` — требует авторизованного пользователя
4. `test_update_order` — требует авторизованного пользователя
5. `test_delete_order_requires_manager` — требует manager+ токен
6. `test_delete_order_manager` — требует manager токен
7. `test_get_revenue_requires_manager` — требует manager+ токен
8. `test_get_revenue_manager` — требует manager токен
9. `test_get_users_manager` — требует manager токен
10. `test_create_user_admin` — требует admin токен
11. `test_create_user_requires_admin` — требует admin токен
12. `test_update_user_admin` — требует admin токен
13. `test_delete_user_admin` — требует admin токен
14. `test_cannot_delete_higher_level` — требует admin токен

---

## 🔧 Решение

Необходимо добавить в `conftest.py` фикстуры для создания пользователей с разными уровнями доступа:

```python
@pytest.fixture
def admin_token(client, test_db):
    """Создаёт admin пользователя и возвращает токен."""
    # Создание пользователя
    # Login
    # Возврат токена
```

---

## 📝 Примечания

### Тестовая БД vs Реальная БД

**Тесты используют изолированную БД:**
- Создаётся перед каждым тестом
- Удаляется после теста
- Не зависит от `cafe.db`

**Реальная БД (`cafe.db`):**
- Используется uvicorn (приложение)
- Заполняется через `create_test_data.py`
- Требует остановки uvicorn для пересоздания

### Инструкция для реальной БД

```bash
# 1. Остановить uvicorn
# 2. Заполнить БД
python create_test_data.py

# 3. Запустить uvicorn
uvicorn app.main:app --reload

# 4. Проверить curl
curl -X POST 'http://localhost:8000/api/auth/login' ^
  -H 'Content-Type: application/x-www-form-urlencoded' ^
  -d 'username=pit2&password=123456'
```

Или использовать скрипт:
```bash
python reset_db.py
```
