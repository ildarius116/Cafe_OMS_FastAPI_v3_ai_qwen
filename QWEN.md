# Project Overview

**Cafe Orders** — полнофункциональное веб-приложение для управления заказами в кафе с аутентификацией пользователей и ролевой моделью доступа.

**Расположение:** `E:\PycharmProjects\AI_webinar\test_project`

---

## 📁 Структура проекта

```
test_project/
├── app/                        # Backend (FastAPI + SQLAlchemy)
│   ├── main.py                 # Точка входа FastAPI
│   ├── config.py               # Настройки приложения
│   ├── database.py             # SQLAlchemy конфигурация (SQLite)
│   ├── seed.py                 # Скрипт заполнения БД тестовыми данными
│   ├── models/                 # SQLAlchemy модели
│   │   ├── user.py             # User модель (7 уровней доступа)
│   │   └── order.py            # Order, OrderItem модели
│   ├── schemas/                # Pydantic схемы валидации
│   │   ├── user.py             # UserCreate, UserUpdate, UserResponse
│   │   └── order.py            # OrderCreate, OrderUpdate, OrderResponse
│   ├── services/               # Бизнес-логика
│   │   ├── user_service.py     # CRUD пользователей + права доступа
│   │   └── order_service.py    # CRUD заказов + расчёт выручки
│   ├── routers/                # API endpoints
│   │   ├── auth.py             # /api/auth/register, /api/auth/login, /api/auth/init-db
│   │   ├── users.py            # /api/users CRUD
│   │   └── orders.py           # /api/orders CRUD + /revenue
│   └── core/                   # Утилиты
│       ├── security.py         # JWT, bcrypt хэширование
│       └── exceptions.py       # AppError, NotFoundError, PermissionError
├── frontend/                   # Frontend (React 19 + TypeScript)
│   ├── src/
│   │   ├── pages/              # Страницы приложения
│   │   ├── components/         # UI компоненты
│   │   ├── lib/api.ts          # API клиент (axios)
│   │   └── App.tsx             # Корневой компонент
│   ├── package.json
│   └── vite.config.ts
├── tests/                      # Pytest тесты
│   ├── conftest.py             # pytest конфигурация
│   ├── test_auth.py            # Тесты аутентификации (8 тестов)
│   ├── test_users.py           # Тесты пользователей (7 тестов)
│   ├── test_orders.py          # Тесты заказов (13 тестов)
│   └── test_all_endpoints.py   # Интеграционные тесты (12 тестов)
├── tasks/                      # Задачи по фазам разработки
├── reports/                    # Отчёты о разработке
├── .qwen/agents/               # AI агенты для разработки
│   ├── ui-designer.md          # Создание UI компонентов
│   ├── code-generator.md       # Генерация backend кода
│   ├── code-reviewer.md        # Проверка кода на ошибки
│   └── test-generator.md       # Создание тестов
├── requirements.txt            # Python зависимости
├── RUN.md                      # Инструкция по запуску
└── test_api.html               # HTML тестовая страница
```

---

## 🛠 Стек технологий

### Backend
| Технология | Версия | Назначение |
|------------|--------|------------|
| Python | 3.14+ | Язык программирования |
| FastAPI | 0.115 | REST API фреймворк |
| SQLAlchemy | 2.0 | ORM для работы с БД |
| Pydantic | 2.7 | Валидация данных |
| python-jose | 3.3 | JWT токены |
| Passlib (bcrypt) | 1.7 | Хэширование паролей |
| SQLite | — | База данных (WAL режим) |

### Frontend
| Технология | Версия | Назначение |
|------------|--------|------------|
| React | 19 | UI библиотека |
| TypeScript | 5.7 | Типизация |
| Tailwind CSS | 3.4 | Стилизация |
| React Router | 7.2 | Роутинг |
| Axios | 1.7 | HTTP клиент |
| Zustand | 5.0 | Управление состоянием |

### Testing
| Технология | Версия | Назначение |
|------------|--------|------------|
| pytest | 8.2 | Тестовый фреймворк |
| pytest-asyncio | 0.23.6 | Асинхронные тесты |
| httpx | 0.27 | TestClient для FastAPI |

---

## 🚀 Запуск проекта

### 1. Установка зависимостей

```bash
# Backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 2. Запуск серверов

**Terminal 1 — Backend:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

### 3. Инициализация БД

**Через Swagger UI (рекомендуется):**
1. Откройте http://localhost:8000/docs
2. Найдите `POST /api/auth/init-db`
3. Нажмите **Try it out** → **Execute**

**Через curl:**
```bash
curl -X POST http://localhost:8000/api/auth/init-db
```

### 4. Доступ к приложению

| Сервис | URL |
|--------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| HTML Test | `test_api.html` (открыть в браузере) |

---

## 🧪 Тестирование

### Все тесты
```bash
python -m pytest tests/ -v
```

### Тесты endpoints (12 тестов)
```bash
python -m pytest tests/test_all_endpoints_api.py -v
# Результат: 9/12 проходят (3 требуют manager+ уровень)
```

### Тесты аутентификации
```bash
python -m pytest tests/test_auth.py -v
# Результат: 8/8 проходят
```

---

## 📋 API Endpoints

### Аутентификация
| Метод | Endpoint | Описание | Auth |
|-------|----------|----------|------|
| POST | `/api/auth/register` | Регистрация нового пользователя | ❌ |
| POST | `/api/auth/login` | Вход (возвращает JWT токен) | ❌ |
| POST | `/api/auth/init-db` | Инициализация БД тестовыми данными | ❌ |

### Пользователи
| Метод | Endpoint | Описание | Auth |
|-------|----------|----------|------|
| GET | `/api/users/me` | Текущий пользователь | ✅ |
| GET | `/api/users` | Список пользователей | Manager+ |
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

---

## 👥 Уровни доступа

| Уровень | Создание | Удаление | Поиск | Редактирование |
|---------|----------|----------|-------|----------------|
| Гость | ❌ | ❌ | ❌ | ❌ |
| Клиент | ✅ (себя) | ✅ (себя) | ❌ | ✅ (себя) |
| Сотрудник | ✅ | ❌ | ❌ | ❌ |
| Менеджер | ✅ | ❌ | ✅ | ✅ (ниже себя) |
| Администратор | ✅ | ✅ | ✅ | ✅ (ниже себя) |
| Руководитель | ✅ | ✅ | ✅ | ✅ (ниже себя) |
| Суперпользователь | ✅ | ✅ | ✅ | ✅ (ниже себя) |

**Важно:** Понизить любого пользователя до уровня "гость" нельзя.

---

## 🔑 Тестовые учётные данные

После инициализации БД (`POST /api/auth/init-db`):

| Email | Никнейм | Пароль | Уровень |
|-------|---------|--------|---------|
| admin@cafe.ru | admin | admin123 | admin |
| anna@cafe.ru | manager_anna | manager123 | manager |
| igor@cafe.ru | waiter_igor | staff123 | staff |
| john@example.com | john_doe | client123 | client |
| pit_v2@example.com | pit2 | 123456 | client |

---

## 📝 Development Conventions

### Код
- **Типизация:** Использовать `typing` для всех функций
- **Docstrings:** Подробные описания функций и классов
- **PEP 8:** Следовать стандартным соглашениям Python
- **Именование:** snake_case для переменных/функций, PascalCase для классов

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

### SQLite на Windows
- **Проблема:** curl/urllib запросы могут блокироваться из-за конкурентного доступа
- **Решение:** Используйте Swagger UI (http://localhost:8000/docs) или pytest тесты
- **HTML тест:** Откройте `test_api.html` в браузере для тестирования API

### Инициализация БД
- Таблицы создаются автоматически при старте uvicorn
- Тестовые данные добавляются через `POST /api/auth/init-db`
- При ошибке блокировки: остановить uvicorn → удалить `cafe.db*` → запустить снова

### AI Агенты
Проект использует 4 специализированных агента в `.qwen/agents/`:
- **ui-designer** — Создание React компонентов
- **code-generator** — Генерация backend кода
- **code-reviewer** — Проверка кода на ошибки
- **test-generator** — Создание pytest тестов

---

## 📚 Дополнительная документация

- `README.md` — Основная документация проекта
- `RUN.md` — Инструкция по запуску
- `project_assignment.md` — Техническое задание
- `reports/` — Отчёты по фазам разработки
- `test_api.html` — HTML страница для тестирования API
