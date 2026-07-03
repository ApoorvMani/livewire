import { useNavigate, useLocation } from 'react-router-dom'

const tabs = [
  { path: '/', label: 'Home', icon: '🏠' },
  { path: '/crimes', label: 'Crimes', icon: '💀' },
  { path: '/fight', label: 'Fight', icon: '⚔️', disabled: true },
  { path: '/market', label: 'Market', icon: '💰', disabled: true },
  { path: '/city', label: 'City', icon: '🏙️' },
]

export default function BottomNav() {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-gray-900 border-t border-gray-800">
      <div className="max-w-md mx-auto flex justify-around">
        {tabs.map(t => (
          <button
            key={t.path}
            disabled={t.disabled}
            className={`flex flex-col items-center py-2 px-3 text-xs ${location.pathname === t.path ? 'text-blue-400' : 'text-gray-500'} ${t.disabled ? 'opacity-40' : ''}`}
            onClick={() => navigate(t.path)}
          >
            <span className="text-lg">{t.icon}</span>
            <span>{t.label}</span>
          </button>
        ))}
      </div>
    </nav>
  )
}
