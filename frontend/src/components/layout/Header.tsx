import { useState, useEffect } from 'react'
import { Bell, LogOut, User } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { usersApi } from '../../lib/api'

interface CurrentUser {
  id: number
  nickname: string
  name: string
  surname: string
  email: string
  level: string
  status: string
}

const levelLabels: Record<string, string> = {
  guest: 'Гость',
  client: 'Клиент',
  staff: 'Сотрудник',
  manager: 'Менеджер',
  admin: 'Администратор',
  director: 'Руководитель',
  superuser: 'Суперпользователь',
}

export function Header() {
  const navigate = useNavigate()
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchCurrentUser = async () => {
      try {
        setLoading(true)
        const data = await usersApi.getCurrent()
        setCurrentUser(data)
      } catch (error: any) {
        // Если ошибка 401 - пользователь не авторизован
        if (error.response?.status === 401) {
          setCurrentUser(null)
        }
        // В остальных случаях просто показываем null
        setCurrentUser(null)
      } finally {
        setLoading(false)
      }
    }
    fetchCurrentUser()

    // Слушатель события storage для обновления пользователя после логина/логаута
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'token') {
        fetchCurrentUser()
      }
    }
    window.addEventListener('storage', handleStorageChange)

    // Слушатель кастомного события для обновления пользователя
    const handleUserUpdate = () => {
      fetchCurrentUser()
    }
    window.addEventListener('user-updated', handleUserUpdate)

    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('user-updated', handleUserUpdate)
    }
  }, [])

  // Редирект на login если токен был удалён (401 ошибка)
  useEffect(() => {
    if (!loading && !currentUser && window.location.pathname !== '/login') {
      const token = localStorage.getItem('token')
      if (!token) {
        // Проверяем, не гость ли это
        const guestToken = localStorage.getItem('guest_token')
        if (!guestToken) {
          navigate('/login')
        }
      }
    }
  }, [currentUser, loading, navigate])

  const handleLogout = () => {
    localStorage.removeItem('token')
    setCurrentUser(null)
    setLoading(false)
    window.dispatchEvent(new Event('user-updated'))
    navigate('/login')
  }

  const getInitials = () => {
    if (!currentUser) return 'G'
    return (currentUser.name[0] + currentUser.surname[0]).toUpperCase()
  }

  const getDisplayName = () => {
    if (loading) return 'Загрузка...'
    if (!currentUser) return 'Гость'
    return `${currentUser.name} ${currentUser.surname}`
  }

  const getUserLevelLabel = () => {
    if (loading) return ''
    if (!currentUser) return 'Не авторизован'
    return levelLabels[currentUser.level] || currentUser.level
  }

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-8">
      <div className="flex items-center gap-4">
        <h1 className="text-2xl font-bold text-gray-900">
          Добро пожаловать, {loading ? '...' : currentUser ? currentUser.name : 'Гость'}!
        </h1>
      </div>
      <div className="flex items-center gap-4">
        <button
          className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors"
          title="Уведомления"
        >
          <Bell className="w-5 h-5 text-gray-600" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>

        <div className="flex items-center gap-3 pl-4 border-l border-gray-200">
          <div className="text-right">
            <div className="text-sm font-medium text-gray-900">
              {getDisplayName()}
            </div>
            <div className="text-xs text-gray-500">
              {getUserLevelLabel()}
            </div>
          </div>
          <div className="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white font-medium">
            {getInitials()}
          </div>
        </div>

        {!currentUser ? (
          <button
            onClick={() => navigate('/login')}
            className="btn-primary flex items-center gap-2"
          >
            <User className="w-5 h-5" />
            Войти
          </button>
        ) : (
          <button
            onClick={handleLogout}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Выйти"
          >
            <LogOut className="w-5 h-5 text-gray-600" />
          </button>
        )}
      </div>
    </header>
  )
}
