import { useState, useEffect } from 'react'
import { Search, Plus, Filter, Trash2, CheckCircle, X } from 'lucide-react'
import { ordersApi, menuItemsApi } from '../lib/api'

interface MenuItem {
  id: number
  name: string
  description: string
  price: number
  category: string
  is_available: boolean
}

interface OrderItem {
  id?: number
  menu_item_id: number
  quantity: number
  price?: number
  note?: string
  menu_item?: MenuItem
}

interface Order {
  id: number
  table_number: number
  items: OrderItem[]
  total_price: number
  status: 'pending' | 'ready' | 'paid'
  created_at: string
}

const statusColors = {
  pending: 'bg-yellow-100 text-yellow-800',
  ready: 'bg-green-100 text-green-800',
  paid: 'bg-blue-100 text-blue-800',
}

const statusLabels = {
  pending: 'В ожидании',
  ready: 'Готово',
  paid: 'Оплачено',
}

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [menuItems, setMenuItems] = useState<MenuItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [showStatusModal, setShowStatusModal] = useState(false)
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [newOrder, setNewOrder] = useState({
    table_number: 1,
    items: [{ menu_item_id: 0, quantity: 1 }] as { menu_item_id: number, quantity: number }[]
  })
  const [editOrder, setEditOrder] = useState({
    table_number: 1,
    items: [] as OrderItem[]
  })

  const fetchMenuItems = async () => {
    try {
      console.log('[OrdersPage] Fetching menu items...')
      const data = await menuItemsApi.getAll({ is_available: true }).catch(() => [])
      console.log('[OrdersPage] Menu items loaded:', data)
      setMenuItems(data)
    } catch (err: any) {
      console.error('[OrdersPage] Error fetching menu items:', err)
      console.error('[OrdersPage] Error details:', err.response?.data)
    }
  }

  const fetchOrders = async () => {
    try {
      console.log('[OrdersPage] Fetching orders...')
      setLoading(true)
      const data = await ordersApi.getAll().catch((err) => {
        console.error('[OrdersPage] API error:', err)
        throw err // Пробрасываем ошибку дальше для обработки
      })
      console.log('[OrdersPage] Orders loaded:', data)
      setOrders(data)
      setError(null)
    } catch (err: any) {
      console.error('[OrdersPage] Error fetching orders:', err)
      console.error('[OrdersPage] Error response:', err.response)
      console.error('[OrdersPage] Error data:', err.response?.data)
      
      // Определяем тип ошибки
      let errorMessage = 'Ошибка загрузки заказов'
      if (err.response?.status === 401) {
        errorMessage = 'Требуется авторизация. Пожалуйста, войдите в систему.'
      } else if (err.response?.status === 403) {
        errorMessage = 'Недостаточно прав для просмотра заказов'
      } else if (err.code === 'ERR_NETWORK') {
        errorMessage = 'Ошибка сети. Проверьте подключение к серверу.'
      } else if (err.message) {
        errorMessage = err.message
      }
      
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMenuItems()
    fetchOrders()
  }, [])

  const handleCreateOrder = async () => {
    try {
      // Преобразуем данные для API
      const orderData = {
        table_number: newOrder.table_number,
        items: newOrder.items
          .filter(item => item.menu_item_id > 0)
          .map(item => ({
            menu_item_id: item.menu_item_id,
            quantity: item.quantity
          }))
      }
      
      if (orderData.items.length === 0) {
        alert('Добавьте хотя бы одно блюдо')
        return
      }
      
      await ordersApi.create(orderData)
      await fetchOrders()
      setShowCreateModal(false)
      setNewOrder({ table_number: 1, items: [{ menu_item_id: 0, quantity: 1 }] })
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка создания заказа')
    }
  }

  const openEditModal = (order: Order) => {
    setSelectedOrder(order)
    setEditOrder({
      table_number: order.table_number,
      items: order.items.map(item => ({ ...item }))
    })
    setShowEditModal(true)
  }

  const handleEditOrder = async () => {
    if (!selectedOrder) return
    try {
      const orderData = {
        table_number: editOrder.table_number,
        items: editOrder.items
          .filter(item => item.menu_item_id > 0)
          .map(item => ({
            menu_item_id: item.menu_item_id,
            quantity: item.quantity
          }))
      }
      
      if (orderData.items.length === 0) {
        alert('Добавьте хотя бы одно блюдо')
        return
      }
      
      await ordersApi.update(selectedOrder.id, orderData)
      await fetchOrders()
      setShowEditModal(false)
      setSelectedOrder(null)
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка обновления заказа')
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Удалить этот заказ?')) return
    try {
      await ordersApi.delete(id)
      setOrders(orders.filter(o => o.id !== id))
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка удаления')
    }
  }

  const handleStatusChange = async (status: string) => {
    if (!selectedOrder) return
    try {
      await ordersApi.updateStatus(selectedOrder.id, status)
      await fetchOrders()
      setShowStatusModal(false)
      setSelectedOrder(null)
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка обновления статуса')
    }
  }

  const filteredOrders = orders.filter(order => {
    const matchesSearch = search === '' || 
      order.table_number.toString().includes(search) ||
      order.id.toString().includes(search)
    const matchesStatus = statusFilter === 'all' || order.status === statusFilter
    return matchesSearch && matchesStatus
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Загрузка заказов...</div>
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
          <h2 className="text-3xl font-bold text-gray-900">Заказы</h2>
          <p className="text-gray-600 mt-1">Управление заказами кафе</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Новый заказ
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
              placeholder="Поиск по номеру стола или ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              className="input-field"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">Все статусы</option>
              <option value="pending">В ожидании</option>
              <option value="ready">Готово</option>
              <option value="paid">Оплачено</option>
            </select>
          </div>
        </div>
      </div>

      {/* Таблица заказов */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">ID</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Стол</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Блюда</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Сумма</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Статус</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Действия</th>
              </tr>
            </thead>
            <tbody>
              {filteredOrders.map((order) => (
                <tr key={order.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 text-sm font-medium text-gray-900">#{order.id}</td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center justify-center w-8 h-8 bg-primary-100 text-primary-700 rounded-lg text-sm font-medium">
                      {order.table_number}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="text-sm text-gray-900">
                      {order.items.map((item, idx) => (
                        <div key={idx}>{item.quantity}x {item.menu_item?.name || 'Блюдо'}</div>
                      ))}
                    </div>
                  </td>
                  <td className="py-3 px-4 text-sm font-semibold text-gray-900">{order.total_price} ₽</td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[order.status]}`}>
                      {statusLabels[order.status]}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => openEditModal(order)}
                        className="p-1 hover:bg-blue-100 rounded transition-colors"
                        title="Редактировать заказ"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4 text-blue-600"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>
                      </button>
                      <button
                        onClick={() => { setSelectedOrder(order); setShowStatusModal(true) }}
                        className="p-1 hover:bg-gray-200 rounded transition-colors"
                        title="Изменить статус"
                      >
                        <CheckCircle className="w-4 h-4 text-gray-600" />
                      </button>
                      <button
                        onClick={() => handleDelete(order.id)}
                        className="p-1 hover:bg-red-100 rounded transition-colors"
                        title="Удалить"
                      >
                        <Trash2 className="w-4 h-4 text-red-600" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredOrders.length === 0 && (
          <div className="text-center py-12">
            <Search className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">Заказы не найдены</p>
          </div>
        )}
      </div>

      {/* Модальное окно изменения статуса */}
      {showStatusModal && selectedOrder && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Изменить статус заказа #{selectedOrder.id}</h3>
            <div className="space-y-2">
              {(['pending', 'ready', 'paid'] as const).map((status) => (
                <button
                  key={status}
                  onClick={() => handleStatusChange(status)}
                  className={`w-full p-3 rounded-lg text-left font-medium ${
                    selectedOrder.status === status
                      ? 'bg-primary-100 text-primary-700'
                      : 'bg-gray-100 hover:bg-gray-200'
                  }`}
                >
                  {statusLabels[status]}
                </button>
              ))}
            </div>
            <button
              onClick={() => { setShowStatusModal(false); setSelectedOrder(null) }}
              className="mt-4 w-full btn-secondary"
            >
              Отмена
            </button>
          </div>
        </div>
      )}

      {/* Модальное окно создания заказа */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Создать новый заказ</h3>
              <button
                onClick={() => { setShowCreateModal(false); setNewOrder({ table_number: 1, items: [{ menu_item_id: 0, quantity: 1 }] }) }}
                className="p-1 hover:bg-gray-100 rounded transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Номер стола
                </label>
                <input
                  type="number"
                  value={newOrder.table_number}
                  onChange={(e) => setNewOrder({ ...newOrder, table_number: parseInt(e.target.value) || 1 })}
                  className="input-field"
                  min="1"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Блюда из меню
                </label>
                {newOrder.items.map((item, idx) => (
                  <div key={idx} className="flex gap-2 mb-2">
                    <select
                      value={item.menu_item_id}
                      onChange={(e) => {
                        const newItems = [...newOrder.items]
                        newItems[idx] = { 
                          menu_item_id: parseInt(e.target.value),
                          quantity: item.quantity
                        }
                        setNewOrder({ ...newOrder, items: newItems })
                      }}
                      className="input-field flex-1"
                    >
                      <option value={0}>Выберите блюдо...</option>
                      {menuItems.map(mi => (
                        <option key={mi.id} value={mi.id}>
                          {mi.name} — {mi.price}₽
                        </option>
                      ))}
                    </select>
                    <input
                      type="number"
                      placeholder="Кол-во"
                      value={item.quantity}
                      onChange={(e) => {
                        const newItems = [...newOrder.items]
                        newItems[idx] = { ...item, quantity: parseInt(e.target.value) || 1 }
                        setNewOrder({ ...newOrder, items: newItems })
                      }}
                      className="input-field w-20"
                      min="1"
                    />
                    <button
                      onClick={() => {
                        const newItems = newOrder.items.filter((_, i) => i !== idx)
                        setNewOrder({ ...newOrder, items: newItems.length ? newItems : [{ menu_item_id: 0, quantity: 1 }] })
                      }}
                      className="p-2 hover:bg-red-100 rounded transition-colors"
                    >
                      <Trash2 className="w-4 h-4 text-red-600" />
                    </button>
                  </div>
                ))}
                <button
                  onClick={() => {
                    setNewOrder({ ...newOrder, items: [...newOrder.items, { menu_item_id: 0, quantity: 1 }] })
                  }}
                  className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  + Добавить блюдо
                </button>
              </div>
            </div>
            <div className="flex gap-2 mt-6">
              <button
                onClick={handleCreateOrder}
                className="flex-1 btn-primary"
              >
                Создать заказ
              </button>
              <button
                onClick={() => { setShowCreateModal(false); setNewOrder({ table_number: 1, items: [{ menu_item_id: 0, quantity: 1 }] }) }}
                className="flex-1 btn-secondary"
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Модальное окно редактирования заказа */}
      {showEditModal && selectedOrder && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Редактировать заказ #{selectedOrder.id}</h3>
              <button
                onClick={() => { setShowEditModal(false); setSelectedOrder(null) }}
                className="p-1 hover:bg-gray-100 rounded transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Номер стола
                </label>
                <input
                  type="number"
                  value={editOrder.table_number}
                  onChange={(e) => setEditOrder({ ...editOrder, table_number: parseInt(e.target.value) || 1 })}
                  className="input-field"
                  min="1"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Блюда из меню
                </label>
                {editOrder.items.map((item, idx) => (
                  <div key={idx} className="flex gap-2 mb-2">
                    <select
                      value={item.menu_item_id}
                      onChange={(e) => {
                        const newItems = [...editOrder.items]
                        newItems[idx] = { 
                          ...item,
                          menu_item_id: parseInt(e.target.value)
                        }
                        setEditOrder({ ...editOrder, items: newItems })
                      }}
                      className="input-field flex-1"
                    >
                      <option value={0}>Выберите блюдо...</option>
                      {menuItems.map(mi => (
                        <option key={mi.id} value={mi.id}>
                          {mi.name} — {mi.price}₽
                        </option>
                      ))}
                    </select>
                    <input
                      type="number"
                      placeholder="Кол-во"
                      value={item.quantity}
                      onChange={(e) => {
                        const newItems = [...editOrder.items]
                        newItems[idx] = { ...item, quantity: parseInt(e.target.value) || 1 }
                        setEditOrder({ ...editOrder, items: newItems })
                      }}
                      className="input-field w-20"
                      min="1"
                    />
                    <button
                      onClick={() => {
                        const newItems = editOrder.items.filter((_, i) => i !== idx)
                        setEditOrder({ ...editOrder, items: newItems.length ? newItems : [{ menu_item_id: 0, quantity: 1, price: 0 }] })
                      }}
                      className="p-2 hover:bg-red-100 rounded transition-colors"
                    >
                      <Trash2 className="w-4 h-4 text-red-600" />
                    </button>
                  </div>
                ))}
                <button
                  onClick={() => {
                    setEditOrder({ ...editOrder, items: [...editOrder.items, { menu_item_id: 0, quantity: 1, price: 0 }] })
                  }}
                  className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  + Добавить блюдо
                </button>
              </div>
            </div>
            <div className="flex gap-2 mt-6">
              <button
                onClick={handleEditOrder}
                className="flex-1 btn-primary"
              >
                Сохранить изменения
              </button>
              <button
                onClick={() => { setShowEditModal(false); setSelectedOrder(null) }}
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
