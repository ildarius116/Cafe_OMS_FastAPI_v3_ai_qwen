import { useState, useEffect } from 'react'
import { Search, Plus, Filter, MoreVertical, Mail, Trash2, Edit, X } from 'lucide-react'
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

const levelColors: Record<string, string> = {
  guest: 'bg-gray-100 text-gray-800',
  client: 'bg-blue-100 text-blue-800',
  staff: 'bg-green-100 text-green-800',
  manager: 'bg-purple-100 text-purple-800',
  admin: 'bg-red-100 text-red-800',
  director: 'bg-indigo-100 text-indigo-800',
  superuser: 'bg-amber-100 text-amber-800',
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

const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-red-100 text-red-800',
}

const statusLabels: Record<string, string> = {
  active: 'Активен',
  inactive: 'Неактивен',
}

const levelOptions = [
  { value: 'guest', label: 'Гость' },
  { value: 'client', label: 'Клиент' },
  { value: 'staff', label: 'Сотрудник' },
  { value: 'manager', label: 'Менеджер' },
  { value: 'admin', label: 'Администратор' },
  { value: 'director', label: 'Руководитель' },
  { value: 'superuser', label: 'Суперпользователь' },
]

const emptyUser: Omit<User, 'id' | 'created_at'> & { password: string } = {
  nickname: '',
  name: '',
  surname: '',
  email: '',
  password: '',
  level: 'client',
  status: 'active',
}

const emptyEditUser: Omit<User, 'id' | 'created_at'> = {
  nickname: '',
  name: '',
  surname: '',
  email: '',
  level: 'client',
  status: 'active',
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [levelFilter, setLevelFilter] = useState<string>('all')

  // Модальные окна
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showActionMenu, setShowActionMenu] = useState<number | null>(null)
  const [selectedUser, setSelectedUser] = useState<User | null>(null)

  // Формы
  const [newUser, setNewUser] = useState(emptyUser)
  const [editUser, setEditUser] = useState(emptyEditUser)
  const [formLoading, setFormLoading] = useState(false)

  // Debounce для поиска
  const [debouncedSearch, setDebouncedSearch] = useState('')

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search)
    }, 500) // 500ms задержка для поиска чтобы не терять фокус

    return () => clearTimeout(timer)
  }, [search])

  useEffect(() => {
    fetchUsers()
  }, [debouncedSearch, levelFilter])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      // Передаём search и levelFilter на сервер для фильтрации
      const params: any = { limit: 1000 } // Увеличиваем лимит для поиска
      if (debouncedSearch) {
        params.search = debouncedSearch
      }
      if (levelFilter !== 'all') {
        params.level = levelFilter
      }
      const data = await usersApi.getAll(params)
      setUsers(data)
      setError(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки пользователей')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateUser = async () => {
    try {
      setFormLoading(true)
      await usersApi.create(newUser)
      await fetchUsers()
      setShowCreateModal(false)
      setNewUser(emptyUser)
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка создания пользователя')
    } finally {
      setFormLoading(false)
    }
  }

  const handleEditUser = async () => {
    if (!selectedUser) return
    try {
      setFormLoading(true)
      await usersApi.update(selectedUser.id, editUser)
      await fetchUsers()
      setShowEditModal(false)
      setSelectedUser(null)
      setEditUser(emptyUser)
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка обновления пользователя')
    } finally {
      setFormLoading(false)
    }
  }

  const handleDeleteUser = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить этого пользователя?')) return
    try {
      await usersApi.delete(id)
      setUsers(users.filter(u => u.id !== id))
      setShowActionMenu(null)
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка удаления пользователя')
    }
  }

  const openEditModal = (user: User) => {
    setSelectedUser(user)
    setEditUser({
      nickname: user.nickname,
      name: user.name,
      surname: user.surname,
      email: user.email,
      level: user.level,
      status: user.status,
    })
    setShowEditModal(true)
    setShowActionMenu(null)
  }

  // Фильтрация на клиенте больше не нужна - поиск выполняется на сервере
  const filteredUsers = users

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Загрузка пользователей...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-500">Ошибка: {error}</div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Пользователи</h2>
          <p className="text-gray-600 mt-1">Управление пользователями системы</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Добавить пользователя
        </button>
      </div>

      {/* Фильтры и поиск */}
      <div className="card mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              className="input-field pl-10"
              placeholder="Поиск по имени, фамилии, email или ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              className="input-field"
              value={levelFilter}
              onChange={(e) => setLevelFilter(e.target.value)}
            >
              <option value="all">Все уровни</option>
              <option value="guest">Гость</option>
              <option value="client">Клиент</option>
              <option value="staff">Сотрудник</option>
              <option value="manager">Менеджер</option>
              <option value="admin">Администратор</option>
              <option value="director">Руководитель</option>
              <option value="superuser">Суперпользователь</option>
            </select>
          </div>
        </div>
      </div>

      {/* Таблица пользователей */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">ID</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Пользователь</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Email</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Уровень</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Статус</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Действия</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map((user) => (
                <tr key={user.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 text-sm font-medium text-gray-900">#{user.id}</td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white font-medium">
                        {user.name[0]}{user.surname[0]}
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{user.name} {user.surname}</div>
                        <div className="text-sm text-gray-500">@{user.nickname}</div>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Mail className="w-4 h-4 text-gray-400" />
                      {user.email}
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${levelColors[user.level]}`}>
                      {levelLabels[user.level]}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[user.status]}`}>
                      {statusLabels[user.status]}
                    </span>
                  </td>
                  <td className="py-3 px-4 relative">
                    <button
                      onClick={() => setShowActionMenu(showActionMenu === user.id ? null : user.id)}
                      className="p-1 hover:bg-gray-200 rounded transition-colors"
                    >
                      <MoreVertical className="w-4 h-4 text-gray-600" />
                    </button>

                    {/* Выпадающее меню действий */}
                    {showActionMenu === user.id && (
                      <>
                        <div
                          className="fixed inset-0 z-10"
                          onClick={() => setShowActionMenu(null)}
                        />
                        <div className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-20">
                          <div className="py-1">
                            <button
                              onClick={() => openEditModal(user)}
                              className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                            >
                              <Edit className="w-4 h-4" />
                              Редактировать
                            </button>
                            <button
                              onClick={() => handleDeleteUser(user.id)}
                              className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                            >
                              <Trash2 className="w-4 h-4" />
                              Удалить
                            </button>
                          </div>
                        </div>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredUsers.length === 0 && (
          <div className="text-center py-12">
            <Search className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">Пользователи не найдены</p>
          </div>
        )}
      </div>

      {/* Модальное окно создания пользователя */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Добавить пользователя</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="p-1 hover:bg-gray-100 rounded transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Никнейм *
                </label>
                <input
                  type="text"
                  name="nickname"
                  value={newUser.nickname}
                  onChange={(e) => setNewUser({ ...newUser, nickname: e.target.value })}
                  className="input-field"
                  placeholder="username"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Имя *
                </label>
                <input
                  type="text"
                  name="name"
                  value={newUser.name}
                  onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                  className="input-field"
                  placeholder="Иван"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Фамилия *
                </label>
                <input
                  type="text"
                  name="surname"
                  value={newUser.surname}
                  onChange={(e) => setNewUser({ ...newUser, surname: e.target.value })}
                  className="input-field"
                  placeholder="Иванов"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email *
                </label>
                <input
                  type="email"
                  name="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                  className="input-field"
                  placeholder="email@example.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Пароль *
                </label>
                <input
                  type="password"
                  name="password"
                  value={newUser.password}
                  onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                  className="input-field"
                  placeholder="Минимум 6 символов"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Уровень доступа
                </label>
                <select
                  value={newUser.level}
                  onChange={(e) => setNewUser({ ...newUser, level: e.target.value })}
                  className="input-field"
                >
                  {levelOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Статус
                </label>
                <select
                  value={newUser.status}
                  onChange={(e) => setNewUser({ ...newUser, status: e.target.value })}
                  className="input-field"
                >
                  <option value="active">Активен</option>
                  <option value="inactive">Неактивен</option>
                </select>
              </div>
            </div>
            <div className="flex gap-2 mt-6">
              <button
                onClick={handleCreateUser}
                disabled={formLoading || !newUser.nickname || !newUser.name || !newUser.surname || !newUser.email || !newUser.password}
                className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {formLoading ? 'Создание...' : 'Создать'}
              </button>
              <button
                onClick={() => setShowCreateModal(false)}
                disabled={formLoading}
                className="flex-1 btn-secondary"
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Модальное окно редактирования пользователя */}
      {showEditModal && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">
                Редактирование пользователя #{selectedUser.id}
              </h3>
              <button
                onClick={() => setShowEditModal(false)}
                className="p-1 hover:bg-gray-100 rounded transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Никнейм *
                </label>
                <input
                  type="text"
                  value={editUser.nickname}
                  onChange={(e) => setEditUser({ ...editUser, nickname: e.target.value })}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Имя *
                </label>
                <input
                  type="text"
                  value={editUser.name}
                  onChange={(e) => setEditUser({ ...editUser, name: e.target.value })}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Фамилия *
                </label>
                <input
                  type="text"
                  value={editUser.surname}
                  onChange={(e) => setEditUser({ ...editUser, surname: e.target.value })}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email *
                </label>
                <input
                  type="email"
                  value={editUser.email}
                  onChange={(e) => setEditUser({ ...editUser, email: e.target.value })}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Уровень доступа
                </label>
                <select
                  value={editUser.level}
                  onChange={(e) => setEditUser({ ...editUser, level: e.target.value })}
                  className="input-field"
                >
                  {levelOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Статус
                </label>
                <select
                  value={editUser.status}
                  onChange={(e) => setEditUser({ ...editUser, status: e.target.value })}
                  className="input-field"
                >
                  <option value="active">Активен</option>
                  <option value="inactive">Неактивен</option>
                </select>
              </div>
            </div>
            <div className="flex gap-2 mt-6">
              <button
                onClick={handleEditUser}
                disabled={formLoading || !editUser.nickname || !editUser.name || !editUser.surname || !editUser.email}
                className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {formLoading ? 'Сохранение...' : 'Сохранить'}
              </button>
              <button
                onClick={() => setShowEditModal(false)}
                disabled={formLoading}
                className="flex-1 btn-secondary"
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
