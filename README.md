# Cafe Orders — Система управления заказами в кафе

**Полнофункциональное веб-приложение** для управления заказами и пользователями в кафе с аутентификацией, ролевой моделью доступа и полным CRUD.

Приложение упаковано в **Docker-контейнеры** (backend, frontend, PostgreSQL) для быстрого развёртывания.

---

## 📋 Оглавление

- [Возможности](#-возможности)
- [Стек технологий](#-стек-технологий)
- [Быстрый старт (Docker)](#-быстрый-старт-docker)
- [Локальная разработка](#-локальная-разработка)
- [API Документация](#-api-документация)
- [Структура проекта](#-структура-проекта)
- [Уровни доступа](#-уровни-доступа)
- [Тестирование](#-тестирование)
- [Подключение к PostgreSQL](#-подключение-к-postgresql)
- [Интерфейс](#-интерфейс)

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
| Pydantic | 2.9 | Валидация данных |
| Pydantic Settings | 2.6 | Управление настройками |
| python-jose | 3.3 | JWT токены |
| bcrypt | 5.0 | Хэширование паролей |
| psycopg2-binary | 2.9 | PostgreSQL драйвер |
| Poetry | 2.3 | Менеджер зависимостей |

### Frontend
| Технология | Версия | Описание |
|------------|--------|----------|
| React | 19 | UI библиотека |
| TypeScript | 5.7 | Типизация |
| Tailwind CSS | 3.4 | Стилизация |
| React Router | 7.2 | Роутинг |
| Zustand | 5.0 | Управление состоянием |
| Axios | 1.7 | HTTP клиент |
| React Hook Form | 7.54 | Управление формами |
| Zod | 3.24 | Валидация схем |
| Lucide React | 0.475 | Иконки |
| Vite | 6.1 | Сборщик |

### База данных и инфраструктура
| Технология | Версия | Описание |
|------------|--------|----------|
| PostgreSQL | 15 | Основная БД |
| Docker | 20+ | Контейнеризация |
| Docker Compose | 2+ | Оркестрация контейнеров |
| Nginx | Alpine | Reverse proxy (production) |

### Тестирование
| Технология | Версия | Описание |
|------------|--------|----------|
| pytest | 8.2 | Тестовый фреймворк |
| pytest-asyncio | 0.23.6 | Асинхронные тесты |
| httpx | 0.27 | TestClient для FastAPI |
| playwright | 1.40 | E2E браузерные тесты |

---

## 🐳 Быстрый старт (Docker)

### Требования
- Docker Desktop (Windows/Mac) или Docker + Docker Compose (Linux)
- Порт 5432, 8000, 5173 должны быть свободны

### 1. Запуск контейнеров

```bash
# Запуск всех сервисов (backend, frontend, PostgreSQL)
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d

# Production режим (с nginx)
docker-compose --profile production up -d
```

### 2. Создание тестовых данных

```bash
# Выполнить скрипт в контейнере backend
docker-compose exec backend poetry run python create_test_data.py --recreate
```

### 3. Доступ к приложению

| Сервис | URL |
|--------|-----|
| **Frontend** | http://localhost:5173 |
| **Backend API** | http://localhost:8000 |
| **Swagger Docs** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |
| **Health Check** | http://localhost:8000/health |
| **Nginx (production)** | http://localhost:8080 |

### 4. Остановка

```bash
docker-compose down

# Полная очистка (включая данные БД)
docker-compose down -v
```

---

## 🛠 Локальная разработка

### 1. Установка зависимостей

```bash
# Установка Poetry (если не установлен)
pip install poetry

# Установка backend зависимостей
poetry install

# Установка frontend зависимостей
cd frontend
npm install
```

### 2. Настройка окружения

```bash
# Скопируйте шаблон
cp .env.example .env

# Отредактируйте при необходимости
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/cafe_orders
```

### 3. Запуск PostgreSQL (локально)

```bash
# Через Docker
docker run -d --name cafe-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=cafe_orders \
  -p 5432:5432 \
  postgres:15
```

### 4. Создание тестовых данных

```bash
poetry run python create_test_data.py --recreate
```

### 5. Запуск серверов

**Terminal 1 — Backend:**
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

---

## 📋 API Документация

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

| Метод | Endpoint | Описание | Auth |
|-------|----------|----------|------|
| GET | `/api/orders` | Список заказов (с фильтрами) | ❌ |
| GET | `/api/orders/{id}` | Заказ по ID | ❌ |
| POST | `/api/orders` | Создание заказа | ✅ |
| PUT | `/api/orders/{id}` | Обновление заказа | ✅ |
| PATCH | `/api/orders/{id}/status` | Изменение статуса | ✅ |
| DELETE | `/api/orders/{id}` | Удаление заказа | Manager+ |
| GET | `/api/orders/revenue` | Выручка за период | Manager+ |
| GET | `/api/orders/active` | Активные заказы | ❌ |
| GET | `/api/orders/table/{num}` | Заказы по столу | ❌ |

#### Создать заказ
```http
POST /api/orders
Authorization: Bearer <token>
Content-Type: application/json

{
  "table_number": 5,
  "items": [
    {"menu_item_id": 1, "quantity": 2},
    {"menu_item_id": 3, "quantity": 1}
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

### Пользователи

| Метод | Endpoint | Описание | Auth |
|-------|----------|----------|------|
| GET | `/api/users/me` | Текущий пользователь | ✅ |
| GET | `/api/users` | Список пользователей | Manager+ |
| GET | `/api/users/{id}` | Пользователь по ID | ✅ |
| POST | `/api/users` | Создание пользователя | Admin+ |
| PUT | `/api/users/{id}` | Обновление пользователя | Admin+ |
| DELETE | `/api/users/{id}` | Удаление пользователя | Admin+ |

### Меню

| Метод | Endpoint | Описание | Auth |
|-------|----------|----------|------|
| GET | `/api/menu-items` | Список блюд меню | ❌ |
| GET | `/api/menu-items/{id}` | Блюдо по ID | ❌ |
| POST | `/api/menu-items` | Добавление блюда | Admin+ |
| PUT | `/api/menu-items/{id}` | Обновление блюда | Admin+ |
| DELETE | `/api/menu-items/{id}` | Удаление блюда | Admin+ |

---

## 🏗 Структура проекта

```
Cafe_OMS_FastAPI_v3_ai_qwen/
├── app/                        # Backend (FastAPI + SQLAlchemy)
│   ├── main.py                 # Точка входа FastAPI
│   ├── config.py               # Настройки приложения
│   ├── database.py             # SQLAlchemy конфигурация
│   ├── models/                 # SQLAlchemy модели
│   │   ├── user.py             # User (7 уровней)
│   │   ├── order.py            # Order, OrderItem
│   │   └── menu_item.py        # MenuItem
│   ├── schemas/                # Pydantic схемы
│   ├── services/               # Бизнес-логика
│   ├── routers/                # API endpoints
│   └── core/                   # Утилиты (JWT, security)
├── frontend/                   # Frontend (React 19 + TypeScript)
│   ├── src/
│   │   ├── pages/              # Страницы
│   │   ├── components/         # UI компоненты
│   │   └── lib/                # Утилиты (api, store)
│   └── package.json
├── tests/                      # Pytest тесты
├── docker-compose.yml          # Docker Compose конфигурация
├── Dockerfile                  # Backend Docker образ
├── .env                        # Переменные окружения
├── pyproject.toml              # Python зависимости (Poetry)
└── create_test_data.py         # Скрипт тестовых данных
```

---

## 👥 Уровни доступа

| Уровень | Создание | Удаление | Поиск | Редактирование |
|---------|----------|----------|-------|----------------|
| 🟦 Гость (guest) | ❌ | ❌ | ❌ | ❌ |
| 🟦 Клиент (client) | ✅ (себя) | ✅ (себя) | ❌ | ✅ (себя) |
| 🟩 Сотрудник (staff) | ✅ | ❌ | ❌ | ❌ |
| 🟪 Менеджер (manager) | ✅ | ❌ | ✅ | ✅ (ниже себя) |
| 🟥 Администратор (admin) | ✅ | ✅ | ✅ | ✅ (ниже себя) |
| 🟦 Руководитель (director) | ✅ | ✅ | ✅ | ✅ (ниже себя) |
| 🟨 Суперпользователь (superuser) | ✅ | ✅ | ✅ | ✅ (ниже себя) |

> **Важно:** Понизить любого пользователя до уровня "гость" нельзя.

---

## 🧪 Тестовые учётные данные

После запуска `create_test_data.py`:

| Email | Никнейм | Пароль | Уровень |
|-------|---------|--------|---------|
| admin@cafe.ru | admin | admin123 | admin |
| anna@cafe.ru | manager_anna | manager123 | manager |
| igor@cafe.ru | waiter_igor | staff123 | staff |
| john@example.com | john_doe | client123 | client |
| pit_v2@example.com | pit2 | 123456 | client |

**Суперпользователь** (создаётся отдельно):
| Email | Никнейм | Пароль | Уровень |
|-------|---------|--------|---------|
| super_good@cafe.ru | super_good | 12345 | superuser |

---

## 🧪 Тестирование

### Все тесты
```bash
python -m pytest tests/ -v
```

### Отдельные категории
```bash
# Тесты аутентификации
python -m pytest tests/test_auth.py -v

# Тесты пользователей
python -m pytest tests/test_users.py -v

# Тесты заказов
python -m pytest tests/test_orders.py -v

# Интеграционные тесты API
python -m pytest tests/test_all_endpoints_api.py -v

# UI тесты (требуется Playwright)
python -m pytest tests/test_ui_functional.py -v
```

### С покрытием кода
```bash
python -m pytest tests/ -v --cov=app --cov-report=html
```

---

## 🔧 Docker команды

```bash
# Запуск контейнеров
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d

# Остановка
docker-compose down

# Просмотр логов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend

# Выполнить команду в контейнере
docker-compose exec backend poetry run python create_test_data.py --recreate

# Вход в контейнер
docker-compose exec backend bash

# Пересборка без кэша
docker-compose build --no-cache

# Production режим (с nginx)
docker-compose --profile production up -d
```

---

## 🔌 Подключение к PostgreSQL

**Извне (DBeaver, pgAdmin, psql):**
- Host: `localhost`
- Port: `5432`
- Database: `cafe_orders`
- User: `postgres`
- Password: `postgres`

**Из контейнера backend:**
```bash
docker-compose exec backend psql -U postgres -d cafe_orders -h db
```

---

## 📝 Интерфейс
- Окно логина: ![01_login_page.png](test_screenshots/01_login_page.png)
- Окно дашборда: ![04_after_submit.png](test_screenshots/04_after_submit.png)
