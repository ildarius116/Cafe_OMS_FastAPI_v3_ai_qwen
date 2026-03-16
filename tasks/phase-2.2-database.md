# ФАЗА 2.2: Настройка базы данных

## Цель
Настроить SQLAlchemy для работы с SQLite (локально) и PostgreSQL (production).

## Задачи

### 1. Создание database.py
- Engine для SQLite
- SessionLocal для сессий
- Base для моделей

### 2. Создание моделей
**User:**
- id (Integer, primary key)
- nickname (String, unique)
- name (String)
- surname (String)
- email (String, unique)
- level (Enum: guest, client, staff, manager, admin, director, superuser)
- status (Enum: active, inactive)
- hashed_password (String)

**Order:**
- id (Integer, primary key)
- table_number (Integer)
- items (JSON/relationship)
- total_price (Float)
- status (Enum: pending, ready, paid)
- created_at (DateTime)

**OrderItem:**
- id (Integer, primary key)
- order_id (ForeignKey)
- name (String)
- price (Float)
- quantity (Integer)

### 3. Настройка Alembic
```bash
alembic init alembic
```

### 4. Создание миграций
- Initial migration с таблицами users и orders

## Ожидаемый результат
- Рабочая конфигурация SQLAlchemy
- Модели данных с правильными связями
- Настроенные миграции
