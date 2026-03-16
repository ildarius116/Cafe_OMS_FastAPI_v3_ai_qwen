# Cafe Orders — Система управления заказами в кафе

Веб-приложение для управления заказами и пользователями в кафе с полным CRUD, аутентификацией и ролевой моделью доступа.

## 📋 Оглавление

- [Возможности](#возможности)
- [Стек технологий](#стек-технологий)
- [Установка](#установка)
- [Запуск](#запуск)
- [API Документация](#api-документация)
- [Структура проекта](#структура-проекта)
- [Уровни доступа](#уровни-доступа)

---

## 🚀 Возможности

### Для заказов:
- ✅ Создание, чтение, обновление, удаление заказов
- ✅ Поиск по номеру стола и ID
- ✅ Фильтрация по статусу (в ожидании, готово, оплачено)
- ✅ Автоматический расчёт общей стоимости
- ✅ Изменение статуса заказа

### Для пользователей:
- ✅ Регистрация и аутентификация (JWT)
- ✅ Управление профилем
- ✅ Ролевая модель доступа (7 уровней)
- ✅ Поиск и фильтрация пользователей
- ✅ Управление правами доступа

### Дополнительно:
- ✅ Расчёт выручки за смену
- ✅ REST API с документацией (Swagger/OpenAPI)
- ✅ Адаптивный веб-интерфейс
- ✅ Обработка ошибок и валидация

---

## 🛠 Стек технологий

### Backend
| Технология | Версия | Описание |
|------------|--------|----------|
| Python | 3.14+ | Язык программирования |
| FastAPI | 0.115 | Веб-фреймворк |
| SQLAlchemy | 2.0 | ORM для работы с БД |
| Pydantic | 2.7 | Валидация данных |
| Alembic | 1.13 | Миграции БД |
| python-jose | 3.3 | JWT токены |
| Passlib | 1.7 | Хэширование паролей |
| SQLite/PostgreSQL | — | База данных |

### Frontend
| Технология | Версия | Описание |
|------------|--------|----------|
| React | 19 | UI библиотека |
| TypeScript | 5.7 | Типизация |
| Tailwind CSS | 3.4 | Стилизация |
| React Router | 7.2 | Роутинг |
| Zustand | 5.0 | Управление состоянием |
| Axios | 1.7 | HTTP клиент |
| Lucide React | 0.475 | Иконки |

---

## 📦 Установка

### 1. Клонирование репозитория
```bash
cd E:\PycharmProjects\AI_webinar\test_project
```

### 2. Установка backend зависимостей
```bash
# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt
```

### 3. Установка frontend зависимостей
```bash
cd frontend
npm install
```

### 4. Создание тестовых данных
```bash
# Из корня проекта
python create_test_data.py
```

---

## ▶️ Запуск

### Backend
```bash
# Из корня проекта (с активированным venv)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Или используйте скрипт:**
```bash
# Windows
start.bat

# Linux/Mac
bash start.sh
```

### Frontend
```bash
# В отдельном терминале
cd frontend
npm run dev
```

### Доступ к приложению
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Документация (Swagger):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 📖 API Документация

### Аутентификация

#### Регистрация
```http
POST /api/auth/register
Content-Type: application/json

{
  "nickname": "john_doe",
  "name": "John",
  "surname": "Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

#### Вход
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=john@example.com&password=securepassword123
```

**Ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Заказы

#### Получить все заказы
```http
GET /api/orders?skip=0&limit=10&status=pending
Authorization: Bearer <token>
```

#### Создать заказ
```http
POST /api/orders
Authorization: Bearer <token>
Content-Type: application/json

{
  "table_number": 5,
  "items": [
    {"name": "Бургер", "price": 350, "quantity": 2},
    {"name": "Картофель", "price": 150, "quantity": 1}
  ]
}
```

#### Изменить статус
```http
PATCH /api/orders/{order_id}/status
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "ready"
}
```

#### Получить выручку
```http
GET /api/orders/revenue?start_date=2026-03-14&end_date=2026-03-14
Authorization: Bearer <token>
```

### Пользователи

#### Получить всех пользователей
```http
GET /api/users?skip=0&limit=10&level=client
Authorization: Bearer <token>
```

#### Обновить пользователя
```http
PUT /api/users/{user_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "level": "staff",
  "status": "active"
}
```

---

## 🏗 Структура проекта

```
test_project/
├── app/                        # Backend (FastAPI)
│   ├── __init__.py
│   ├── main.py                 # Точка входа
│   ├── config.py               # Конфигурация
│   ├── database.py             # Подключение к БД
│   ├── models/                 # SQLAlchemy модели
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── order.py
│   ├── schemas/                # Pydantic схемы
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── order.py
│   ├── services/               # Бизнес-логика
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── order_service.py
│   ├── routers/                # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   └── orders.py
│   └── core/                   # Утилиты
│       ├── __init__.py
│       ├── security.py         # JWT, хэширование
│       └── exceptions.py       # Исключения
├── frontend/                   # Frontend (React)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── tasks/                      # Задачи по фазам
├── reports/                    # Отчёты
├── requirements.txt            # Python зависимости
├── create_test_data.py         # Тестовые данные
└── README.md                   # Этот файл
```

---

## 👥 Уровни доступа

| Уровень | Создание | Удаление | Поиск | Редактирование |
|---------|----------|----------|-------|----------------|
| 🟦 Гость | ❌ | ❌ | ❌ | ❌ |
| 🟦 Клиент | ✅ (себя) | ✅ (себя) | ❌ | ✅ (себя) |
| 🟩 Сотрудник | ✅ | ❌ | ❌ | ❌ |
| 🟪 Менеджер | ✅ | ❌ | ✅ | ✅ (ниже себя) |
| 🟥 Администратор | ✅ | ✅ | ✅ | ✅ (ниже себя) |
| 🟦 Руководитель | ✅ | ✅ | ✅ | ✅ (ниже себя) |
| 🟨 Суперпользователь | ✅ | ✅ | ✅ | ✅ (ниже себя) |

> **Важно:** Понизить любого пользователя до уровня "гость" нельзя.

---

## 🧪 Тестовые учётные данные

После запуска `create_test_data.py`:

| Email | Пароль | Уровень |
|-------|--------|---------|
| admin@cafe.ru | admin123 | Администратор |
| anna@cafe.ru | manager123 | Менеджер |
| igor@cafe.ru | staff123 | Сотрудник |
| john@example.com | client123 | Клиент |

---

## 📝 Лицензия

ISC
