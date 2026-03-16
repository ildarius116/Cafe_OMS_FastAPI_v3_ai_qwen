import { NavLink } from 'react-router-dom'
import { LayoutDashboard, ShoppingCart, Users, User, BarChart3 } from 'lucide-react'

const navigation = [
  { name: 'Дашборд', href: '/', icon: LayoutDashboard },
  { name: 'Заказы', href: '/orders', icon: ShoppingCart },
  { name: 'Пользователи', href: '/users', icon: Users },
  { name: 'Выручка', href: '/revenue', icon: BarChart3 },
  { name: 'Профиль', href: '/profile', icon: User },
]

export function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 w-64 bg-white border-r border-gray-200">
      <div className="flex items-center h-16 px-6 border-b border-gray-200">
        <span className="text-xl font-bold text-gray-900">Cafe Orders</span>
      </div>
      <nav className="p-4 space-y-1">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-100'
              }`
            }
          >
            <item.icon className="w-5 h-5" />
            <span className="font-medium">{item.name}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
