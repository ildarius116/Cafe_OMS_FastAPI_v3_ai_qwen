import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Отключаем StrictMode для стабильности в production и тестах
// В development можно включить обратно для проверки
const enableStrictMode = false

ReactDOM.createRoot(document.getElementById('root')!).render(
  enableStrictMode ? (
    <React.StrictMode>
      <App />
    </React.StrictMode>
  ) : (
    <App />
  )
)
