import { useState, useEffect } from 'react'
import { ShoppingCart, DollarSign, Clock, TrendingUp } from 'lucide-react'
import { ordersApi } from '../lib/api'

interface Order {
  id: number
  table_number: number
  items: { name: string; price: number; quantity: number }[]
  total_price: number
  status: string
  created_at: string
}

interface Revenue {
  total_revenue: number
  orders_count: number
}

const statsConfig = [
  { name: 'Активные заказы', icon: ShoppingCart, color: 'bg-blue-500', stat: 'active' },
  { name: 'Выручка за смену', icon: DollarSign, color: 'bg-green-500', stat: 'revenue' },
  { name: 'В ожидании', icon: Clock, color: 'bg-yellow-500', stat: 'pending' },
  { name: 'Всего заказов', icon: TrendingUp, color: 'bg-purple-500', stat: 'total' },
]

const statusLabels = {
  pending: 'В ожидании',
  ready: 'Готово',
  paid: 'Оплачено',
}

// Проверка что дата относится к текущему дню
const isToday = (dateString: string) => {
  const date = new Date(dateString)
  const today = new Date()
  return date.getFullYear() === today.getFullYear() &&
         date.getMonth() === today.getMonth() &&
         date.getDate() === today.getDate()
}

export default function Dashboard() {
  const [orders, setOrders] = useState<Order[]>([])
  const [_revenue, setRevenue] = useState<Revenue | null>(null)
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({ active: 0, revenue: 0, pending: 0, total: 0 })

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [ordersData, revenueData] = await Promise.all([
          ordersApi.getAll().catch(() => []),
          ordersApi.getRevenue().catch(() => null),
        ])
        
        // Фильтруем заказы только за текущий день
        const todayOrders = ordersData.filter((o: Order) => isToday(o.created_at))
        
        setOrders(todayOrders)
        setRevenue(revenueData)

        // Вычисляем статистику только за текущий день
        const active = todayOrders.filter((o: Order) => o.status === 'pending' || o.status === 'ready').length
        const pending = todayOrders.filter((o: Order) => o.status === 'pending').length
        const totalRevenue = revenueData?.total_revenue || todayOrders.filter((o: Order) => o.status === 'paid').reduce((sum: number, o: Order) => sum + o.total_price, 0)

        setStats({
          active,
          revenue: totalRevenue,
          pending,
          total: todayOrders.length,
        })
      } catch (err) {
        console.error('Error fetching dashboard data:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) {
    return <div className="text-gray-500">Загрузка...</div>
  }

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Дашборд</h2>
        <p className="text-gray-600 mt-1">Статистика заказов за текущий день</p>
      </div>

      {/* Карточки статистики */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statsConfig.map((item) => (
          <div key={item.name} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{item.name}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {item.stat === 'revenue' 
                    ? `${stats[item.stat as keyof typeof stats].toLocaleString('ru-RU')} ₽`
                    : stats[item.stat as keyof typeof stats]
                  }
                </p>
              </div>
              <div className={`${item.color} p-3 rounded-lg`}>
                <item.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Все заказы за сегодня */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-gray-900">Все заказы за сегодня</h3>
          <a href="/orders" className="text-sm text-primary-600 hover:text-primary-700 font-medium">
            Перейти к заказам →
          </a>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">ID</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Стол</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Блюда</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Сумма</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Статус</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr key={order.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 text-sm text-gray-900">#{order.id}</td>
                  <td className="py-3 px-4 text-sm text-gray-900">Стол {order.table_number}</td>
                  <td className="py-3 px-4 text-sm text-gray-600">
                    {order.items.map((item, idx) => (
                      <span key={idx}>{item.quantity}x {item.name}{idx < order.items.length - 1 ? ', ' : ''}</span>
                    ))}
                  </td>
                  <td className="py-3 px-4 text-sm font-medium text-gray-900">{order.total_price} ₽</td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      order.status === 'ready' ? 'bg-green-100 text-green-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {statusLabels[order.status as keyof typeof statusLabels]}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {orders.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">Заказов пока нет</p>
          </div>
        )}
      </div>
    </div>
  )
}
