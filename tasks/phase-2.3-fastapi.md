# ФАЗА 2.3: Базовая конфигурация FastAPI

## Цель
Настроить базовое приложение FastAPI с CORS и health-check endpoint.

## Задачи

### 1. Создание main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Cafe Orders API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

### 2. Создание .env файла
```
DATABASE_URL=sqlite:///./cafe.db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Настройка logging
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### 4. Тестирование
```bash
uvicorn app.main:app --reload
curl http://localhost:8000/health
```

## Ожидаемый результат
- Запускаемое FastAPI приложение
- CORS настроен для frontend
- Health-check endpoint работает
