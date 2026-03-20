# Cafe Orders — Система управления заказами в кафе

**Полнофункциональное веб-приложение** для управления заказами и пользователями в кафе с аутентификацией, ролевой моделью доступа и полным CRUD.

**Расположение:** `E:\PycharmProjects\Cafe_OMS_FastAPI_v3_ai_qwen`

**База данных:** PostgreSQL (внешняя, вне Docker)

**Контейнеризация:** Docker + Docker Compose

---

## 📁 Структура проекта

```
Cafe_OMS_FastAPI_v3_ai_qwen/
├── app/                        # Backend (FastAPI + SQLAlchemy)
│   ├── main.py                 # Точка входа FastAPI
│   ├── config.py               # Настройки приложения (pydantic-settings)
│   ├── database.py             # SQLAlchemy конфигурация (PostgreSQL/SQLite)
│   ├── seed.py                 # Скрипт заполнения БД
│   ├── models/                 # SQLAlchemy модели
│   │   ├── user.py             # User (7 уровней: guest→superuser)
│   │   ├── order.py            # Order, OrderItem (many-to-many)
│   │   └── menu_item.py        # MenuItem (меню блюд)
│   ├── schemas/                # Pydantic схемы валидации
│   │   ├── user.py             # UserCreate, UserUpdate, UserResponse
│   │   ├── order.py            # OrderCreate, OrderUpdate, OrderResponse
│   │   └── menu_item.py        # MenuItem schemas
│   ├── services/               # Бизнес-логика
│   │   ├── user_service.py     # CRUD пользователей + права доступа
│   │   ├── order_service.py    # CRUD заказов + расчёт выручки
│   │   └── menu_item_service.py# CRUD меню
│   ├── routers/                # API endpoints
│   │   ├── auth.py             # /api/auth/register, /login
│   │   ├── users.py            # /api/users CRUD
│   │   ├── orders.py           # /api/orders CRUD + /revenue
│   │   └── menu_items.py       # /api/menu-items CRUD
│   └── core/                   # Утилиты
│       ├── security.py         # JWT, bcrypt хэширование
│       └── exceptions.py       # AppError, NotFoundError, PermissionError
├── frontend/                   # Frontend (React 19 + TypeScript)
│   ├── src/
│   │   ├── pages/              # Страницы приложения
│   │   │   ├── Dashboard.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   ├── OrdersPage.tsx
│   │   │   ├── UsersPage.tsx
│   │   │   ├── ProfilePage.tsx
│   │   │   └── RevenuePage.tsx
│   │   ├── components/         # UI компоненты
│   │   │   └── layout/         # Sidebar, Header
│   │   ├── lib/                # Утилиты (api клиент, store)
│   │   ├── App.tsx             # Корневой компонент
│   │   └── main.tsx            # Entry point
│   ├── package.json
│   └── vite.config.ts
├── tests/                      # Pytest тесты
│   ├── conftest.py             # pytest конфигурация, фикстуры
│   ├── test_auth.py            # Тесты аутентификации
│   ├── test_users.py           # Тесты пользователей
│   ├── test_orders.py          # Тесты заказов
│   ├── test_orders_many_to_many.py  # Тесты many-to-many связей
│   ├── test_all_endpoints_api.py    # Интеграционные тесты API
│   ├── test_all_endpoints_web.py    # Web тесты
│   └── test_ui_functional.py   # UI функциональные тесты
├── tasks/                      # Задачи по фазам разработки
├── reports/                    # Отчёты о разработке
├── test_screenshots/           # Скриншоты тестов
├── .qwen/                      # Конфигурация Qwen Code
│   ├── agents/                 # AI агенты
│   └── skills/                 # Скиллы
├── .env.example                # Шаблон переменных окружения
├── .dockerignore               # Исключения для Docker
├── pyproject.toml              # Python зависимости (Poetry)
├── poetry.lock                 # Заблокированные версии зависимостей
├── pytest.ini                  # Pytest конфигурация
├── Dockerfile                  # Docker образ backend
├── docker-compose.yml          # Docker Compose конфигурация
├── nginx.conf                  # Nginx конфигурация (reverse proxy)
├── create_superuser.py         # Скрипт создания суперпользователя
├── create_test_data.py         # Скрипт тестовых данных
├── start.bat                   # Скрипт запуска (Windows)
└── start.sh                    # Скрипт запуска (Linux/Mac)
```

---

## 🛠 Стек технологий

### Backend
| Технология | Версия | Назначение |
|------------|--------|------------|
| Python | 3.14+ | Язык программирования |
| FastAPI | 0.115 | REST API фреймворк |
| SQLAlchemy | 2.0 | ORM для работы с БД |
| Pydantic | 2.9 | Валидация данных |
| Pydantic Settings | 2.6 | Управление настройками |
| Alembic | 1.13 | Миграции БД |
| python-jose | 3.3 | JWT токены |
| bcrypt | 5.0 | Хэширование паролей |
| PostgreSQL | 15+ | Основная БД |
| psycopg2-binary | 2.9 | PostgreSQL драйвер |
| Poetry | 2.3 | Менеджер зависимостей |
| Docker | 20+ | Контейнеризация |

### Frontend
| Технология | Версия | Назначение |
|------------|--------|------------|
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

### Testing
| Технология | Версия | Назначение |
|------------|--------|------------|
| pytest | 8.2 | Тестовый фреймворк |
| pytest-asyncio | 0.23.6 | Асинхронные тесты |
| pytest-cov | 5.0 | Покрытие кода |
| httpx | 0.27 | TestClient для FastAPI |
| playwright | 1.40 | E2E браузерные тесты |

---

## 🚀 Запуск проекта

### Вариант 1: Docker Compose (рекомендуется)

**Требования:**
- Docker Desktop (Windows/Mac) или Docker + Docker Compose (Linux)

**1. Быстрая инициализация:**

Windows:
```bash
init.bat
```

Linux/Mac:
```bash
bash init.sh
```

**2. Ручной запуск:**

```bash
# Запуск всех сервисов (backend, frontend, PostgreSQL)
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d

# Запуск с nginx (production режим)
docker-compose --profile production up -d
```

**3. Создание тестовых данных:**
```bash
# Выполнить скрипт в контейнере
docker-compose exec backend poetry run python create_test_data.py --recreate
```

**4. Остановка:**
```bash
docker-compose down

# Полная очистка (включая данные БД)
docker-compose down -v
```

### Вариант 2: Локальная разработка (Poetry)

**1. Установка зависимостей:**
```bash
# Установка Poetry (если не установлен)
pip install poetry

# Установка зависимостей
poetry install
```

**2. Настройка PostgreSQL:**
```bash
# Скопируйте .env.example в .env
cp .env.example .env

# Отредактируйте DATABASE_URL в .env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/cafe_orders
```

**3. Создание тестовых данных:**
```bash
poetry run python create_test_data.py --recreate
```

**4. Запуск серверов:**

Terminal 1 — Backend:
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 — Frontend:
```bash
cd frontend
npm run dev
```

### 5. Доступ к приложению

| Сервис | URL |
|--------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |
| Nginx (production) | http://localhost:8080 |
| PostgreSQL | localhost:5432 |

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

## 🔐 Переменные окружения

**По умолчанию (для Docker Compose):**
```bash
# Database (PostgreSQL)
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db  # имя сервиса в docker-compose.yml
DB_PORT=5432
DB_NAME=cafe_orders

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
FRONTEND_URLS=http://localhost:3000,http://localhost:5173,http://localhost:8080
```

**Для локальной разработки:**
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/cafe_orders
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URLS=http://localhost:3000,http://localhost:5173,http://localhost:8080
```

---

## 📦 Poetry команды

```bash
# Запустить команду в окружении Poetry
poetry run <command>

# Войти в оболочку Poetry
poetry shell

# Показать путь к виртуальному окружению
poetry env info

# Добавить новую зависимость
poetry add <package>

# Добавить dev-зависимость
poetry add --group dev <package>

# Установить все зависимости
poetry install

# Обновить зависимости
poetry update
```

---

## 🐳 Docker команды

```bash
# Запуск контейнеров
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d

# Остановка контейнеров
docker-compose down

# Просмотр логов
docker-compose logs -f

# Просмотр логов конкретного сервиса
docker-compose logs -f backend

# Выполнить команду в контейнере
docker-compose exec backend <command>

# Пример: создание тестовых данных
docker-compose exec backend poetry run python create_test_data.py --recreate

# Пример: вход в контейнер
docker-compose exec backend bash

# Пересборка без кэша
docker-compose build --no-cache

# Запуск только backend
docker-compose up backend

# Запуск только frontend
docker-compose up frontend

# Production режим (с nginx)
docker-compose --profile production up -d
```

---

## 📋 API Endpoints

### Аутентификация
| Метод | Endpoint | Описание | Auth |
|-------|----------|----------|------|
| POST | `/api/auth/register` | Регистрация нового пользователя | ❌ |
| POST | `/api/auth/login` | Вход (возвращает JWT токен) | ❌ |

### Пользователи
| Метод | Endpoint | Описание | Auth |
|-------|----------|----------|------|
| GET | `/api/users/me` | Текущий пользователь | ✅ |
| GET | `/api/users` | Список пользователей (с фильтрами) | Manager+ |
| GET | `/api/users/{id}` | Пользователь по ID | ✅ |
| POST | `/api/users` | Создание пользователя | Admin+ |
| PUT | `/api/users/{id}` | Обновление пользователя | Admin+ |
| DELETE | `/api/users/{id}` | Удаление пользователя | Admin+ |

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

### Меню
| Метод | Endpoint | Описание | Auth |
|-------|----------|----------|------|
| GET | `/api/menu-items` | Список блюд меню | ❌ |
| GET | `/api/menu-items/{id}` | Блюдо по ID | ❌ |
| POST | `/api/menu-items` | Добавление блюда | Admin+ |
| PUT | `/api/menu-items/{id}` | Обновление блюда | Admin+ |
| DELETE | `/api/menu-items/{id}` | Удаление блюда | Admin+ |

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

**Важно:** Понизить любого пользователя до уровня "гость" нельзя.

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

**Суперпользователь** (создаётся отдельно через `create_superuser.py`):
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

# Тесты many-to-many связей
python -m pytest tests/test_orders_many_to_many.py -v

# Интеграционные тесты API
python -m pytest tests/test_all_endpoints_api.py -v

# UI функциональные тесты (требуется Playwright)
python -m pytest tests/test_ui_functional.py -v
```

### С покрытием кода
```bash
python -m pytest tests/ -v --cov=app --cov-report=html
```

---

## 📝 Development Conventions

### Код
- **Типизация:** Использовать `typing` для всех функций
- **Docstrings:** Подробные описания функций и классов (Google style)
- **PEP 8:** Следовать стандартным соглашениям Python
- **Именование:** 
  - `snake_case` для переменных/функций
  - `PascalCase` для классов
  - `UPPER_CASE` для констант

### Frontend
- **Компоненты:** Функциональные компоненты с хуками
- **Стили:** Tailwind CSS утилитарные классы
- **Состояние:** Zustand store для глобального состояния
- **Формы:** React Hook Form + Zod валидация

### Тесты
- **Именование:** `test_*.py` файлы, `test_*` функции
- **Фикстуры:** Использовать pytest фикстуры для изоляции
- **Ассерты:** Проверять статусы, структуры ответов, ошибки

### База данных
- **WAL режим:** Включён для SQLite (конкурентный доступ)
- **busy_timeout:** 60 секунд ожидания
- **Сессии:** Каждая запрос создаёт новую сессию

---

## ⚠️ Важные примечания

### База данных PostgreSQL

**Данные сохраняются в Docker volume:**
- `postgres_data` — именованный том для данных PostgreSQL
- Данные сохраняются между перезапусками контейнеров

**Для полного сброса БД:**
```bash
docker-compose down -v  # удалит том с данными
docker-compose up --build
docker-compose exec backend poetry run python create_test_data.py --recreate
```

### Инициализация БД
- Таблицы создаются автоматически при старте uvicorn
- Тестовые данные добавляются через `create_test_data.py`
- Скрипт `create_superuser.py` создаёт суперпользователя

### AI Агенты и Скиллы
Проект использует AI агентов и скиллы в `.qwen/`:
- **Агенты:** Для создания кода, ревью, тестов
- **Скиллы:** Для специализированных задач

---

## 📚 Дополнительная документация

- `README.md` — Основная документация проекта
- `project_assignment.md` — Техническое задание
- `reports/` — Отчёты по фазам разработки
- `tasks/` — Задачи по разработке
- `test_screenshots/` — Скриншоты UI тестов
