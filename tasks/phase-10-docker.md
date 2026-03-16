# ФАЗА 10: Контейнеризация

## Цель
Упаковать приложение в Docker контейнеры для production развёртывания.

## Задачи

### 10.1. Подготовка к контейнеризации
- [ ] Переход на PostgreSQL
  - [ ] Обновление config.py для поддержки PostgreSQL
  - [ ] Создание .env с DATABASE_URL для PostgreSQL
- [ ] Вынос секретов в переменные окружения
- [ ] Настройка logging

### 10.2. Dockerfile для backend
- [ ] Создать Dockerfile
  - [ ] Python 3.14 slim image
  - [ ] Установка зависимостей
  - [ ] Копирование кода
  - [ ] CMD для uvicorn
- [ ] .dockerignore для backend

### 10.3. Dockerfile для frontend
- [ ] Создать Dockerfile
  - [ ] Node image для сборки
  - [ ] Multi-stage build
  - [ ] Nginx для раздачи статики
- [ ] .dockerignore для frontend

### 10.4. Docker Compose
- [ ] Создать docker-compose.yml
  - [ ] backend service
  - [ ] frontend service
  - [ ] postgres service
  - [ ] pgadmin service (опционально)
- [ ] Настройка network
- [ ] Настройка volumes для БД

### 10.5. Миграции БД
- [ ] Настройка Alembic
- [ ] Создание initial migration
- [ ] Авто-применение миграций при старте

### 10.6. Тестирование
- [ ] Запуск docker-compose up
- [ ] Проверка backend API
- [ ] Проверка frontend
- [ ] Проверка подключения к БД
- [ ] End-to-end тестирование

## Ожидаемый результат
- Рабочее приложение в Docker
- PostgreSQL база данных
- Одна команда для запуска: docker-compose up
- Готово к production развёртыванию

## Файлы
```
docker-compose.yml
backend/Dockerfile
backend/.dockerignore
frontend/Dockerfile
frontend/.dockerignore
```

## Пример docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: cafe_orders
      POSTGRES_USER: cafe_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://cafe_user:secure_password@db:5432/cafe_orders
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - db
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    depends_on:
      - backend
    ports:
      - "3000:80"

volumes:
  postgres_data:
```
