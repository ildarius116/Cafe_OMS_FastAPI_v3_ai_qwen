# ФАЗА 2.1: Инициализация Python-проекта

## Цель
Создать структуру Python-проекта для FastAPI приложения.

## Задачи

### 1. Создание виртуального окружения
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 2. Создание requirements.txt
**Зависимости:**
```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.30
alembic==1.13.0
pydantic==2.7.0
pydantic-settings==2.3.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
aiosqlite==0.20.0
```

### 3. Создание структуры проекта
```
app/
├── __init__.py
├── main.py              # Точка входа FastAPI
├── config.py            # Конфигурация
├── database.py          # Подключение к БД
├── models/
│   ├── __init__.py
│   ├── user.py
│   └── order.py
├── schemas/
│   ├── __init__.py
│   ├── user.py
│   └── order.py
├── services/
│   ├── __init__.py
│   ├── user_service.py
│   └── order_service.py
├── routers/
│   ├── __init__.py
│   ├── auth.py
│   ├── users.py
│   └── orders.py
└── core/
    ├── __init__.py
    ├── security.py      # Хэширование, JWT
    └── exceptions.py    # Кастомные исключения
```

### 4. Создание базовых файлов
- `app/__init__.py`
- `app/main.py` — базовое FastAPI приложение
- `app/config.py` — настройки из .env

## Ожидаемый результат
- Рабочая структура проекта
- Установленные зависимости
- Базовое приложение FastAPI
