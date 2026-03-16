#!/bin/bash
# Скрипт запуска приложения

# Активация виртуального окружения
source venv/bin/activate  # Для Linux/Mac
# source venv\Scripts\activate  # Для Windows

# Запуск backend
echo "Запуск FastAPI backend..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
