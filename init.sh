#!/bin/bash

# Скрипт инициализации проекта Cafe Orders
# Автоматическая установка зависимостей и создание тестовых данных

set -e

echo "🚀 Инициализация проекта Cafe Orders..."

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не найден. Установите Docker Desktop."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не найден."
    exit 1
fi

echo "✅ Docker найден"

# Проверка наличия Poetry
if ! command -v poetry &> /dev/null; then
    echo "⚠️ Poetry не найден. Установка..."
    pip install poetry
fi

echo "✅ Poetry найден"

# Проверка наличия Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js не найден. Установите Node.js 20+."
    exit 1
fi

echo "✅ Node.js найден"

# Копирование .env если не существует
if [ ! -f .env ]; then
    echo "📋 Копирование .env.example в .env..."
    cp .env.example .env
fi

# Остановка старых контейнеров
echo "🛑 Остановка старых контейнеров..."
docker-compose down 2>/dev/null || true

# Запуск контейнеров
echo "🐳 Запуск Docker контейнеров..."
docker-compose up -d --build

# Ожидание готовности БД
echo "⏳ Ожидание готовности PostgreSQL..."
sleep 10

# Создание тестовых данных
echo "📊 Создание тестовых данных..."
docker-compose exec backend poetry run python create_test_data.py --recreate

echo ""
echo "✅ Инициализация завершена!"
echo ""
echo "📍 Доступ к приложению:"
echo "   Frontend:  http://localhost:5173"
echo "   Backend:   http://localhost:8000"
echo "   Swagger:   http://localhost:8000/docs"
echo "   PostgreSQL: localhost:5432"
echo ""
echo "🔑 Тестовые учётные данные:"
echo "   admin@cafe.ru / admin123 (admin)"
echo "   anna@cafe.ru / manager123 (manager)"
echo "   john@example.com / client123 (client)"
echo ""
