@echo off
REM Скрипт инициализации проекта Cafe Orders для Windows
REM Автоматическая установка зависимостей и создание тестовых данных

echo 🚀 Инициализация проекта Cafe Orders...

REM Проверка наличия Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker не найден. Установите Docker Desktop.
    exit /b 1
)

where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker Compose не найден.
    exit /b 1
)

echo ✅ Docker найден

REM Проверка наличия Poetry
where poetry >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ Poetry не найден. Установка...
    pip install poetry
)

echo ✅ Poetry найден

REM Проверка наличия Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js не найден. Установите Node.js 20+.
    exit /b 1
)

echo ✅ Node.js найден

REM Копирование .env если не существует
if not exist .env (
    echo 📋 Копирование .env.example в .env...
    copy .env.example .env
)

REM Остановка старых контейнеров
echo 🛑 Остановка старых контейнеров...
docker-compose down 2>nul || true

REM Запуск контейнеров
echo 🐳 Запуск Docker контейнеров...
docker-compose up -d --build

REM Ожидание готовности БД
echo ⏳ Ожидание готовности PostgreSQL...
timeout /t 10 /nobreak >nul

REM Создание тестовых данных
echo 📊 Создание тестовых данных...
docker-compose exec backend poetry run python create_test_data.py --recreate

echo.
echo ✅ Инициализация завершена!
echo.
echo 📍 Доступ к приложению:
echo    Frontend:  http://localhost:5173
echo    Backend:   http://localhost:8000
echo    Swagger:   http://localhost:8000/docs
echo    PostgreSQL: localhost:5432
echo.
echo 🔑 Тестовые учётные данные:
echo    admin@cafe.ru / admin123 (admin)
echo    anna@cafe.ru / manager123 (manager)
echo    john@example.com / client123 (client)
echo.

pause
