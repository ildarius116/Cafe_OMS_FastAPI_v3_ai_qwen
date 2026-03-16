import { BrowserRouter, Routes, Route } from 'react-router-dom'

// Layout components
import { Sidebar } from './components/layout/Sidebar'
import { Header } from './components/layout/Header'

// Pages
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import OrdersPage from './pages/OrdersPage'
import UsersPage from './pages/UsersPage'
import ProfilePage from './pages/ProfilePage'
import RevenuePage from './pages/RevenuePage'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <div className="flex">
          <Sidebar />
          <div className="flex-1 ml-64">
            <Header />
            <main className="p-8">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<LoginPage />} />
                <Route path="/orders" element={<OrdersPage />} />
                <Route path="/users" element={<UsersPage />} />
                <Route path="/profile" element={<ProfilePage />} />
                <Route path="/revenue" element={<RevenuePage />} />
              </Routes>
            </main>
          </div>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
