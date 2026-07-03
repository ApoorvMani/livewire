import { Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Login from './pages/Login'
import Home from './pages/Home'
import Crimes from './pages/Crimes'
import Gym from './pages/Gym'
import BottomNav from './components/BottomNav'
import { api } from './api'

export default function App() {
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.me().then(setUser).catch(() => setUser(null)).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex items-center justify-center h-screen"><p>Loading...</p></div>
  if (!user) return <Login onLogin={() => api.me().then(setUser)} />

  return (
    <div className="max-w-md mx-auto min-h-screen flex flex-col">
      <main className="flex-1 p-4 pb-20 overflow-y-auto">
        <Routes>
          <Route path="/" element={<Home user={user} />} />
          <Route path="/crimes" element={<Crimes />} />
          <Route path="/gym" element={<Gym />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
      <BottomNav />
    </div>
  )
}
