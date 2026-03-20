@echo off
REM Скрипт запуска приложения для Windows

REM Запуск backend через Poetry
echo Запуск FastAPI backend...
python -m poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
