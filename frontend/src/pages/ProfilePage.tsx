import { useState, useEffect } from 'react'
import { User, Mail, Shield, Calendar, Edit2, Trash2 } from 'lucide-react'
import { usersApi } from '../lib/api'

interface User {
  id: number
  nickname: string
  name: string
  surname: string
  email: string
  level: string
  status: string
  created_at: string
}

export default function ProfilePage() {
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchUser = async () => {
      try {
        setLoading(true)
        const data = await usersApi.getCurrent()
        setCurrentUser(data)
        setError(null)
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Ошибка загрузки профиля')
      } finally {
        setLoading(false)
      }
    }
    fetchUser()
  }, [])

  const levelLabels: Record<string, string> = {
    guest: 'Гость',
    client: 'Клиент',
    staff: 'Сотрудник',
    manager: 'Менеджер',
    admin: 'Администратор',
    director: 'Руководитель',
    superuser: 'Суперпользователь',
  }

  const statusLabels: Record<string, string> = {
    active: 'Активен',
    inactive: 'Неактивен',
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Загрузка профиля...</div>
      </div>
    )
  }

  if (error || !currentUser) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-500">Ошибка: {error || 'Пользователь не найден'}</div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Профиль</h2>
        <p className="text-gray-600 mt-1">Управление личными данными</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Карточка профиля */}
        <div className="card lg:col-span-1">
          <div className="text-center">
            <div className="w-24 h-24 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white text-3xl font-bold mx-auto mb-4">
              {currentUser.name[0]}{currentUser.surname[0]}
            </div>
            <h3 className="text-xl font-semibold text-gray-900">{currentUser.name} {currentUser.surname}</h3>
            <p className="text-gray-500">@{currentUser.nickname}</p>

            <div className="mt-4 flex flex-wrap gap-2 justify-center">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                <Shield className="w-3 h-3 mr-1" />
                {levelLabels[currentUser.level]}
              </span>
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                {statusLabels[currentUser.status]}
              </span>
            </div>

            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
                <Calendar className="w-4 h-4" />
                Регистрация: {new Date(currentUser.created_at).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })}
              </div>
            </div>
          </div>
        </div>

        {/* Информация и настройки */}
        <div className="lg:col-span-2 space-y-6">
          {/* Личные данные */}
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Личные данные</h3>
              <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                <Edit2 className="w-4 h-4 text-gray-600" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-500 mb-1">Никнейм</label>
                <div className="flex items-center gap-2 text-gray-900">
                  <User className="w-5 h-5 text-gray-400" />
                  <span>{currentUser.nickname}</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">Имя</label>
                  <p className="text-gray-900">{currentUser.name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">Фамилия</label>
                  <p className="text-gray-900">{currentUser.surname}</p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-500 mb-1">Email</label>
                <div className="flex items-center gap-2 text-gray-900">
                  <Mail className="w-5 h-5 text-gray-400" />
                  <span>{currentUser.email}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Смена пароля */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Смена пароля</h3>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Текущий пароль</label>
                <input type="password" className="input-field" placeholder="••••••••" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Новый пароль</label>
                <input type="password" className="input-field" placeholder="••••••••" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Подтверждение пароля</label>
                <input type="password" className="input-field" placeholder="••••••••" />
              </div>
              <button type="submit" className="btn-primary">
                Изменить пароль
              </button>
            </form>
          </div>

          {/* Опасная зона */}
          <div className="card border-red-200">
            <h3 className="text-lg font-semibold text-red-600 mb-4">Опасная зона</h3>
            <p className="text-sm text-gray-600 mb-4">
              После удаления аккаунта все данные будут безвозвратно удалены. Это действие нельзя отменить.
            </p>
            <button className="btn-secondary flex items-center gap-2 text-red-600 hover:bg-red-50">
              <Trash2 className="w-4 h-4" />
              Удалить аккаунт
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
