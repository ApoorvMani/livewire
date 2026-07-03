import Bars from '../components/Bars'
import { useNavigate } from 'react-router-dom'

interface Props { user: any }

export default function Home({ user }: Props) {
  const navigate = useNavigate()

  return (
    <div className="flex flex-col gap-4">
      <div className="bg-gray-800 rounded-lg p-4">
        <h2 className="text-xl font-bold mb-1">{user.name}</h2>
        <p className="text-sm text-gray-400">Level {user.level} · ${user.cash}</p>
      </div>
      <div className="bg-gray-800 rounded-lg p-4">
        <Bars
          energy={user.energy} maxEnergy={user.max_energy}
          nerve={user.nerve} maxNerve={user.max_nerve}
          health={user.health} maxHealth={user.max_health}
        />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <button className="bg-gray-800 p-4 rounded-lg text-left" onClick={() => navigate('/crimes')}>
          <div className="text-2xl mb-1">💀</div>
          <div className="font-semibold">Crimes</div>
          <div className="text-xs text-gray-400">Spend nerve for cash</div>
        </button>
        <button className="bg-gray-800 p-4 rounded-lg text-left" onClick={() => navigate('/gym')}>
          <div className="text-2xl mb-1">🏋️</div>
          <div className="font-semibold">Gym</div>
          <div className="text-xs text-gray-400">Train your stats</div>
        </button>
      </div>
    </div>
  )
}
