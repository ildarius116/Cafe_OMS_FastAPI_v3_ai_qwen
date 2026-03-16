# API Integration Plan

## Base URL
```typescript
const API_BASE_URL = 'http://localhost:8000/api'
```

## Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login (returns JWT) |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | Get all users (Manager+) |
| GET | `/users/me` | Get current user |
| GET | `/users/{id}` | Get user by ID |
| POST | `/users` | Create user (Admin+) |
| PUT | `/users/{id}` | Update user (Admin+) |
| DELETE | `/users/{id}` | Delete user (Admin+) |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/orders` | Get all orders |
| GET | `/orders/active` | Get active orders |
| GET | `/orders/revenue` | Get revenue stats (Manager+) |
| GET | `/orders/{id}` | Get order by ID |
| POST | `/orders` | Create new order |
| PUT | `/orders/{id}` | Update order |
| PATCH | `/orders/{id}/status` | Update order status |
| DELETE | `/orders/{id}` | Delete order (Manager+) |
| GET | `/orders/table/{number}` | Get orders by table |

## TypeScript Types

```typescript
// User types
interface User {
  id: number
  nickname: string
  name: string
  surname: string
  email: string
  level: 'guest' | 'client' | 'staff' | 'manager' | 'admin' | 'director' | 'superuser'
  status: 'active' | 'inactive'
  created_at: string
  updated_at: string
}

interface UserCreate {
  nickname: string
  name: string
  surname: string
  email: string
  password: string
}

interface UserUpdate {
  nickname?: string
  name?: string
  surname?: string
  email?: string
  level?: UserLevel
  status?: UserStatus
}

interface LoginRequest {
  username: string  // email
  password: string
}

interface TokenResponse {
  access_token: string
  token_type: 'bearer'
}

// Order types
interface Order {
  id: number
  table_number: number
  items: OrderItem[]
  total_price: number
  status: 'pending' | 'ready' | 'paid'
  user_id?: number
  created_at: string
  updated_at: string
}

interface OrderItem {
  name: string
  price: number
  quantity: number
}

interface OrderCreate {
  table_number: number
  items: OrderItem[]
}

interface OrderUpdate {
  table_number?: number
  items?: OrderItem[]
  status?: OrderStatus
}

interface OrderRevenue {
  total_revenue: number
  orders_count: number
  period_start?: string
  period_end?: string
}
```

## API Client (axios)

```typescript
// src/lib/api.ts
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for adding token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: async (email: string, password: string): Promise<TokenResponse> => {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)
    
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return response.data
  },
  
  register: async (data: UserCreate): Promise<User> => {
    const response = await api.post('/auth/register', data)
    return response.data
  },
}

// Users API
export const usersApi = {
  getCurrent: (): Promise<User> => api.get('/users/me').then(r => r.data),
  getAll: (params?: { skip?: number; limit?: number; search?: string }): Promise<User[]> => 
    api.get('/users', { params }).then(r => r.data),
  getById: (id: number): Promise<User> => api.get(`/users/${id}`).then(r => r.data),
  create: (data: UserCreate): Promise<User> => api.post('/users', data).then(r => r.data),
  update: (id: number, data: UserUpdate): Promise<User> => api.put(`/users/${id}`, data).then(r => r.data),
  delete: (id: number): Promise<void> => api.delete(`/users/${id}`).then(() => {}),
}

// Orders API
export const ordersApi = {
  getAll: (params?: { skip?: number; limit?: number; table_number?: number; status?: string }): Promise<Order[]> =>
    api.get('/orders', { params }).then(r => r.data),
  getById: (id: number): Promise<Order> => api.get(`/orders/${id}`).then(r => r.data),
  create: (data: OrderCreate): Promise<Order> => api.post('/orders', data).then(r => r.data),
  update: (id: number, data: OrderUpdate): Promise<Order> => api.put(`/orders/${id}`, data).then(r => r.data),
  updateStatus: (id: number, status: OrderStatus): Promise<Order> => 
    api.patch(`/orders/${id}/status`, { status }).then(r => r.data),
  delete: (id: number): Promise<void> => api.delete(`/orders/${id}`).then(() => {}),
  getRevenue: (params?: { start_date?: string; end_date?: string }): Promise<OrderRevenue> =>
    api.get('/orders/revenue', { params }).then(r => r.data),
  getActive: (): Promise<Order[]> => api.get('/orders/active').then(r => r.data),
}
```

## Zustand Stores

```typescript
// src/stores/authStore.ts
import { create } from 'zustand'
import { authApi, usersApi } from '../lib/api'
import type { User, TokenResponse } from '../types'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  
  login: (email: string, password: string) => Promise<void>
  register: (data: UserCreate) => Promise<void>
  logout: () => void
  getUser: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  isLoading: false,
  error: null,
  
  login: async (email, password) => {
    set({ isLoading: true, error: null })
    try {
      const data: TokenResponse = await authApi.login(email, password)
      localStorage.setItem('token', data.access_token)
      set({ token: data.access_token, isAuthenticated: true })
      
      const user = await usersApi.getCurrent()
      set({ user, isLoading: false })
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Ошибка входа',
        isLoading: false
      })
      throw error
    }
  },
  
  register: async (data) => {
    set({ isLoading: true, error: null })
    try {
      await authApi.register(data)
      set({ isLoading: false })
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Ошибка регистрации',
        isLoading: false
      })
      throw error
    }
  },
  
  logout: () => {
    localStorage.removeItem('token')
    set({ user: null, token: null, isAuthenticated: false })
  },
  
  getUser: async () => {
    try {
      const user = await usersApi.getCurrent()
      set({ user })
    } catch (error) {
      set({ user: null })
    }
  },
  
  clearError: () => set({ error: null }),
}))
```

```typescript
// src/stores/ordersStore.ts
import { create } from 'zustand'
import { ordersApi } from '../lib/api'
import type { Order, OrderCreate, OrderUpdate, OrderStatus, OrderRevenue } from '../types'

interface OrdersState {
  orders: Order[]
  revenue: OrderRevenue | null
  isLoading: boolean
  error: string | null
  
  fetchOrders: (params?: any) => Promise<void>
  fetchRevenue: (params?: any) => Promise<void>
  createOrder: (data: OrderCreate) => Promise<Order>
  updateOrder: (id: number, data: OrderUpdate) => Promise<Order>
  updateStatus: (id: number, status: OrderStatus) => Promise<Order>
  deleteOrder: (id: number) => Promise<void>
  clearError: () => void
}

export const useOrdersStore = create<OrdersState>((set) => ({
  orders: [],
  revenue: null,
  isLoading: false,
  error: null,
  
  fetchOrders: async (params) => {
    set({ isLoading: true, error: null })
    try {
      const orders = await ordersApi.getAll(params)
      set({ orders, isLoading: false })
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Ошибка загрузки заказов',
        isLoading: false
      })
    }
  },
  
  fetchRevenue: async (params) => {
    set({ isLoading: true, error: null })
    try {
      const revenue = await ordersApi.getRevenue(params)
      set({ revenue, isLoading: false })
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Ошибка загрузки выручки',
        isLoading: false
      })
    }
  },
  
  createOrder: async (data) => {
    const order = await ordersApi.create(data)
    set((state) => ({ orders: [order, ...state.orders] }))
    return order
  },
  
  updateOrder: async (id, data) => {
    const order = await ordersApi.update(id, data)
    set((state) => ({
      orders: state.orders.map(o => o.id === id ? order : o)
    }))
    return order
  },
  
  updateStatus: async (id, status) => {
    const order = await ordersApi.updateStatus(id, status)
    set((state) => ({
      orders: state.orders.map(o => o.id === id ? order : o)
    }))
    return order
  },
  
  deleteOrder: async (id) => {
    await ordersApi.delete(id)
    set((state) => ({
      orders: state.orders.filter(o => o.id !== id)
    }))
  },
  
  clearError: () => set({ error: null }),
}))
```

## Integration Steps

1. **Setup API client** — create `src/lib/api.ts`
2. **Create stores** — auth, orders, users
3. **Update LoginPage** — connect to auth store
4. **Update Dashboard** — fetch real stats
5. **Update OrdersPage** — connect to orders store
6. **Update UsersPage** — connect to users store
7. **Add loading states** — spinners during API calls
8. **Add toast notifications** — success/error messages
