#!/bin/bash
# Скрипт запуска приложения

# Запуск backend через Poetry
echo "Запуск FastAPI backend..."
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
