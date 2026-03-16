import { useState, useEffect } from 'react'
import { DollarSign, TrendingUp, Calendar, Download } from 'lucide-react'
import { ordersApi } from '../lib/api'

interface Revenue {
  total_revenue: number
  orders_count: number
}

export default function RevenuePage() {
  const [revenue, setRevenue] = useState<Revenue | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [period, setPeriod] = useState('today')

  useEffect(() => {
    const fetchRevenue = async () => {
      try {
        setLoading(true)
        const data = await ordersApi.getRevenue()
        setRevenue(data)
        setError(null)
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Ошибка загрузки выручки')
      } finally {
        setLoading(false)
      }
    }
    fetchRevenue()
  }, [])

  if (loading) {
    return <div className="text-gray-500">Загрузка...</div>
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-500">Ошибка: {error}</div>
      </div>
    )
  }

  const totalRevenue = revenue?.total_revenue || 0
  const totalOrders = revenue?.orders_count || 0
  const avgCheck = totalOrders > 0 ? totalRevenue / totalOrders : 0

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Выручка за смену</h2>
          <p className="text-gray-600 mt-1">Финансовая статистика и аналитика</p>
        </div>
        <button className="btn-secondary flex items-center gap-2">
          <Download className="w-5 h-5" />
          Экспорт
        </button>
      </div>

      {/* Выбор периода */}
      <div className="card mb-6">
        <div className="flex items-center gap-2">
          <Calendar className="w-5 h-5 text-gray-400" />
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setPeriod('today')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                period === 'today'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Сегодня
            </button>
            <button
              onClick={() => setPeriod('week')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                period === 'week'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Неделя
            </button>
            <button
              onClick={() => setPeriod('month')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                period === 'month'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Месяц
            </button>
          </div>
        </div>
      </div>

      {/* Карточки статистики */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Общая выручка</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{totalRevenue.toLocaleString('ru-RU')} ₽</p>
              <p className="text-sm text-green-600 mt-2 flex items-center gap-1">
                <TrendingUp className="w-4 h-4" />
                За все время
              </p>
            </div>
            <div className="bg-green-500 p-4 rounded-xl">
              <DollarSign className="w-8 h-8 text-white" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Всего оплачено заказов</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{totalOrders}</p>
              <p className="text-sm text-gray-500 mt-2">Оплаченных заказов</p>
            </div>
            <div className="bg-blue-500 p-4 rounded-xl">
              <Calendar className="w-8 h-8 text-white" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Средний чек</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{Math.round(avgCheck).toLocaleString('ru-RU')} ₽</p>
              <p className="text-sm text-gray-500 mt-2">На один заказ</p>
            </div>
            <div className="bg-purple-500 p-4 rounded-xl">
              <TrendingUp className="w-8 h-8 text-white" />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
