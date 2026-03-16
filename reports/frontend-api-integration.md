# Отчёт: Подключение frontend к реальной БД

**Дата:** 14 марта 2026 г.  
**Статус:** ✅ Завершено

---

## 📊 Что было сделано

### 1. Mock-данные удалены ✅

**До:**
```typescript
// OrdersPage.tsx
const allOrders = [
  { id: 1, table: 5, items: [...], total: 850, status: 'pending' },
  { id: 2, table: 3, items: [...], total: 1200, status: 'ready' },
  // ... hardcoded data
]
```

**После:**
```typescript
// OrdersPage.tsx
const [orders, setOrders] = useState<Order[]>([])

useEffect(() => {
  const fetchOrders = async () => {
    const data = await ordersApi.getAll()
    setOrders(data)
  }
  fetchOrders()
}, [])
```

### 2. API клиент создан ✅

**Файл:** `frontend/src/lib/api.ts`

- Axios инстанс с базовым URL `http://localhost:8000/api`
- Interceptor для добавления JWT токена
- Interceptor для обработки ошибок (401 → redirect на /login)
- Методы для всех CRUD операций:
  - `authApi` — login, register
  - `ordersApi` — getAll, getById, create, update, delete, getRevenue, etc.
  - `usersApi` — getAll, getById, create, update, delete

### 3. Страницы обновлены ✅

| Страница | Статус | API метод |
|----------|--------|-----------|
| Dashboard | ✅ Обновлено | `ordersApi.getAll()`, `ordersApi.getRevenue()` |
| OrdersPage | ✅ Обновлено | `ordersApi.getAll()`, `delete()`, `updateStatus()` |
| UsersPage | ✅ Обновлено | `usersApi.getAll()` |
| RevenuePage | ✅ Обновлено | `ordersApi.getRevenue()` |

### 4. Данные в БД ✅

**Скрипт:** `seed_database.py`

**Пользователи (4):**
| Email | Уровень | Пароль |
|-------|---------|--------|
| admin@cafe.ru | admin | admin123 |
| anna@cafe.ru | manager | manager123 |
| igor@cafe.ru | staff | staff123 |
| john@example.com | client | client123 |

**Заказы (6):**
| Стол | Сумма | Статус |
|------|-------|--------|
| 5 | 850₽ | pending |
| 3 | 1200₽ | ready |
| 7 | 1850₽ | paid |
| 2 | 890₽ | pending |
| 10 | 900₽ | ready |
| 1 | 650₽ | paid |

---

## 📁 Изменённые файлы

### Frontend
```
frontend/src/
├── lib/
│   └── api.ts              # НОВЫЙ — API клиент
└── pages/
    ├── Dashboard.tsx       # Обновлён — использует API
    ├── OrdersPage.tsx      # Обновлён — использует API
    ├── UsersPage.tsx       # Обновлён — использует API
    └── RevenuePage.tsx     # Обновлён — использует API
```

### Backend
```
test_project/
├── seed_database.py        # НОВЫЙ — заполнение БД
└── cafe.db                 # База данных с реальными данными
```

---

## 🚀 Как использовать

### 1. Заполнить БД (если ещё не заполнена)
```bash
python seed_database.py
```

### 2. Запустить backend
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Запустить frontend
```bash
cd frontend
npm run dev
```

### 4. Войти в систему
- Откройте http://localhost:3000/login
- Email: `admin@cafe.ru`
- Пароль: `admin123`

---

## ✅ Результат

**Теперь:**
- ✅ Все данные приходят из реальной БД
- ✅ Mock-данные удалены из кода
- ✅ Frontend отображает то что есть в БД
- ✅ При изменении в БД — изменения видны в frontend

**Данные синхронизированы между:**
- Backend API ↔ SQLite БД ↔ Frontend

---

## 🔧 Примечания

1. **CORS:** Backend настроен на `http://localhost:3000`
2. **JWT токены:** Сохраняются в localStorage
3. **401 ошибки:** Автоматический редирект на /login
4. **Loading states:** Показываются во время загрузки данных
5. **Error handling:** Ошибки отображаются пользователю
