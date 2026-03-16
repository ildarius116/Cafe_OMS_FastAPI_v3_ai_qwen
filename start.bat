@echo off
REM Скрипт запуска приложения для Windows

REM Активация виртуального окружения
call venv\Scripts\activate

REM Запуск backend
echo Запуск FastAPI backend...
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
