# ФАЗА 9: Тестирование и документация

## Цель
Покрыть проект тестами и создать полную документацию.

## Задачи

### 9.1. Backend тесты

#### Unit тесты сервисов
- [ ] test_user_service.py
  - [ ] test_create_user_success
  - [ ] test_create_user_duplicate_email
  - [ ] test_update_user_permissions
  - [ ] test_delete_user_permissions
  - [ ] test_get_users_filtered

- [ ] test_order_service.py
  - [ ] test_create_order_calculates_total
  - [ ] test_update_status
  - [ ] test_get_revenue
  - [ ] test_get_orders_by_table

#### Integration тесты API
- [ ] test_auth_api.py
  - [ ] test_register_success
  - [ ] test_register_duplicate_email
  - [ ] test_login_success
  - [ ] test_login_wrong_password
  - [ ] test_protected_endpoint_requires_auth

- [ ] test_users_api.py
  - [ ] test_get_users_requires_manager
  - [ ] test_create_user_as_admin
  - [ ] test_update_user_hierarchy
  - [ ] test_delete_user

- [ ] test_orders_api.py
  - [ ] test_get_orders
  - [ ] test_create_order
  - [ ] test_update_order_status
  - [ ] test_get_revenue_requires_manager

### 9.2. Frontend тесты

#### Component тесты
- [ ] test Sidebar component
- [ ] test Header component
- [ ] test LoginPage form
- [ ] test OrdersTable component
- [ ] test UsersTable component

#### Integration тесты
- [ ] test orders page flow
- [ ] test users page flow
- [ ] test auth flow

### 9.3. Документация

#### README.md
- [ ] Описание проекта
- [ ] Стек технологий
- [ ] Инструкция по установке
- [ ] API документация
- [ ] Примеры использования
- [ ] Тестовые данные

#### API документация
- [ ] Swagger UI (/docs)
- [ ] ReDoc (/redoc)
- [ ] Примеры запросов
- [ ] Описание ошибок

#### Code documentation
- [ ] Docstrings для всех функций
- [ ] Type hints
- [ ] Комментарии для сложной логики

## Ожидаемый результат
- 80%+ покрытие тестами
- Полная документация
- Working CI/CD (опционально)
